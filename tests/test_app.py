"""Tests for the FastAPI application endpoints."""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns status 200."""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary."""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)
    
    def test_get_activities_contains_expected_activities(self, client):
        """Test that response contains expected activity names."""
        response = client.get("/activities")
        activities = response.json()
        
        expected_activities = [
            "Tennis Club",
            "Basketball Team",
            "Drama Club",
            "Art Studio",
            "Debate Team",
            "Science Club",
            "Chess Club",
            "Programming Class",
            "Gym Class"
        ]
        
        for activity in expected_activities:
            assert activity in activities
    
    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_details in activities.items():
            for field in required_fields:
                assert field in activity_details, f"Activity '{activity_name}' missing field '{field}'"


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_for_activity_success(self, client, reset_activities):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Tennis Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant."""
        email = "newstudent@mergington.edu"
        client.post(
            "/activities/Tennis Club/signup",
            params={"email": email}
        )
        
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Tennis Club"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for non-existent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_participant(self, client, reset_activities):
        """Test that duplicate signups are rejected."""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            "/activities/Tennis Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            "/activities/Tennis Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity."""
        email = "newstudent@mergington.edu"
        
        # First signup
        client.post(
            "/activities/Tennis Club/signup",
            params={"email": email}
        )
        
        # Then unregister
        response = client.delete(
            "/activities/Tennis Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant."""
        email = "newstudent@mergington.edu"
        
        # Signup
        client.post(
            "/activities/Tennis Club/signup",
            params={"email": email}
        )
        
        # Unregister
        client.delete(
            "/activities/Tennis Club/unregister",
            params={"email": email}
        )
        
        # Verify removal
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Tennis Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from non-existent activity returns 404."""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
    
    def test_unregister_not_signed_up(self, client):
        """Test unregistering someone not signed up returns 400."""
        response = client.delete(
            "/activities/Tennis Club/unregister",
            params={"email": "nosignup@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]


class TestRootEndpoint:
    """Tests for the root endpoint."""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
