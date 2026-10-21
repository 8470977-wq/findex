from fastapi.testclient import TestClient
from findex.web.app import app, get_index

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_root():
    response = client.get("/")
    assert response.status_code == 200

def test_get_index():
    assert get_index() == "index.bin"
