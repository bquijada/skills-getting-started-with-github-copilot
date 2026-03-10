"""
Pytest configuration and shared fixtures for FastAPI tests
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import the real app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


def get_fresh_activities():
    """
    Returns a fresh copy of the activities database for test isolation.
    """
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for intramural and inter-school games",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in friendly matches",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["sarah@mergington.edu", "james@mergington.edu"]
        },
        "Digital Art Studio": {
            "description": "Create digital art, graphic design, and animation projects",
            "schedule": "Tuesdays and Fridays, 4:00 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu"]
        },
        "Theater Club": {
            "description": "Perform in school plays and develop acting and stage presence skills",
            "schedule": "Mondays, Wednesdays, Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["grace@mergington.edu", "ryan@mergington.edu", "lucas@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills through competitive debate",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["avery@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore STEM concepts through hands-on experiments and projects",
            "schedule": "Wednesdays, 3:30 PM - 4:45 PM",
            "max_participants": 20,
            "participants": ["tyler@mergington.edu", "natalie@mergington.edu"]
        }
    }


@pytest.fixture
def client(monkeypatch):
    """
    Provides a TestClient for the real app with fresh activities data for each test.
    Uses monkeypatch to inject clean state, ensuring complete test isolation.
    """
    # Reset the app's activities dictionary to a fresh state
    monkeypatch.setattr("app.activities", get_fresh_activities())
    return TestClient(app)


@pytest.fixture
def sample_activities(client):
    """
    Provides sample test data and returns the fresh activities state.
    This fixture is used to verify the structure of activities.
    """
    response = client.get("/activities")
    return response.json()


@pytest.fixture
def sample_emails():
    """
    Provides sample student emails for testing
    """
    return {
        "existing": "michael@mergington.edu",  # Already signed up for Chess Club
        "new": "newstudent@mergington.edu",
        "another_new": "anotherstudent@mergington.edu",
    }


@pytest.fixture
def sample_activities_names():
    """
    Provides sample activity names for testing
    """
    return {
        "existing": "Chess Club",
        "full_or_near_full": "Theater Club",  # Already has 3 participants
        "available": "Programming Class",
        "invalid": "Nonexistent Club",
    }
