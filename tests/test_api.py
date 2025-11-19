"""
Tests for Mergington High School API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Store original state
    original = {
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
            "description": "Practice basketball skills and compete in inter-school tournaments",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "alex@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Improve swimming techniques and participate in competitions",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["sarah@mergington.edu", "liam@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore various art mediums including painting, drawing, and sculpture",
            "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["emily@mergington.edu", "noah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Develop acting skills and perform in school theater productions",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["ava@mergington.edu", "ethan@mergington.edu"]
        },
        "Debate Team": {
            "description": "Enhance critical thinking and public speaking through competitive debates",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in science and engineering challenges and tournaments",
            "schedule": "Fridays, 3:30 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu", "mason@mergington.edu"]
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original)
    
    yield
    
    # Clean up after test
    activities.clear()
    activities.update(original)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all(self, client):
        """Test that get_activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_structure(self, client):
        """Test that each activity has correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup to an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_duplicate_student(self, client):
        """Test that duplicate signup fails"""
        # First signup
        client.post("/activities/Chess Club/signup?email=test@mergington.edu")
        
        # Try to signup again
        response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup to non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_increases_participant_count(self, client):
        """Test that signup increases participant count"""
        # Get initial count
        activities_response = client.get("/activities")
        initial_count = len(activities_response.json()["Chess Club"]["participants"])
        
        # Signup
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        
        # Get new count
        activities_response = client.get("/activities")
        new_count = len(activities_response.json()["Chess Club"]["participants"])
        
        assert new_count == initial_count + 1


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        # Verify student is registered
        activities_response = client.get("/activities")
        assert "michael@mergington.edu" in activities_response.json()["Chess Club"]["participants"]
        
        # Unregister
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Verify student was removed
        activities_response = client.get("/activities")
        assert "michael@mergington.edu" not in activities_response.json()["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from non-existent activity fails"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_not_registered_student(self, client):
        """Test unregister of student not in activity fails"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not registered" in data["detail"]
    
    def test_unregister_decreases_participant_count(self, client):
        """Test that unregister decreases participant count"""
        # Get initial count
        activities_response = client.get("/activities")
        initial_count = len(activities_response.json()["Chess Club"]["participants"])
        
        # Unregister
        client.delete("/activities/Chess Club/unregister?email=michael@mergington.edu")
        
        # Get new count
        activities_response = client.get("/activities")
        new_count = len(activities_response.json()["Chess Club"]["participants"])
        
        assert new_count == initial_count - 1


class TestIntegrationScenarios:
    """Integration tests for complete user workflows"""
    
    def test_signup_and_unregister_workflow(self, client):
        """Test complete workflow of signup and unregister"""
        email = "workflow@mergington.edu"
        activity = "Programming Class"
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[activity]["participants"]
        assert email not in initial_participants
        
        # Signup
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signup
        after_signup = client.get("/activities")
        assert email in after_signup.json()[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200
        
        # Verify unregister
        after_unregister = client.get("/activities")
        assert email not in after_unregister.json()[activity]["participants"]
    
    def test_multiple_activities_signup(self, client):
        """Test that a student can sign up for multiple activities"""
        email = "multitask@mergington.edu"
        
        # Signup for multiple activities
        client.post(f"/activities/Chess Club/signup?email={email}")
        client.post(f"/activities/Art Studio/signup?email={email}")
        client.post(f"/activities/Drama Club/signup?email={email}")
        
        # Verify student is in all activities
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]
        assert email in data["Art Studio"]["participants"]
        assert email in data["Drama Club"]["participants"]
