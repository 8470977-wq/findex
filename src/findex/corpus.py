import re
import unicodedata
from pathlib import Path
from typing import Iterator, Tuple

TOKEN_RE = re.compile(r"\b\w+(?:['’-]\w+)*\b", re.UNICODE)

def iter_documents(data_dir: str | Path) -> Iterator[Tuple[Path, str]]:
    path = Path(data_dir)
    for file_path in path.rglob("*.txt"):
        if file_path.is_file():
            try:
                content = file_path.read_text(encoding="utf-8")
                yield file_path, content
            except UnicodeDecodeError:
                continue

def tokenize(text: str) -> Iterator[str]:
    normalized_text = unicodedata.normalize("NFC", text).lower()
    for match in TOKEN_RE.finditer(normalized_text):
        token = match.group()
        if token.strip("'-"):
            yield token
