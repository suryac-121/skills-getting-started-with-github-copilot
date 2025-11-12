from fastapi.testclient import TestClient
import pytest

from src.app import app, activities

client = TestClient(app)


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    # ensure known activity present
    assert "Chess Club" in data


@pytest.fixture(autouse=True)
def reset_activities():
    # reset activities to known state before each test
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        }
    })
    yield


def test_signup_and_unregister_flow():
    # signup a new participant
    res = client.post("/activities/Chess%20Club/signup?email=test@example.com")
    assert res.status_code == 200
    assert "Signed up test@example.com" in res.json().get("message", "")

    # verify participant is present
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert "test@example.com" in data["Chess Club"]["participants"]

    # unregister the participant
    res = client.delete("/activities/Chess%20Club/participants?email=test@example.com")
    assert res.status_code == 200
    assert "Unregistered test@example.com" in res.json().get("message", "")

    # verify participant removed
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert "test@example.com" not in data["Chess Club"]["participants"]


def test_signup_errors():
    # duplicate signup
    res = client.post("/activities/Chess%20Club/signup?email=michael@mergington.edu")
    assert res.status_code == 400

    # bad activity
    res = client.post("/activities/Unknown/signup?email=a@b.com")
    assert res.status_code == 404


def test_unregister_errors():
    # unregister not signed up
    res = client.delete("/activities/Chess%20Club/participants?email=nosuch@x.com")
    assert res.status_code == 400

    # unknown activity
    res = client.delete("/activities/Unknown/participants?email=a@b.com")
    assert res.status_code == 404
