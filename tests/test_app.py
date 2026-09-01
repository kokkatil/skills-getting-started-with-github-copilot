from urllib.parse import quote
from uuid import uuid4

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def test_duplicate_signup_is_rejected():
    activity_name = "Chess Club"
    email = f"duplicate-{uuid4()}@mergington.edu"
    activity = activities[activity_name]
    initial_count = len(activity["participants"])

    first_response = client.post(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": email},
    )
    assert first_response.status_code == 200

    second_response = client.post(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": email},
    )
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student is already signed up"
    assert len(activity["participants"]) == initial_count + 1


def test_participant_can_be_removed_from_activity():
    activity_name = "Chess Club"
    email = f"remove-{uuid4()}@mergington.edu"
    activity = activities[activity_name]
    initial_count = len(activity["participants"])

    signup_response = client.post(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": email},
    )
    assert signup_response.status_code == 200
    assert email in activity["participants"]

    remove_response = client.delete(
        f"/activities/{quote(activity_name)}/participants",
        params={"email": email},
    )
    assert remove_response.status_code == 200
    assert remove_response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activity["participants"]
    assert len(activity["participants"]) == initial_count
