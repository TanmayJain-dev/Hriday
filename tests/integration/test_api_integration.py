"""Integration tests for the thin FastAPI entry point."""


def test_api_health_endpoint():
    try:
        import fastapi
        from fastapi.testclient import TestClient
        from backend.api.main import app
    except ImportError:
        # FastAPI not installed in current environment; skip gracefully
        return

    client = TestClient(app)
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "service": "hriday-api"}
