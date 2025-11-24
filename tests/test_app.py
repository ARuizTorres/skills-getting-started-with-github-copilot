from fastapi.testclient import TestClient
import pytest

from src import app as app_module

client = TestClient(app_module.app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Basic sanity checks
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "testuser+ci@example.com"

    activities = app_module.activities

    # Ensure clean state: remove email if present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    json_body = resp.json()
    assert "Signed up" in json_body.get("message", "")
    assert email in activities[activity]["participants"]

    # Duplicate signup should fail with 400
    resp_dup = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp_dup.status_code == 400

    # Now remove the participant
    resp_del = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp_del.status_code == 200
    json_del = resp_del.json()
    assert "Removed" in json_del.get("message", "")
    assert email not in activities[activity]["participants"]


def test_unregister_nonexistent_participant():
    activity = "Chess Club"
    email = "nonexistent+ci@example.com"

    # Ensure email is not present
    activities = app_module.activities
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 404
    body = resp.json()
    assert body.get("detail") == "Participant not found in activity"
