import sys
from pathlib import Path
sys.path.insert(0, str(Path("src").resolve()))

from findex.corpus import tokenize

def test_tokenize_basic():
    text = "Hello, World! Python3 IS cool."
    assert list(tokenize(text)) == ["hello", "world", "python3", "is", "cool"]

def test_tokenize_unicode():
    text = "Сім'я, об'єм та state-of-the-art"
    tokens = list(tokenize(text))
    assert "сім'я" in tokens
    assert "state-of-the-art" in tokens
