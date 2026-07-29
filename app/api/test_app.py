from app import app


def test_health_endpoint():
    client = app.test_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "ok" #assert response.json["status"] == "healthy"
    assert response.json["service"] == "api"


def test_info_endpoint():
    client = app.test_client()
    response = client.get("/api/info")

    assert response.status_code == 200
    assert response.json["service"] == "api"
    assert "message" in response.json


def test_unknown_route_returns_json_404():
    client = app.test_client()
    response = client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.content_type.startswith("application/json")
    assert response.json["error"] == "not found"
