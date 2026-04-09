"""Test API endpoint functionality"""

import pytest


class TestRootEndpoint:
    """Test GET / endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Verify root endpoint redirects to static home page"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Test GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Verify get_activities returns all 9 activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
        assert "Basketball Team" in activities
        assert "Soccer Club" in activities
        assert "Art Club" in activities
        assert "Drama Club" in activities
        assert "Debate Club" in activities
        assert "Science Club" in activities
    
    def test_get_activities_returns_proper_structure(self, client, reset_activities):
        """Verify activity data structure has all required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_includes_initial_participants(self, client, reset_activities):
        """Verify activities include initial participant enrollments"""
        response = client.get("/activities")
        activities = response.json()
        
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]
        assert "emma@mergington.edu" in activities["Programming Class"]["participants"]
        assert "sophia@mergington.edu" in activities["Programming Class"]["participants"]


class TestSignupEndpoint:
    """Test POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_valid_student(self, client, reset_activities, sample_emails):
        """Verify student can sign up for an available activity"""
        email = sample_emails["valid"]
        response = client.post("/activities/Basketball Team/signup", params={"email": email})
        
        assert response.status_code == 200
        assert email in response.json()["message"]
        
        # Verify student is now in participants list
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Basketball Team"]["participants"]
    
    def test_signup_activity_not_found(self, client, reset_activities, sample_emails):
        """Verify signup fails when activity doesn't exist"""
        email = sample_emails["valid"]
        response = client.post("/activities/Nonexistent Club/signup", params={"email": email})
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_duplicate_enrollment(self, client, reset_activities, sample_emails):
        """Verify student cannot sign up twice for same activity"""
        email = sample_emails["existing_chess"]
        response = client.post("/activities/Chess Club/signup", params={"email": email})
        
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_multiple_activities(self, client, reset_activities, sample_emails):
        """Verify student can sign up for multiple activities"""
        email = sample_emails["valid"]
        
        # Sign up for first activity
        response1 = client.post("/activities/Basketball Team/signup", params={"email": email})
        assert response1.status_code == 200
        
        # Sign up for second activity
        response2 = client.post("/activities/Soccer Club/signup", params={"email": email})
        assert response2.status_code == 200
        
        # Verify both signups succeeded
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Basketball Team"]["participants"]
        assert email in activities_data["Soccer Club"]["participants"]
    
    def test_signup_maintains_existing_participants(self, client, reset_activities, sample_emails):
        """Verify new signup doesn't remove existing participants"""
        email = sample_emails["valid"]
        response = client.post("/activities/Chess Club/signup", params={"email": email})
        
        assert response.status_code == 200
        activities_response = client.get("/activities")
        chess_participants = activities_response.json()["Chess Club"]["participants"]
        
        # Original participants should still be there
        assert "michael@mergington.edu" in chess_participants
        assert "daniel@mergington.edu" in chess_participants
        # New participant should be added
        assert email in chess_participants


class TestUnregisterEndpoint:
    """Test DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_unregister_valid_student(self, client, reset_activities, sample_emails):
        """Verify student can unregister from an activity they're enrolled in"""
        email = sample_emails["existing_chess"]
        response = client.delete("/activities/Chess Club/signup", params={"email": email})
        
        assert response.status_code == 200
        assert email in response.json()["message"]
        
        # Verify student is no longer in participants list
        activities_response = client.get("/activities")
        assert email not in activities_response.json()["Chess Club"]["participants"]
    
    def test_unregister_activity_not_found(self, client, reset_activities, sample_emails):
        """Verify unregister fails when activity doesn't exist"""
        email = sample_emails["valid"]
        response = client.delete("/activities/Nonexistent Club/signup", params={"email": email})
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_unregister_student_not_enrolled(self, client, reset_activities, sample_emails):
        """Verify unregister fails when student is not enrolled"""
        email = sample_emails["valid"]
        response = client.delete("/activities/Chess Club/signup", params={"email": email})
        
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()
    
    def test_unregister_maintains_other_participants(self, client, reset_activities, sample_emails):
        """Verify unregistering one student doesn't affect others"""
        email_to_remove = sample_emails["existing_chess"]
        
        response = client.delete("/activities/Chess Club/signup", params={"email": email_to_remove})
        assert response.status_code == 200
        
        activities_response = client.get("/activities")
        chess_participants = activities_response.json()["Chess Club"]["participants"]
        
        # Removed participant should not be there
        assert email_to_remove not in chess_participants
        # Other participants should remain
        assert "daniel@mergington.edu" in chess_participants or "michael@mergington.edu" in chess_participants
    
    def test_signup_after_unregister(self, client, reset_activities, sample_emails):
        """Verify student can re-enroll after unregistering"""
        email = sample_emails["existing_chess"]
        
        # Unregister
        response1 = client.delete("/activities/Chess Club/signup", params={"email": email})
        assert response1.status_code == 200
        
        # Re-enroll
        response2 = client.post("/activities/Chess Club/signup", params={"email": email})
        assert response2.status_code == 200
        
        # Verify back in participants list
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Chess Club"]["participants"]
