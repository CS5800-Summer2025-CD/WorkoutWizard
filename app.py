# app.py - Flask Backend for Workout Wizard

from flask import Flask, request, jsonify, render_template
from tinydb import TinyDB, Query
import os
import random

# Initialize Flask app
app = Flask(__name__)

# Define the database path
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db')
DB_PATH = os.path.join(DB_DIR, 'workout_db.json')

# Ensure the database directory exists
os.makedirs(DB_DIR, exist_ok=True)

# Initialize TinyDB
db = TinyDB(DB_PATH)

# Check if the database is empty and populate it with initial data if needed
if not db.all():
    print("Populating TinyDB with initial data...")
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
            "muscle_targets": ["chest", "shoulders", "triceps", "core"],
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
    print("Database populated.")

# Define the allowed exercise attributes
EXERCISE_TYPES = ["cardio", "strength", "circuit", "anaerobic", "recovery", "stability", "flexibility", "core"]
SPORTS = ["running", "swimming", "biking", "tennis", "yoga"]
MUSCLE_TARGETS = ["shoulder", "back", "calves", "legs", "chest", "triceps", "biceps", "glutes", "core", "upper body", "full body", "upper back"]

@app.route('/')
def index():
    """Renders the main index.html page."""
    return render_template('index.html',
                           exercise_types=EXERCISE_TYPES,
                           sports=SPORTS,
                           muscle_targets=MUSCLE_TARGETS)

@app.route('/generate_workout', methods=['POST'])
def generate_workout():
    """
    Generates a workout plan based on user-selected attributes.
    Expects a JSON payload with 'selected_types', 'selected_sports',
    and 'selected_muscle_targets'.
    """
    data = request.get_json()
    selected_types = data.get('selected_types', [])
    selected_sports = data.get('selected_sports', [])
    selected_muscle_targets = data.get('selected_muscle_targets', [])

    # Create a TinyDB Query object
    Exercise = Query()

    # Build the query dynamically based on selected attributes
    query_conditions = []

    # Add conditions for exercise types
    if selected_types:
        type_conditions = [Exercise.types.any(t) for t in selected_types]
        query_conditions.append(type_conditions[0])
        for cond in type_conditions[1:]:
            query_conditions[0] = query_conditions[0] | cond

    # Add conditions for sports
    if selected_sports:
        sport_conditions = [Exercise.sports.any(s) for s in selected_sports]
        if query_conditions:
            sport_combined = sport_conditions[0]
            for cond in sport_conditions[1:]:
                sport_combined = sport_combined | cond
            query_conditions[0] = query_conditions[0] & sport_combined
        else:
            query_conditions.append(sport_conditions[0])
            for cond in sport_conditions[1:]:
                query_conditions[0] = query_conditions[0] | cond

    # Add conditions for muscle targets
    if selected_muscle_targets:
        muscle_conditions = [Exercise.muscle_targets.any(m) for m in selected_muscle_targets]
        if query_conditions:
            muscle_combined = muscle_conditions[0]
            for cond in muscle_conditions[1:]:
                muscle_combined = muscle_combined | cond
            query_conditions[0] = query_conditions[0] & muscle_combined
        else:
            query_conditions.append(muscle_conditions[0])
            for cond in muscle_conditions[1:]:
                query_conditions[0] = query_conditions[0] | cond

    # Combine all query conditions with a logical AND
    final_query = None
    if query_conditions:
        final_query = query_conditions[0]
        for cond in query_conditions[1:]:
            final_query = final_query & cond

    # Perform the search
    if final_query:
        matching_exercises = db.search(final_query)
    else:
        # If no attributes are selected, return a message or a default set of exercises
        return jsonify({"workout_plan": [], "message": "Please select at least one attribute to generate a workout."})

    # If too many exercises are found, select a random subset
    # Otherwise, use all found exercises
    num_exercises_to_select = min(len(matching_exercises), 5) # Max 5 exercises for a workout plan
    workout_plan = random.sample(matching_exercises, num_exercises_to_select)

    if not workout_plan:
        return jsonify({"workout_plan": [], "message": "No exercises found matching your criteria. Try different selections!"})

    return jsonify({"workout_plan": workout_plan})

# To run the Flask app:
# 1. Save this code as `app.py`.
# 2. Make sure you have Flask and TinyDB installed: `pip install Flask TinyDB`
# 3. Run from your terminal: `python app.py`
#    (Or `flask run` if your Flask environment is set up)
# The app will be available at http://127.0.0.1:5000/
if __name__ == '__main__':
    app.run(debug=True)
