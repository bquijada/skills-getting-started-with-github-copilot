"""
Tests for GET /activities endpoint
"""
import pytest


class TestGetActivities:
    """Tests for retrieving activities"""

    def test_get_activities_returns_all_activities(self, client):
        """
        Test that GET /activities returns all activities
        """
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0

    def test_activities_have_required_fields(self, client):
        """
        Test that each activity has all required fields
        """
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert all(field in activity_data for field in required_fields)
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)

    def test_activities_participants_are_valid_emails(self, client):
        """
        Test that all participants in activities are valid email-like strings
        """
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email format check

    def test_max_participants_is_positive_integer(self, client):
        """
        Test that max_participants is a positive integer
        """
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0

    def test_participants_count_does_not_exceed_max(self, client):
        """
        Test that participant count never exceeds max_participants for any activity
        (data consistency check)
        """
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            participant_count = len(activity_data["participants"])
            max_participants = activity_data["max_participants"]
            assert participant_count <= max_participants, \
                f"{activity_name} has {participant_count} participants but max is {max_participants}"

    def test_no_duplicate_participants_in_activity(self, client):
        """
        Test that no participant appears twice in the same activity
        """
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            participants = activity_data["participants"]
            assert len(participants) == len(set(participants)), \
                f"{activity_name} has duplicate participants"
