# app.py

from flask import Flask, render_template, request, jsonify
from tinydb import TinyDB, Query
import os
import random

app = Flask(__name__)

# --- TinyDB Configuration ---
# Get the base directory of the application (where app.py resides)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the local 'db' folder for TinyDB when running development locally
LOCAL_DB_DIR = os.path.join(BASE_DIR, 'db')
DEFAULT_DB_FILE_PATH = os.path.join(LOCAL_DB_DIR, 'workout_db.json')

# Get the TinyDB path from an environment variable (for Azure deployment),
# or default to the 'db' folder within the local project root for development.
DB_PATH = os.environ.get('TINYDB_PATH', DEFAULT_DB_FILE_PATH)

# Ensure the directory for the DB file exists.
# This will create the 'db' folder if running locally and it doesn't exist.
# For Azure, it ensures the mounted path's directory exists (though the mount itself ensures the top-level path).
db_directory = os.path.dirname(DB_PATH)
if not os.path.exists(db_directory):
    os.makedirs(db_directory, exist_ok=True) # exist_ok=True prevents error if dir already exists

# Initialize TinyDB with the determined path
db = TinyDB(DB_PATH)

# --- Initial Data Population Logic (Crucial for TinyDB on persistent storage) ---
# This logic will run on every app startup.
# It checks if the database is empty and populates it if so.
# This ensures data exists on the *persistent* storage even after redeployments.

# Define your exercise data as a Python list of dictionaries
INITIAL_EXERCISE_DATA = [
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
]

# Populate database only if it's empty
if len(db) == 0:
    print(f"Database is empty at {DB_PATH}, populating with initial data...")
    db.insert_multiple(INITIAL_EXERCISE_DATA)
    print("Initial data population complete.")
else:
    print(f"Database at {DB_PATH} already contains data, skipping initial population.")


EXERCISE_TYPES = ["strength", "cardio", "recovery", "stability", "circuit", "anaerobic", "flexibility"]
SPORTS = ["swimming", "running", "biking", "yoga"]
MUSCLE_TARGETS = ["shoulder", "upper body", "upper back", "chest", "triceps", "core", "full body", "legs", "glutes"]


@app.route('/')
def index():
    return render_template('index.html',
                           exercise_types=EXERCISE_TYPES,
                           sports=SPORTS,
                           muscle_targets=MUSCLE_TARGETS)

@app.route('/generate_workout', methods=['POST'])
def generate_workout():
    data = request.get_json()
    selected_types = data.get('selected_types', [])
    selected_sports = data.get('selected_sports', [])
    selected_muscle_targets = data.get('selected_muscle_targets', [])

    Exercise = Query()
    all_conditions = []

    # Build OR'd condition for exercise types
    type_query = None
    if selected_types:
        for t in selected_types:
            if type_query is None:
                type_query = Exercise.types.any(t)
            else:
                type_query |= Exercise.types.any(t)
        if type_query:
            all_conditions.append(type_query)

    # Build OR'd condition for sports
    sport_query = None
    if selected_sports:
        for s in selected_sports:
            if sport_query is None:
                sport_query = Exercise.sports.any(s)
            else:
                sport_query |= Exercise.sports.any(s)
        if sport_query:
            all_conditions.append(sport_query)

    # Build OR'd condition for muscle targets
    muscle_query = None
    if selected_muscle_targets:
        for m in selected_muscle_targets:
            if muscle_query is None:
                muscle_query = Exercise.muscle_targets.any(m)
            else:
                muscle_query |= Exercise.muscle_targets.any(m)
        if muscle_query:
            all_conditions.append(muscle_query)

    # If no attributes are selected, return a message
    if not all_conditions:
        return jsonify({"workout_plan": [], "message": "Please select at least one attribute to generate a workout."})

    # Combine all individual category conditions with a logical AND
    final_query = all_conditions[0]
    for cond in all_conditions[1:]:
        final_query &= cond

    # Perform the search
    matching_exercises = db.search(final_query)

    # If too many exercises are found, select a random subset
    num_exercises_to_select = min(len(matching_exercises), 5)

    if num_exercises_to_select > 0:
        workout_plan = random.sample(matching_exercises, num_exercises_to_select)
    else:
        workout_plan = []

    if not workout_plan:
        return jsonify({"workout_plan": [], "message": "No exercises found matching your criteria. Try different selections!"})

    return jsonify({"workout_plan": workout_plan})

if __name__ == '__main__':
    # When running locally, the DB_PATH will be a local file.
    # The initial population logic above handles seeding.
    app.run(debug=True)