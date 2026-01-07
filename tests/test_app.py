from urllib.parse import quote
import sys
import os

# allow importing from src
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


def test_get_activities_contains_known_activity():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"].get("participants"), list)


def test_signup_and_unregister_flow():
    activity = "Art Club"
    email = "alice@example.com"

    # Clean up if already present
    activities = client.get("/activities").json()
    if email in activities.get(activity, {}).get("participants", []):
        client.delete(f"/activities/{quote(activity)}/participants?email={quote(email)}")

    # Sign up
    signup = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert signup.status_code == 200
    assert "Signed up" in signup.json().get("message", "")

    # Verify participant appears
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]

    # Unregister
    unregister = client.delete(f"/activities/{quote(activity)}/participants?email={quote(email)}")
    assert unregister.status_code == 200
    assert "Unregistered" in unregister.json().get("message", "")

    # Verify removed
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]


def test_unregister_nonexistent_returns_400():
    activity = "Debate Team"
    email = "nonexistent@example.com"
    # Ensure not registered
    client.delete(f"/activities/{quote(activity)}/participants?email={quote(email)}")

    resp = client.delete(f"/activities/{quote(activity)}/participants?email={quote(email)}")
    assert resp.status_code == 400
