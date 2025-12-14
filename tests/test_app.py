import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball Team" in data
    assert "participants" in data["Basketball Team"]

def test_signup_success():
    # Test successful signup
    response = client.post("/activities/Basketball%20Team/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up test@example.com for Basketball Team" in data["message"]

    # Check if added
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" in data["Basketball Team"]["participants"]

def test_signup_duplicate():
    # First signup
    client.post("/activities/Soccer%20Club/signup?email=duplicate@example.com")
    # Second signup should fail
    response = client.post("/activities/Soccer%20Club/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Student already signed up" in data["detail"]

def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent%20Activity/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_signup_activity_full():
    # Chess Club has 2 participants, max 12, so not full, but let's assume we fill it
    # Actually, to test full, I need an activity that's almost full.
    # Gym Class has 2 participants, max 30, so add 28 more.
    # But for simplicity, let's add a test that assumes it's full by adding many.
    # Actually, better to modify the test to fill it.

    # For now, since max is 30, I'll add 28 participants to Gym Class.
    for i in range(28):
        client.post(f"/activities/Gym%20Class/signup?email=user{i}@example.com")

    # Now it should be full
    response = client.post("/activities/Gym%20Class/signup?email=full@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Activity is full" in data["detail"]

def test_unregister_success():
    # First signup
    client.post("/activities/Art%20Club/signup?email=unregister@example.com")
    # Then unregister
    response = client.delete("/activities/Art%20Club/unregister?email=unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered unregister@example.com from Art Club" in data["message"]

    # Check if removed
    response = client.get("/activities")
    data = response.json()
    assert "unregister@example.com" not in data["Art Club"]["participants"]

def test_unregister_not_signed_up():
    response = client.delete("/activities/Drama%20Club/unregister?email=notsigned@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Student not signed up" in data["detail"]

def test_unregister_activity_not_found():
    response = client.delete("/activities/Nonexistent%20Activity/unregister?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    # Since it's a redirect, but TestClient follows redirects by default? Wait, no, FastAPI redirect.
    # Actually, RedirectResponse returns 307, but TestClient follows it.
    # But in test, it should follow to /static/index.html, but since static is mounted, it might work.
    # For simplicity, just check it's not 404.