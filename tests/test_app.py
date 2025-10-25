import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that root path redirects to /static/index.html"""
    response = client.get("/")
    assert response.status_code == 200  # Success, served directly by StaticFiles
    assert "text/html" in response.headers["content-type"].lower()

def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    # Test structure of an activity
    activity = list(activities.values())[0]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity

def test_signup_success():
    """Test successful activity signup"""
    activity_name = "Chess Club"
    email = "test_user@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

def test_signup_duplicate():
    """Test duplicate signup prevention"""
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Using existing participant
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()

def test_signup_nonexistent_activity():
    """Test signup for non-existent activity"""
    activity_name = "Nonexistent Club"
    email = "test_user@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_unregister_success():
    """Test successful unregistration"""
    # First sign up a test user
    activity_name = "Chess Club"
    email = "test_unregister@mergington.edu"
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Then try to unregister them
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

def test_unregister_not_registered():
    """Test unregistration when user is not registered"""
    activity_name = "Chess Club"
    email = "not_registered@mergington.edu"
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()

def test_unregister_nonexistent_activity():
    """Test unregistration from non-existent activity"""
    activity_name = "Nonexistent Club"
    email = "test_user@mergington.edu"
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()