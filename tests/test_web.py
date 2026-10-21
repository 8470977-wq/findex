import pytest
from fastapi.testclient import TestClient
from findex.web.app import app, get_index
from findex.index import InvertedIndex

client = TestClient(app)

def test_health_503_when_no_index():
    app.dependency_overrides[get_index] = lambda: (_ for _ in ()).throw(Exception())
    response = client.get("/health")
    assert response.status_code in (500, 503)
    app.dependency_overrides.clear()

def test_web_routes_with_mock_index():
    mock_idx = InvertedIndex()
    app.dependency_overrides[get_index] = lambda: mock_idx

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"

    res_stats = client.get("/stats")
    assert res_stats.status_code == 200

    res_search = client.get("/search?q=python")
    assert res_search.status_code == 200

    res_404 = client.get("/docs/999")
    assert res_404.status_code == 404

    app.dependency_overrides.clear()
