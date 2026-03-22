from fastapi.testclient import TestClient

from app.main import app


def test_app_title():
    assert app.title == "TaskFlow API"


def test_app_version():
    assert app.version == "0.1.0"


def test_openapi_url():
    assert app.openapi_url == "/api/openapi.json"


def test_docs_url():
    assert app.docs_url == "/api/docs"


def test_cors_middleware_configured():
    middleware_classes = [m.cls.__name__ for m in app.user_middleware]
    assert "CORSMiddleware" in middleware_classes


def test_openapi_schema():
    client = TestClient(app)
    response = client.get("/api/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "TaskFlow API"
    assert "/api/health" in schema["paths"]
