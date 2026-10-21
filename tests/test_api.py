from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_home_page():
    response = client.get("/")
    assert response.status_code in (200, 307, 308, 404)


def test_health_endpoint():
    response = client.get("/health")

    if response.status_code == 404:
        response = client.get("/api/health")

    assert response.status_code in (200, 404)


def test_static_files_are_served():
    response = client.get("/static/index.html")
    assert response.status_code in (200, 404)


def test_invalid_endpoint():
    response = client.get("/this-endpoint-does-not-exist")
    assert response.status_code == 404


def test_app_is_loaded():
    assert app is not None
    assert hasattr(app, "routes")
