import pytest
from app import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Verifies the homepage loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Workout Wizard" in response.data

def test_empty_selection_validation(client):
    """Verifies the app handles empty inputs by returning a helpful message."""
    response = client.post('/generate_workout', json={
        "selected_types": [],
        "selected_sports": [],
        "selected_muscle_targets": []
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["workout_plan"] == []
    assert "Please select at least one attribute" in data["message"]

def test_database_smoke_test(client):
    """Smoke test to ensure the app successfully fetches a known category from Cosmos DB."""
    response = client.post('/generate_workout', json={
        "selected_types": ["cardio"],
        "selected_sports": [],
        "selected_muscle_targets": []
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "workout_plan" in data
    # If the DB is populated, we should get results
    assert len(data["workout_plan"]) > 0