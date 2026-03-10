"""
Tests for DELETE /activities/{activity_name}/signup endpoint
"""
import pytest


class TestUnregisterFromActivity:
    """Tests for unregistering a student from an activity"""

    def test_unregister_successful(self, client, sample_emails):
        """
        Test that a student can successfully unregister from an activity they're in
        """
        activity = "Chess Club"
        email = sample_emails["existing"]  # Already in Chess Club
        
        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        assert email in data["message"]

    def test_unregister_removes_participant(self, client, sample_emails):
        """
        Test that after unregister, the participant is removed from the activity
        """
        activity = "Chess Club"
        email = sample_emails["existing"]
        
        # Unregister
        client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Verify participant is removed
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities[activity]["participants"]

    def test_unregister_invalid_activity_returns_404(self, client, sample_emails):
        """
        Test that unregistering from a non-existent activity returns 404
        """
        activity = "Nonexistent Club"
        email = sample_emails["existing"]
        
        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_unregister_not_registered_returns_400(self, client, sample_emails):
        """
        Test that unregistering someone not registered returns 400
        """
        activity = "Chess Club"
        email = sample_emails["new"]  # Not registered for Chess Club
        
        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert ("not registered" in data["detail"].lower() or 
                "not found" in data["detail"].lower())

    def test_unregister_decreases_participant_count(self, client, sample_emails):
        """
        Test that unregister decreases the participant count for an activity
        """
        activity = "Chess Club"
        email = sample_emails["existing"]
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Unregister
        client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Get new count
        response = client.get("/activities")
        new_count = len(response.json()[activity]["participants"])
        
        assert new_count == initial_count - 1

    def test_unregister_does_not_affect_other_activities(self, client, sample_emails):
        """
        Test that unregistering from one activity doesn't affect other activities
        """
        unregister_activity = "Chess Club"
        other_activity = "Programming Class"
        email = sample_emails["existing"]  # In Chess Club
        
        # Get initial state of other activity
        response = client.get("/activities")
        initial_participants = response.json()[other_activity]["participants"].copy()
        
        # Unregister from a different activity
        client.delete(
            f"/activities/{unregister_activity}/signup",
            params={"email": email}
        )
        
        # Verify other activity is unchanged
        response = client.get("/activities")
        final_participants = response.json()[other_activity]["participants"]
        assert initial_participants == final_participants

    def test_unregister_preserves_other_participants(self, client, sample_emails):
        """
        Test that unregistering doesn't remove other participants from the activity
        """
        activity = "Chess Club"
        email = sample_emails["existing"]
        
        # Get existing participants
        response = client.get("/activities")
        initial_participants = response.json()[activity]["participants"].copy()
        
        # Unregister one person
        client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Verify all other participants are still there
        response = client.get("/activities")
        final_participants = response.json()[activity]["participants"]
        for participant in initial_participants:
            if participant != email:
                assert participant in final_participants

    def test_unregister_twice_returns_400_second_time(self, client, sample_emails):
        """
        Test that unregistering twice returns 400 on the second attempt
        """
        activity = "Chess Club"
        email = sample_emails["existing"]
        
        # First unregister succeeds
        response1 = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second unregister fails
        response2 = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "detail" in data

    def test_signup_then_unregister_roundtrip(self, client, sample_emails):
        """
        Test signup followed by unregister returns activity to original state
        """
        activity = "Programming Class"
        email = sample_emails["new"]
        
        # Get initial state
        response = client.get("/activities")
        initial_state = response.json()[activity]["participants"].copy()
        
        # Sign up
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Verify signup worked
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        # Verify back to original state
        response = client.get("/activities")
        final_state = response.json()[activity]["participants"]
        assert initial_state == final_state

    def test_multiple_unregisters_from_same_activity(self, client, sample_emails):
        """
        Test that multiple different participants can unregister from the same activity
        """
        activity = "Theater Club"  # Has multiple participants
        
        # Get initial participants
        response = client.get("/activities")
        initial_participants = response.json()[activity]["participants"].copy()
        
        if len(initial_participants) >= 2:
            email1 = initial_participants[0]
            email2 = initial_participants[1]
            
            # Unregister both
            response1 = client.delete(
                f"/activities/{activity}/signup",
                params={"email": email1}
            )
            response2 = client.delete(
                f"/activities/{activity}/signup",
                params={"email": email2}
            )
            
            assert response1.status_code == 200
            assert response2.status_code == 200
            
            # Verify both are gone
            response = client.get("/activities")
            final_participants = response.json()[activity]["participants"]
            assert email1 not in final_participants
            assert email2 not in final_participants
