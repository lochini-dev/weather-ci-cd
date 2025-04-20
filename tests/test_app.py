import os
import pytest
from src.app import get_weather, app

# --- Dummy HTTP Response for mocking ---
class DummyResponse:
    def __init__(self, code, json_data):
        self.status_code = code
        self._json = json_data
    def json(self):
        return self._json

# --- Unit tests for get_weather() ---
def test_get_weather_success(monkeypatch):
    # Simulate 200 OK with temp=22
    dummy = DummyResponse(200, {"main":{"temp":22,"humidity":55},"weather":[{"description":"clear sky"}]})
    monkeypatch.setattr("requests.get", lambda *a, **k: dummy)
    os.environ["API_KEY"] = "fake"
    result = get_weather("London")
    assert result["temperature"] == 22
    assert result["description"] == "clear sky"

def test_get_weather_fail(monkeypatch):
    # Simulate 404 Not Found
    dummy = DummyResponse(404, {})
    monkeypatch.setattr("requests.get", lambda *a, **k: dummy)
    os.environ["API_KEY"] = "fake"
    assert get_weather("NoCity") is None

# --- Integration test for the Flask route ---
@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()

def test_index_get(client):
    res = client.get("/")
    assert res.status_code == 200

def test_index_post_not_found(client, monkeypatch):
    # Simulate API returning nothing
    class Empty(DummyResponse): pass
    dummy = DummyResponse(404, {})
    monkeypatch.setattr("requests.get", lambda *a, **k: dummy)
    os.environ["API_KEY"] = "fake"
    res = client.post("/", data={"city":"Unknown"})
    assert res.status_code == 200
    assert b"City not found" in res.data or b"Unknown" in res.data
