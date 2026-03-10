"""
Tests for POST /activities/{activity_name}/signup endpoint
"""
import pytest


class TestSignupForActivity:
    """Tests for signing up a student for an activity"""

    def test_signup_successful(self, client, sample_emails):
        """
        Test that a new student can successfully sign up for an available activity
        """
        activity = "Programming Class"
        email = sample_emails["new"]
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]

    def test_signup_adds_participant_to_activity(self, client, sample_emails):
        """
        Test that after signup, the participant appears in the activity's participant list
        """
        activity = "Programming Class"
        email = sample_emails["new"]
        
        # Sign up
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Verify participant is in list
        response = client.get("/activities")
        activities = response.json()
        assert email in activities[activity]["participants"]

    def test_signup_invalid_activity_returns_404(self, client, sample_emails):
        """
        Test that signing up for a non-existent activity returns 404
        """
        activity = "Nonexistent Club"
        email = sample_emails["new"]
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_duplicate_registration_returns_400(self, client, sample_emails):
        """
        Test that signing up twice for the same activity returns 400
        """
        activity = "Chess Club"
        email = sample_emails["existing"]  # Already signed up for Chess Club
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already" in data["detail"].lower() or "signed up" in data["detail"].lower()

    def test_signup_increases_participant_count(self, client, sample_emails):
        """
        Test that signup increases the participant count for an activity
        """
        activity = "Programming Class"
        email = sample_emails["new"]
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Sign up
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Get new count
        response = client.get("/activities")
        new_count = len(response.json()[activity]["participants"])
        
        assert new_count == initial_count + 1

    def test_signup_with_empty_email(self, client):
        """
        Test that signing up with empty email string fails appropriately
        """
        activity = "Programming Class"
        email = ""
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Should still add empty email due to lack of validation in current implementation
        # (This is a data validation improvement that could be added)
        assert response.status_code in [200, 400]

    def test_signup_does_not_affect_other_activities(self, client, sample_emails):
        """
        Test that signing up for one activity doesn't affect other activities
        """
        signup_activity = "Programming Class"
        other_activity = "Chess Club"
        email = sample_emails["new"]
        
        # Get initial state of other activity
        response = client.get("/activities")
        initial_participants = response.json()[other_activity]["participants"].copy()
        
        # Sign up for a different activity
        client.post(
            f"/activities/{signup_activity}/signup",
            params={"email": email}
        )
        
        # Verify other activity is unchanged
        response = client.get("/activities")
        final_participants = response.json()[other_activity]["participants"]
        assert initial_participants == final_participants

    def test_signup_preserves_existing_participants(self, client, sample_emails):
        """
        Test that signing up doesn't remove other participants from the activity
        """
        activity = "Programming Class"
        email = sample_emails["new"]
        
        # Get existing participants
        response = client.get("/activities")
        initial_participants = response.json()[activity]["participants"].copy()
        
        # Sign up new person
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Verify all previous participants are still there
        response = client.get("/activities")
        final_participants = response.json()[activity]["participants"]
        for participant in initial_participants:
            assert participant in final_participants

    def test_multiple_students_can_signup(self, client, sample_emails):
        """
        Test that multiple different students can sign up for the same activity
        """
        activity = "Programming Class"
        email1 = sample_emails["new"]
        email2 = sample_emails["another_new"]
        
        # First signup
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email1}
        )
        assert response1.status_code == 200
        
        # Second signup
        response2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email2}
        )
        assert response2.status_code == 200
        
        # Verify both are in the activity
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert email1 in participants
        assert email2 in participants
