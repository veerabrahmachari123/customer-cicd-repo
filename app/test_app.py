from app import app

def test_environment(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "TEST")
    response = app.test_client().get("/environment")
    assert response.status_code == 200
    assert response.json["environment"] == "TEST"

def test_version(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "5.0")
    response = app.test_client().get("/version")
    assert response.status_code == 200
    assert response.json["version"] == "5.0"

def test_search_requires_name():
    response = app.test_client().get("/customers/search")
    assert response.status_code == 400
