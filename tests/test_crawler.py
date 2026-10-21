import pytest
import httpx
from findex.crawler import async_crawl, canonicalize_url

def test_canonicalize_url():
    assert canonicalize_url("HTTP://Example.COM/foo/bar/") == "http://example.com/foo/bar"
    assert canonicalize_url("http://example.com/?b=1&a=2#section") == "http://example.com/?a=2&b=1"

@pytest.mark.asyncio
async def test_crawler_mock():
    async def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if "robots.txt" in url:
            return httpx.Response(200, text="User-agent: *\nDisallow: /private")
        elif url == "http://test.com/":
            return httpx.Response(200, text='<html><body><a href="/page1">P1</a></body></html>')
        elif url == "http://test.com/page1":
            return httpx.Response(200, text='<html><body><a href="/private">Private</a>Page 1 content</body></html>')
        elif url == "http://test.com/private":
            return httpx.Response(200, text='Secret')
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    docs = []
    async for doc in async_crawl("http://test.com/", max_pages=10, custom_transport=transport):
        docs.append(doc)

    urls = [d["url"] for d in docs]
    assert "http://test.com" in urls or "http://test.com/" in urls
    assert "http://test.com/page1" in urls
    assert "http://test.com/private" not in urls  # Заблоковано robots.txt
