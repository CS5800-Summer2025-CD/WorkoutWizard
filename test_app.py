import pytest
import os
from tinydb import TinyDB, Query
# Import the app and its components from your main app.py file
from app import app, db, EXERCISE_TYPES, SPORTS, MUSCLE_TARGETS
import json
from unittest.mock import patch
import shutil

# Define a temporary database path for testing
TEST_DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_db_temp')
TEST_DB_PATH = os.path.join(TEST_DB_DIR, 'test_workout_db.json')

@pytest.fixture(scope='function')
def client():
    """
    Configures the Flask app for testing and sets up a temporary database.
    """
    app.config['TESTING'] = True
    app.config['TINYDB_PATH'] = TEST_DB_PATH # Not strictly used by app.py's global db, but good for context

    # Override the global db object with a test specific one
    # This ensures each test starts with a clean slate
    global db
    original_db = db # Store the original db connection

    # Ensure the test database directory exists
    os.makedirs(TEST_DB_DIR, exist_ok=True)

    # Initialize TinyDB for the test with the temporary path
    db = TinyDB(TEST_DB_PATH)

    # Populate the test database with the FULL initial data from your app.py
    # This is crucial for tests to reflect the real application's behavior
    db.insert_multiple([
        {
            "name": "Dumbbell Shoulder Press",
            "types": ["strength", "stability"],
            "sports": [],
            "muscle_targets": ["shoulder", "upper body"],
            "equipment": ["dumbbells", "bench"],
            "youtube_link": "https://www.youtube.com/watch?v=qEwKCR5Htq4"
        },
        {
            "name": "Face Pulls",
            "types": ["strength", "recovery", "stability"],
            "sports": [],
            "muscle_targets": ["shoulder", "upper back"],
            "equipment": ["cable machine", "rope attachment"],
            "youtube_link": "https://www.youtube.com/watch?v=rep-R7K4s2o"
        },
        {
            "name": "Lateral Raises (Shoulder Abduction)",
            "types": ["strength", "recovery"],
            "sports": [],
            "muscle_targets": ["shoulder"],
            "equipment": ["dumbbells"],
            "youtube_link": "https://www.youtube.com/watch?v=3VcKaXAYSzg"
        },
        {
            "name": "Push-ups",
            "types": ["strength", "circuit", "anaerobic"],
            "sports": [],
            "muscle_targets": ["chest", "shoulder", "triceps", "core"],
            "equipment": ["none"],
            "youtube_link": "https://www.youtube.com/watch?v=IODxDxX7Hsc"
        },
        {
            "name": "Freestyle Swimming (200m)",
            "types": ["cardio"],
            "sports": ["swimming"],
            "muscle_targets": ["full body"],
            "equipment": ["pool"],
            "youtube_link": "https://www.youtube.com/watch?v=rJ7F7lEw2K0"
        },
        {
            "name": "Freestyle Pull (200m)",
            "types": ["strength", "swimming"],
            "sports": ["swimming"],
            "muscle_targets": ["upper body", "core"],
            "equipment": ["pool", "paddles", "pull buoy"],
            "youtube_link": "https://www.youtube.com/watch?v=wX-y4o3oN4k"
        },
        {
            "name": "Medley Order (12 x 50m)",
            "types": ["cardio", "strength", "swimming"],
            "sports": ["swimming"],
            "muscle_targets": ["full body"],
            "equipment": ["pool"],
            "youtube_link": "https://www.youtube.com/watch?v=qB_p_lqfL1g"
        },
        {
            "name": "Sit-ups",
            "types": ["strength", "core"],
            "sports": [],
            "muscle_targets": ["core"],
            "equipment": ["none"],
            "youtube_link": "https://www.youtube.com/watch?v=J9f2pPjK4cQ"
        },
        {
            "name": "Crunches",
            "types": ["strength", "core"],
            "sports": [],
            "muscle_targets": ["core"],
            "equipment": ["none"],
            "youtube_link": "https://www.youtube.com/watch?v=Xyd_fa5zoEU"
        },
        {
            "name": "Mountain Climbers",
            "types": ["cardio", "core", "anaerobic"],
            "sports": [],
            "muscle_targets": ["core", "full body"],
            "equipment": ["none"],
            "youtube_link": "https://www.youtube.com/watch?v=nmwGFXAPlE4"
        },
        {
            "name": "Plank (60 seconds)",
            "types": ["strength", "core", "stability"],
            "sports": [],
            "muscle_targets": ["core"],
            "equipment": ["none"],
            "youtube_link": "https://www.youtube.com/watch?v=ASdvN_vmF6c"
        },
        {
            "name": "Squats",
            "types": ["strength", "circuit"],
            "sports": [],
            "muscle_targets": ["legs", "glutes", "core"],
            "equipment": ["none", "barbell", "dumbbells"],
            "youtube_link": "https://www.youtube.com/watch?v=ultWtk-f6iQ"
        },
        {
            "name": "Lunges",
            "types": ["strength", "circuit"],
            "sports": [],
            "muscle_targets": ["legs", "glutes"],
            "equipment": ["none", "dumbbells"],
            "youtube_link": "https://www.youtube.com/watch?v=QO8_l7Vl_sA"
        },
        {
            "name": "Running (30 minutes)",
            "types": ["cardio"],
            "sports": ["running"],
            "muscle_targets": ["legs", "full body"],
            "equipment": ["running shoes"],
            "youtube_link": "https://www.youtube.com/watch?v=9Lw7yK8Sg-g"
        },
        {
            "name": "Cycling (45 minutes)",
            "types": ["cardio"],
            "sports": ["biking"],
            "muscle_targets": ["legs", "glutes"],
            "equipment": ["bicycle"],
            "youtube_link": "https://www.youtube.com/watch?v=0kG7R8_Xm5M"
        },
        {
            "name": "Yoga Flow (30 minutes)",
            "types": ["recovery", "flexibility"],
            "sports": ["yoga"],
            "muscle_targets": ["full body"],
            "equipment": ["yoga mat"],
            "youtube_link": "https://www.youtube.com/watch?v=eLwL-P9d4Xo"
        },
        {
            "name": "Foam Rolling (15 minutes)",
            "types": ["recovery"],
            "sports": [],
            "muscle_targets": ["full body"],
            "equipment": ["foam roller"],
            "youtube_link": "https://www.youtube.com/watch?v=yYJ4hYgD4F8"
        }
    ])

    with app.test_client() as client:
        yield client

    # Clean up after each test: close and delete the temporary database
    db.close()
    if os.path.exists(TEST_DB_DIR):
        shutil.rmtree(TEST_DB_DIR) # Use rmtree to remove the directory and its contents

    # Restore the original db object
    db = original_db


def test_index_route(client):
    """Test the main index route."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Workout Wizard" in response.data
    for exercise_type in EXERCISE_TYPES:
        assert bytes(exercise_type.encode('utf-8')) in response.data
    for sport in SPORTS:
        assert bytes(sport.encode('utf-8')) in response.data
    for muscle_target in MUSCLE_TARGETS:
        assert bytes(muscle_target.encode('utf-8')) in response.data

def test_generate_workout_no_attributes_selected(client):
    """Test generating a workout with no attributes selected."""
    response = client.post('/generate_workout', json={
        "selected_types": [],
        "selected_sports": [],
        "selected_muscle_targets": []
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["workout_plan"] == []
    assert "Please select at least one attribute" in data["message"]

def test_generate_workout_single_type(client):
    """Test generating a workout with a single exercise type selected."""
    response = client.post('/generate_workout', json={
        "selected_types": ["cardio"],
        "selected_sports": [],
        "selected_muscle_targets": []
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data["workout_plan"]) > 0
    # Cardio exercises from full dataset: Freestyle Swimming, Mountain Climbers, Running, Cycling, Medley Order
    # Since random.sample limits to 5, we can't assert all, but we expect it to contain known cardio.
    exercise_names = [e["name"] for e in data["workout_plan"]]
    assert any("Swimming" in name for name in exercise_names)
    assert any("Running" in name for name in exercise_names)
    assert any("Cycling" in name for name in exercise_names)


def test_generate_workout_single_sport(client):
    """Test generating a workout with a single sport selected."""
    response = client.post('/generate_workout', json={
        "selected_types": [],
        "selected_sports": ["swimming"],
        "selected_muscle_targets": []
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data["workout_plan"]) > 0
    # Expected: "Freestyle Swimming (200m)", "Freestyle Pull (200m)", "Medley Order (12 x 50m)"
    exercise_names = [e["name"] for e in data["workout_plan"]]
    assert "Freestyle Swimming (200m)" in exercise_names
    assert "Freestyle Pull (200m)" in exercise_names
    assert "Medley Order (12 x 50m)" in exercise_names


def test_generate_workout_single_muscle_target(client):
    """Test generating a workout with a single muscle target selected."""
    response = client.post('/generate_workout', json={
        "selected_types": [],
        "selected_sports": [],
        "selected_muscle_targets": ["core"]
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data["workout_plan"]) > 0
    # Expected core exercises from full dataset:
    # Push-ups, Sit-ups, Crunches, Mountain Climbers, Plank (60 seconds), Squats, Freestyle Pull (200m)
    # Since random.sample limits to 5, we verify a subset of these or that the count is appropriate.
    exercise_names = [e["name"] for e in data["workout_plan"]]
    expected_core_exercises = [
        "Push-ups", "Sit-ups", "Crunches", "Mountain Climbers",
        "Plank (60 seconds)", "Squats", "Freestyle Pull (200m)"
    ]
    # At least check that *some* of the expected ones are present
    assert any(name in exercise_names for name in ["Push-ups", "Sit-ups", "Plank (60 seconds)"])
    # And that all returned exercises actually target core
    for exercise in data["workout_plan"]:
        assert "core" in exercise["muscle_targets"]


def test_generate_workout_multiple_attributes_and_logic(client):
    """Test generating a workout with multiple, combined attributes."""
    response = client.post('/generate_workout', json={
        "selected_types": ["strength", "stability"], # Should match items with EITHER 'strength' OR 'stability'
        "selected_sports": [],
        "selected_muscle_targets": ["shoulder"] # AND 'shoulder'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data["workout_plan"]) > 0
    # Expected exercises based on the AND logic with muscle_targets and OR logic with types:
    # "Dumbbell Shoulder Press" (strength, stability, shoulder) - YES
    # "Face Pulls" (strength, recovery, stability, shoulder) - YES
    # "Lateral Raises (Shoulder Abduction)" (strength, recovery, shoulder) - YES
    # "Push-ups" (strength, circuit, anaerobic, chest, shoulder, triceps, core) - YES (has strength, and shoulder)
    exercise_names = [e["name"] for e in data["workout_plan"]]
    assert "Dumbbell Shoulder Press" in exercise_names
    assert "Face Pulls" in exercise_names
    assert "Lateral Raises (Shoulder Abduction)" in exercise_names
    assert "Push-ups" in exercise_names
    # Verify that returned exercises meet *all* criteria
    for exercise in data["workout_plan"]:
        # Check type condition (strength OR stability)
        type_match = any(t in exercise["types"] for t in ["strength", "stability"])
        assert type_match
        # Check muscle target condition (shoulder)
        assert "shoulder" in exercise["muscle_targets"]


def test_generate_workout_no_matching_exercises(client):
    """Test generating a workout with criteria that yield no matches."""
    response = client.post('/generate_workout', json={
        "selected_types": ["nonexistent_type"], # Should never match
        "selected_sports": ["running"],
        "selected_muscle_targets": ["legs"]
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["workout_plan"] == []
    assert "No exercises found matching your criteria" in data["message"]

@patch('random.sample')
def test_generate_workout_random_selection(mock_sample, client):
    """
    Test that random.sample is called correctly when multiple exercises match.
    Mock random.sample to ensure deterministic results.
    """
    # Configure mock_sample to return a specific subset
    mock_sample.return_value = [
        {
            "name": "Dumbbell Shoulder Press",
            "types": ["strength", "stability"],
            "sports": [],
            "muscle_targets": ["shoulder", "upper body"],
            "equipment": ["dumbbells", "bench"],
            "youtube_link": "https://www.youtube.com/watch?v=qEwKCR5Htq4"
        }
    ]

    response = client.post('/generate_workout', json={
        "selected_types": ["strength"],
        "selected_sports": [],
        "selected_muscle_targets": []
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data["workout_plan"]) == 1
    assert data["workout_plan"][0]["name"] == "Dumbbell Shoulder Press"

    # Verify random.sample was called with the correct arguments
    mock_sample.assert_called_once()
    # First argument to random.sample is the population (list of exercises)
    assert isinstance(mock_sample.call_args[0][0], list)
    # The length of the population should be at least the number of strength exercises in the DB
    # (Dumbbell Shoulder Press, Face Pulls, Lateral Raises, Push-ups, Freestyle Pull, Sit-ups, Crunches, Plank, Squats, Lunges, Medley Order)
    assert len(mock_sample.call_args[0][0]) >= 11
    # Second argument is the sample size (min of actual matches, 5)
    assert mock_sample.call_args[0][1] <= 5


def test_generate_workout_multiple_types_or_logic(client):
    """Test OR logic for multiple types (e.g., strength OR cardio)."""
    response = client.post('/generate_workout', json={
        "selected_types": ["strength", "cardio"],
        "selected_sports": [],
        "selected_muscle_targets": []
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data["workout_plan"]) > 0
    # Check that exercises with either 'strength' or 'cardio' are included
    exercise_names = [e["name"] for e in data["workout_plan"]]
    
    # Expected exercises that have 'strength' or 'cardio' from the full dataset:
    # Dumbbell Shoulder Press (strength)
    # Face Pulls (strength)
    # Lateral Raises (strength)
    # Push-ups (strength, cardio)
    # Freestyle Swimming (cardio)
    # Freestyle Pull (strength)
    # Medley Order (cardio, strength)
    # Sit-ups (strength)
    # Crunches (strength)
    # Mountain Climbers (cardio)
    # Plank (strength)
    # Squats (strength)
    # Lunges (strength)
    # Running (cardio)
    # Cycling (cardio)
    # Yoga Flow (recovery, flexibility) - should NOT be included
    # Foam Rolling (recovery) - should NOT be included

    # Assert that at least some representative strength/cardio exercises are present
    assert any(name in exercise_names for name in ["Dumbbell Shoulder Press", "Push-ups", "Freestyle Swimming (200m)"])
    # Verify no non-matching types are included (e.g., recovery only)
    assert "Yoga Flow (30 minutes)" not in exercise_names
    assert "Foam Rolling (15 minutes)" not in exercise_names

    # More robust check (though can be flakier with random.sample if too many matches)
    for exercise in data["workout_plan"]:
        type_match = any(t in exercise["types"] for t in ["strength", "cardio"])
        assert type_match


def test_generate_workout_complex_combination(client):
    """Test a more complex combination of attributes."""
    response = client.post('/generate_workout', json={
        "selected_types": ["strength"],
        "selected_sports": ["swimming"],
        "selected_muscle_targets": ["full body"]
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data["workout_plan"]) > 0
    exercise_names = [e["name"] for e in data["workout_plan"]]
    # Based on the full dataset:
    # "Medley Order (12 x 50m)" has types=["cardio", "strength", "swimming"], sports=["swimming"], muscle_targets=["full body"]
    # This is the only one that perfectly matches all conditions (strength AND swimming AND full body)
    assert "Medley Order (12 x 50m)" in exercise_names
    # Other swimming exercises might not have strength AND full body
    assert "Freestyle Swimming (200m)" not in exercise_names # only cardio, no strength
    assert "Freestyle Pull (200m)" not in exercise_names # strength, swimming, but no full body (has upper body, core)
    # Other strength exercises might not have swimming AND full body
    assert "Dumbbell Shoulder Press" not in exercise_names