"""Test data structure and initialization"""

import pytest


class TestActivityDataStructure:
    """Test that activities have correct data structure"""
    
    def test_all_activities_have_required_fields(self, client, reset_activities):
        """Verify each activity has description, schedule, max_participants, participants"""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        for activity_name, activity_data in activities.items():
            assert required_fields.issubset(activity_data.keys()), \
                f"{activity_name} missing required fields"
    
    def test_description_is_string(self, client, reset_activities):
        """Verify all descriptions are strings"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["description"], str), \
                f"{activity_name} description is not a string"
            assert len(activity_data["description"]) > 0, \
                f"{activity_name} has empty description"
    
    def test_schedule_is_string(self, client, reset_activities):
        """Verify all schedules are strings"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["schedule"], str), \
                f"{activity_name} schedule is not a string"
            assert len(activity_data["schedule"]) > 0, \
                f"{activity_name} has empty schedule"
    
    def test_max_participants_is_positive_integer(self, client, reset_activities):
        """Verify max_participants is a positive integer"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["max_participants"], int), \
                f"{activity_name} max_participants is not an integer"
            assert activity_data["max_participants"] > 0, \
                f"{activity_name} max_participants is not positive"
    
    def test_participants_is_list(self, client, reset_activities):
        """Verify participants field is always a list"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list), \
                f"{activity_name} participants is not a list"


class TestInitialActivities:
    """Test that all expected activities are initialized"""
    
    def test_nine_activities_exist(self, client, reset_activities):
        """Verify exactly 9 activities are initialized"""
        response = client.get("/activities")
        activities = response.json()
        assert len(activities) == 9
    
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
    def test_expected_activities_exist(self, client, reset_activities, activity_name):
        """Verify each expected activity exists in the system"""
        response = client.get("/activities")
        activities = response.json()
        assert activity_name in activities, f"{activity_name} not found in activities"
    
    def test_activity_names_are_case_sensitive(self, client, reset_activities):
        """Verify activity names are case-sensitive in the system"""
        response = client.get("/activities")
        activities = response.json()
        
        # "Chess Club" should exist
        assert "Chess Club" in activities
        
        # "chess club" should not
        assert "chess club" not in activities


class TestInitialParticipants:
    """Test initial participant assignments"""
    
    def test_chess_club_has_initial_participants(self, client, reset_activities):
        """Verify Chess Club has initial participants"""
        response = client.get("/activities")
        activities = response.json()
        
        chess_participants = activities["Chess Club"]["participants"]
        assert len(chess_participants) > 0
        assert "michael@mergington.edu" in chess_participants
        assert "daniel@mergington.edu" in chess_participants
    
    def test_programming_class_has_initial_participants(self, client, reset_activities):
        """Verify Programming Class has initial participants"""
        response = client.get("/activities")
        activities = response.json()
        
        programming_participants = activities["Programming Class"]["participants"]
        assert len(programming_participants) > 0
        assert "emma@mergington.edu" in programming_participants
        assert "sophia@mergington.edu" in programming_participants
    
    def test_gym_class_has_initial_participants(self, client, reset_activities):
        """Verify Gym Class has initial participants"""
        response = client.get("/activities")
        activities = response.json()
        
        gym_participants = activities["Gym Class"]["participants"]
        assert len(gym_participants) > 0
        assert "john@mergington.edu" in gym_participants
        assert "olivia@mergington.edu" in gym_participants
    
    def test_some_activities_start_empty(self, client, reset_activities):
        """Verify some activities have no initial participants"""
        response = client.get("/activities")
        activities = response.json()
        
        # These activities should start empty
        empty_activities = [
            "Basketball Team",
            "Soccer Club",
            "Art Club",
            "Drama Club",
            "Debate Club",
            "Science Club"
        ]
        
        for activity_name in empty_activities:
            assert len(activities[activity_name]["participants"]) == 0, \
                f"{activity_name} should start with no participants"


class TestMaxParticipants:
    """Test max_participants values"""
    
    def test_max_participants_varies_by_activity(self, client, reset_activities):
        """Verify different activities have different max participant limits"""
        response = client.get("/activities")
        activities = response.json()
        
        max_values = [activity["max_participants"] for activity in activities.values()]
        # Should have at least 2 different values
        assert len(set(max_values)) >= 2
    
    @pytest.mark.parametrize("activity,expected_max", [
        ("Chess Club", 12),
        ("Programming Class", 20),
        ("Gym Class", 30),
        ("Basketball Team", 15),
        ("Soccer Club", 22),
        ("Art Club", 18),
        ("Drama Club", 20),
        ("Debate Club", 16),
        ("Science Club", 25),
    ])
    def test_specific_max_participants(self, client, reset_activities, activity, expected_max):
        """Verify specific activities have expected max participant limits"""
        response = client.get("/activities")
        activities = response.json()
        
        assert activities[activity]["max_participants"] == expected_max
