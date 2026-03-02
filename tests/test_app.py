import copy
import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the original activities dict before each test."""
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = original


@pytest.fixture

def client():
    return TestClient(app_module.app)


def test_root_redirects(client):
    # disable automatic following of redirects for proper status code check
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_data(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    # sample structure
    chess = data["Chess Club"]
    assert "description" in chess
    assert isinstance(chess["participants"], list)


def test_successful_signup(client):
    email = "new@student.edu"
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert response.status_code == 200
    assert email in app_module.activities["Chess Club"]["participants"]


def test_signup_nonexistent_activity(client):
    response = client.post("/activities/NotReal/signup", params={"email": "a@example.com"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_duplicate_signup_returns_error(client):
    existing = app_module.activities["Chess Club"]["participants"][0]
    response = client.post("/activities/Chess%20Club/signup", params={"email": existing})
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]
