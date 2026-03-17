from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

# Capture the initial state so tests can reset the in-memory database.
INITIAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activity store before each test."""
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant(client):
    email = "teststudent@mergington.edu"
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]

    data = client.get("/activities").json()
    assert email in data["Chess Club"]["participants"]


def test_signup_duplicate_returns_400(client):
    email = "dupstudent@mergington.edu"
    client.post(f"/activities/Chess%20Club/signup?email={email}")
    response = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_remove_participant(client):
    email = "michael@mergington.edu"
    response = client.delete(f"/activities/Chess%20Club/participants?email={email}")
    assert response.status_code == 200
    assert "Removed" in response.json()["message"]

    data = client.get("/activities").json()
    assert email not in data["Chess Club"]["participants"]


def test_remove_nonexistent_participant_returns_404(client):
    email = "nonexistent@mergington.edu"
    response = client.delete(f"/activities/Chess%20Club/participants?email={email}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
