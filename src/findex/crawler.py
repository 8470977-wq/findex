import asyncio
import random
import time
import re
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode, urljoin
from typing import AsyncGenerator, Dict, Set, Optional, List, Any
from pathlib import Path
import json
import httpx
from html.parser import HTMLParser

class SimpleHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.text_parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr, val in attrs:
                if attr == "href" and val:
                    self.links.append(val)

    def handle_data(self, data):
        cleaned = data.strip()
        if cleaned:
            self.text_parts.append(cleaned)

def extract_links_and_text(html: str, base_url: str) -> tuple[List[str], str]:
    parser = SimpleHTMLParser()
    parser.feed(html)
    full_text = " ".join(parser.text_parts)
    
    resolved_links = []
    for link in parser.links:
        joined = urljoin(base_url, link)
        resolved_links.append(joined)
        
    return resolved_links, full_text

def canonicalize_url(url: str) -> str:
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path or "/"
    if len(path) > 1 and path.endswith("/"):
        path = path.rstrip("/")
        
    query_params = parse_qsl(parsed.query, keep_blank_values=True)
    sorted_query = urlencode(sorted(query_params))
    
    return urlunparse((scheme, netloc, path, parsed.params, sorted_query, ""))

class RobotsCache:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        self.disallowed: Dict[str, Set[str]] = {}

    async def is_allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        host = parsed.netloc
        if host not in self.disallowed:
            self.disallowed[host] = set()
            robots_url = f"{parsed.scheme}://{host}/robots.txt"
            try:
                resp = await self.client.get(robots_url, timeout=3.0)
                if resp.status_code == 200:
                    for line in resp.text.splitlines():
                        line = line.strip()
                        if line.lower().startswith("disallow:"):
                            parts = line.split(":", 1)
                            if len(parts) > 1 and parts[1].strip():
                                self.disallowed[host].add(parts[1].strip())
            except Exception:
                pass
        
        path = parsed.path or "/"
        for rule in self.disallowed[host]:
            if rule and path.startswith(rule):
                return False
        return True

async def fetch_with_retry(
    client: httpx.AsyncClient, 
    url: str, 
    max_retries: int = 3,
    log_file: Optional[Path] = None
) -> Optional[str]:
    retries = 0
    backoff = 0.5
    
    while retries <= max_retries:
        start_time = time.perf_counter()
        try:
            async with asyncio.timeout(5.0):
                resp = await client.get(url)
                elapsed = time.perf_counter() - start_time
                
                if log_file:
                    with open(log_file, "a", encoding="utf-8") as f:
                        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] GET {url} STATUS {resp.status_code} TIME {elapsed:.3f}s\n")

                if resp.status_code == 200:
                    return resp.text
                elif resp.status_code in (429, 500, 502, 503, 504):
                    retry_after = resp.headers.get("Retry-After")
                    if retry_after and retry_after.isdigit():
                        sleep_time = float(retry_after)
                    else:
                        sleep_time = backoff + random.uniform(0, 0.1)
                        backoff *= 2
                    retries += 1
                    await asyncio.sleep(sleep_time)
                else:
                    return None
        except (httpx.RequestError, asyncio.TimeoutError) as e:
            elapsed = time.perf_counter() - start_time
            if log_file:
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ERROR GET {url} REASON {type(e).__name__} TIME {elapsed:.3f}s\n")
            retries += 1
            await asyncio.sleep(backoff + random.uniform(0, 0.1))
            backoff *= 2
            
    return None

async def async_crawl(
    start_url: str,
    max_pages: int = 200,
    concurrency: int = 5,
    out_jsonl: Optional[Path] = None,
    log_file: Optional[Path] = None,
    custom_transport: Optional[httpx.AsyncBaseTransport] = None
) -> AsyncGenerator[Dict[str, Any], None]:
    
    headers = {"User-Agent": "findex-crawler/0.6.0 (+https://github.com/8470977-wq/findex)"}
    
    client_kwargs = {"headers": headers, "follow_redirects": True, "timeout": 5.0}
    if custom_transport:
        client_kwargs["transport"] = custom_transport

    async with httpx.AsyncClient(**client_kwargs) as client:
        robots_cache = RobotsCache(client)
        semaphore = asyncio.Semaphore(concurrency)
        
        queue: asyncio.Queue[str] = asyncio.Queue()
        seen: Set[str] = set()
        
        canon_start = canonicalize_url(start_url)
        await queue.put(canon_start)
        seen.add(canon_start)
        
        crawled_count = 0
        
        while not queue.empty() and crawled_count < max_pages:
            url = await queue.get()
            
            if not await robots_cache.is_allowed(url):
                queue.task_done()
                continue
                
            async with semaphore:
                html = await fetch_with_retry(client, url, log_file=log_file)
                
            if html:
                links, text = extract_links_and_text(html, url)
                crawled_count += 1
                
                doc = {
                    "url": url,
                    "title": url,
                    "content": text,
                    "doc_id": crawled_count
                }
                
                if out_jsonl:
                    with open(out_jsonl, "a", encoding="utf-8") as f:
                        f.write(json.dumps(doc, ensure_ascii=False) + "\n")
                        
                yield doc
                
                for link in links:
                    try:
                        canon = canonicalize_url(link)
                        if canon.startswith("http") and canon not in seen:
                            seen.add(canon)
                            await queue.put(canon)
                    except Exception:
                        pass
                        
            queue.task_done()
