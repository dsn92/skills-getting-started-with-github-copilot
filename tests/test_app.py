"""
Tests for the Mergington High School Activities API
"""

from app import app
from fastapi.testclient import TestClient
import pytest
import sys
from pathlib import Path

# Add src directory to path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


client = TestClient(app)


class TestActivities:
    """Tests for the /activities endpoint"""

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_activities_contain_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()

        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_specific_activities_exist(self):
        """Test that expected activities are in the list"""
        response = client.get("/activities")
        activities = response.json()

        expected_activities = ["Basketball",
                               "Tennis", "Debate Club", "Chess Club"]
        for activity in expected_activities:
            assert activity in activities


class TestSignup:
    """Tests for the signup endpoint"""

    def test_signup_new_student(self):
        """Test signing up a new student for an activity"""
        response = client.post(
            "/activities/Basketball/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_duplicate_student(self):
        """Test that signing up the same student twice fails"""
        email = "duplicate@mergington.edu"

        # First signup should succeed
        response1 = client.post(
            f"/activities/Basketball/signup?email={email}"
        )
        assert response1.status_code == 200

        # Second signup should fail
        response2 = client.post(
            f"/activities/Basketball/signup?email={email}"
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/NonexistentActivity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]


class TestUnregister:
    """Tests for the unregister endpoint"""

    def test_unregister_existing_student(self):
        """Test unregistering an existing student from an activity"""
        email = "unregister_test@mergington.edu"

        # First sign up
        signup_response = client.post(
            f"/activities/Tennis/signup?email={email}"
        )
        assert signup_response.status_code == 200

        # Then unregister
        unregister_response = client.post(
            f"/activities/Tennis/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        data = unregister_response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_nonexistent_student(self):
        """Test unregistering a student who is not signed up"""
        response = client.post(
            "/activities/Math Olympiad/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_nonexistent_activity(self):
        """Test unregistering from a non-existent activity"""
        response = client.post(
            "/activities/FakeActivity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_participant_removed_from_list(self):
        """Test that unregistering removes the participant from the activity"""
        email = "participant_removal_test@mergington.edu"
        activity = "Drama Club"

        # Sign up
        client.post(f"/activities/{activity}/signup?email={email}")

        # Verify participant is in the list
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]

        # Unregister
        client.post(f"/activities/{activity}/unregister?email={email}")

        # Verify participant is no longer in the list
        activities = client.get("/activities").json()
        assert email not in activities[activity]["participants"]


class TestRoot:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static(self):
        """Test that the root endpoint redirects to static files"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
