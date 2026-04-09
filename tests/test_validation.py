"""Test validation logic for API endpoints"""

import pytest


class TestActivityValidation:
    """Test activity existence validation"""
    
    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities, sample_emails):
        """Verify 404 returned for signup to non-existent activity"""
        response = client.post("/activities/Invalid Activity/signup", params={"email": sample_emails["valid"]})
        assert response.status_code == 404
    
    def test_unregister_nonexistent_activity_returns_404(self, client, reset_activities, sample_emails):
        """Verify 404 returned for unregister from non-existent activity"""
        response = client.delete("/activities/Invalid Activity/signup", params={"email": sample_emails["valid"]})
        assert response.status_code == 404
    
    @pytest.mark.parametrize("activity_name", [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Soccer Club",
        "Art Club",
        "Drama Club",
        "Debate Club",
        "Science Club"
    ])
    def test_all_valid_activities_exist(self, client, reset_activities, sample_emails, activity_name):
        """Verify all expected activities can be enrolled in"""
        response = client.post(f"/activities/{activity_name}/signup", params={"email": sample_emails["valid"]})
        # Should not be 404 (may be 200 or 400 for other reasons)
        assert response.status_code != 404


class TestEnrollmentValidation:
    """Test enrollment state validation"""
    
    def test_cannot_signup_twice_for_same_activity(self, client, reset_activities, sample_emails):
        """Verify student cannot sign up twice for the same activity"""
        email = sample_emails["valid"]
        
        # First signup
        response1 = client.post("/activities/Basketball Team/signup", params={"email": email})
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post("/activities/Basketball Team/signup", params={"email": email})
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"].lower()
    
    def test_cannot_unregister_if_not_enrolled(self, client, reset_activities, sample_emails):
        """Verify student cannot unregister if not enrolled"""
        email = sample_emails["valid"]
        response = client.delete("/activities/Basketball Team/signup", params={"email": email})
        
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()
    
    def test_can_enroll_in_different_activities(self, client, reset_activities, sample_emails):
        """Verify same student can enroll in multiple different activities"""
        email = sample_emails["valid"]
        
        response1 = client.post("/activities/Basketball Team/signup", params={"email": email})
        assert response1.status_code == 200
        
        response2 = client.post("/activities/Art Club/signup", params={"email": email})
        assert response2.status_code == 200
        
        response3 = client.post("/activities/Science Club/signup", params={"email": email})
        assert response3.status_code == 200


class TestResponseMessages:
    """Test response message content"""
    
    def test_signup_response_contains_email_and_activity(self, client, reset_activities, sample_emails):
        """Verify signup success message contains email and activity name"""
        email = sample_emails["valid"]
        response = client.post("/activities/Basketball Team/signup", params={"email": email})
        
        assert response.status_code == 200
        message = response.json()["message"]
        assert email in message
        assert "Basketball Team" in message
    
    def test_unregister_response_contains_email_and_activity(self, client, reset_activities, sample_emails):
        """Verify unregister success message contains email and activity name"""
        email = sample_emails["existing_chess"]
        response = client.delete("/activities/Chess Club/signup", params={"email": email})
        
        assert response.status_code == 200
        message = response.json()["message"]
        assert email in message
        assert "Chess Club" in message
    
    def test_error_messages_are_helpful(self, client, reset_activities, sample_emails):
        """Verify error messages provide meaningful feedback"""
        email = sample_emails["valid"]
        
        # Activity not found error
        response1 = client.post("/activities/Fake Activity/signup", params={"email": email})
        assert "not found" in response1.json()["detail"].lower()
        
        # Duplicate signup error
        response2 = client.post("/activities/Chess Club/signup", params={"email": "michael@mergington.edu"})
        assert "already" in response2.json()["detail"].lower() or "signed up" in response2.json()["detail"].lower()
        
        # Not enrolled error
        response3 = client.delete("/activities/Basketball Team/signup", params={"email": "noone@mergington.edu"})
        assert "not signed up" in response3.json()["detail"].lower()


class TestParticipantListIntegrity:
    """Test that participant lists maintain integrity"""
    
    def test_signup_adds_to_participants_list(self, client, reset_activities, sample_emails):
        """Verify signup properly adds email to participants list"""
        email = sample_emails["valid"]
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Basketball Team"]["participants"])
        
        client.post("/activities/Basketball Team/signup", params={"email": email})
        
        after_response = client.get("/activities")
        after_count = len(after_response.json()["Basketball Team"]["participants"])
        
        assert after_count == initial_count + 1
        assert email in after_response.json()["Basketball Team"]["participants"]
    
    def test_unregister_removes_from_participants_list(self, client, reset_activities, sample_emails):
        """Verify unregister properly removes email from participants list"""
        email = sample_emails["existing_chess"]
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Chess Club"]["participants"])
        
        client.delete("/activities/Chess Club/signup", params={"email": email})
        
        after_response = client.get("/activities")
        after_count = len(after_response.json()["Chess Club"]["participants"])
        
        assert after_count == initial_count - 1
        assert email not in after_response.json()["Chess Club"]["participants"]
    
    def test_participants_list_is_always_list_type(self, client, reset_activities):
        """Verify participants field is always a list"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list)
