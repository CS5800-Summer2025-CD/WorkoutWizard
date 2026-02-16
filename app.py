from flask import Flask, render_template, request, jsonify
import os
from services.workout_service import WorkoutService

app = Flask(__name__)

# --- Configuration & Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_DB_DIR = os.path.join(BASE_DIR, 'db')
DEFAULT_DB_FILE_PATH = os.path.join(LOCAL_DB_DIR, 'workout_db.json')
DB_PATH = os.environ.get('TINYDB_PATH', DEFAULT_DB_FILE_PATH)

# Ensure directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# --- Metadata for the Frontend ---
EXERCISE_TYPES = ["strength", "cardio", "recovery", "stability", "circuit", "anaerobic", "flexibility"]
SPORTS = ["swimming", "running", "biking", "yoga"]
MUSCLE_TARGETS = ["shoulder", "upper body", "upper back", "chest", "triceps", "core", "full body", "legs", "glutes"]

# --- Initial Seeding Data ---
INITIAL_EXERCISE_DATA = [
    {
        "name": "Dumbbell Shoulder Press",
        "types": ["strength", "stability"],
        "sports": [],
        "muscle_targets": ["shoulder", "upper body"],
        "equipment": ["dumbbells", "bench"],
        "youtube_link": "https://youtu.be/B-aVuyhvLHU?si=JXXQW6Ij6fthGZP5"
    },
    {
        "name": "Face Pulls",
        "types": ["strength", "recovery", "stability"],
        "sports": [],
        "muscle_targets": ["shoulder", "upper back"],
        "equipment": ["cable machine", "rope attachment"],
        "youtube_link": "https://youtu.be/eFxMixk_qPQ?si=OnxcF7SCVh_1a1q2"
    },
    {
        "name": "Lateral Raises (Shoulder Abduction)",
        "types": ["strength", "recovery"],
        "sports": [],
        "muscle_targets": ["shoulder"],
        "equipment": ["dumbbells"],
        "youtube_link": "https://youtu.be/4p_m96HXMLk?si=q07nzIC1f_cmYs9H"
    },
    {
        "name": "Push-ups",
        "types": ["strength", "circuit", "anaerobic"],
        "sports": [],
        "muscle_targets": ["chest", "shoulder", "triceps", "core"],
        "equipment": ["none"],
        "youtube_link": "https://youtu.be/_l3ySVKYVJ8?si=j1fu62ciG71MfBQ8"
    },
    {
        "name": "Freestyle Swimming (200m)",
        "types": ["cardio"],
        "sports": ["swimming"],
        "muscle_targets": ["full body"],
        "equipment": ["pool"],
        "youtube_link": "https://youtu.be/6_vXycbD2TM?si=FWiMkDJdHq6Deeyw"
    },
    {
        "name": "Freestyle Pull (200m)",
        "types": ["strength", "swimming"],
        "sports": ["swimming"],
        "muscle_targets": ["upper body", "core"],
        "equipment": ["pool", "paddles", "pull buoy"],
        "youtube_link": "https://youtu.be/fcIR3D1_7w4?si=eeRsX6UHNlrmrh11"
    },
    {
        "name": "Medley Order (12 x 50m)",
        "types": ["cardio", "strength", "swimming"],
        "sports": ["swimming"],
        "muscle_targets": ["full body"],
        "equipment": ["pool"],
        "youtube_link": "https://youtu.be/qw-HPBQZlCc?si=LbRpIKFYjhKixB8Z"
    },
    {
        "name": "Sit-ups",
        "types": ["strength", "core"],
        "sports": [],
        "muscle_targets": ["core"],
        "equipment": ["none"],
        "youtube_link": "https://youtu.be/1fbU_MkV7NE?si=lvK_hhVxnbZfgOCL"
    },
    {
        "name": "Crunches",
        "types": ["strength", "core"],
        "sports": [],
        "muscle_targets": ["core"],
        "equipment": ["none"],
        "youtube_link": "https://youtu.be/Xyd_fa5zoEU?si=VXLLRCiMcsVt_2aB"
    },
    {
        "name": "Mountain Climbers",
        "types": ["cardio", "core", "anaerobic"],
        "sports": [],
        "muscle_targets": ["core", "full body"],
        "equipment": ["none"],
        "youtube_link": "https://youtu.be/cnyTQDSE884?si=O2CSSXQ9kfopyngO"
    },
    {
        "name": "Plank (60 seconds)",
        "types": ["strength", "core", "stability"],
        "sports": [],
        "muscle_targets": ["core"],
        "equipment": ["none"],
        "youtube_link": "https://youtu.be/ASdvN_XEl_c?si=LH9sbwGHgXvS-ncy"
    },
    {
        "name": "Squats",
        "types": ["strength", "circuit"],
        "sports": [],
        "muscle_targets": ["legs", "glutes", "core"],
        "equipment": ["none", "barbell", "dumbbells"],
        "youtube_link": "https://youtu.be/xqvCmoLULNY?si=LrAdy9ESHbgj_g2r"
    },
    {
        "name": "Lunges",
        "types": ["strength", "circuit"],
        "sports": [],
        "muscle_targets": ["legs", "glutes"],
        "equipment": ["none", "dumbbells"],
        "youtube_link": "https://youtu.be/wrwwXE_x-pQ?si=QnslQ1K_1tNIfs2p"
    },
    {
        "name": "Running (30 minutes)",
        "types": ["cardio"],
        "sports": ["running"],
        "muscle_targets": ["legs", "full body"],
        "equipment": ["running shoes"],
        "youtube_link": "https://youtu.be/_kGESn8ArrU?si=AjKp86Ybh-tWXHoi"
    },
    {
        "name": "Cycling (45 minutes)",
        "types": ["cardio"],
        "sports": ["biking"],
        "muscle_targets": ["legs", "glutes"],
        "equipment": ["bicycle"],
        "youtube_link": "https://youtu.be/lOVaNLFRLZI?si=x4nX77jtaXWa7DUD"
    },
    {
        "name": "Yoga Flow (30 minutes)",
        "types": ["recovery", "flexibility"],
        "sports": ["yoga"],
        "muscle_targets": ["full body"],
        "equipment": ["yoga mat"],
        "youtube_link": "https://youtu.be/djLCTwi3PmU?si=KHY2gFDWj21YNbGB"
    },
    {
        "name": "Foam Rolling (15 minutes)",
        "types": ["recovery"],
        "sports": [],
        "muscle_targets": ["full body"],
        "equipment": ["foam roller"],
        "youtube_link": "https://youtu.be/c0JRlrKJXPg?si=v94jYT1-_lgCFawz"
    }
]

# Initialize the Service (This handles DB connection and seeding)
workout_service = WorkoutService(DB_PATH, initial_data=INITIAL_EXERCISE_DATA)

@app.route('/')
def index():
    return render_template('index.html',
                           exercise_types=EXERCISE_TYPES,
                           sports=SPORTS,
                           muscle_targets=MUSCLE_TARGETS)

@app.route('/generate_workout', methods=['POST'])
def generate_workout():
    data = request.get_json()
    
    # Use the service to generate the plan
    workout_plan, error_msg = workout_service.generate_plan(
        data.get('selected_types', []),
        data.get('selected_sports', []),
        data.get('selected_muscle_targets', [])
    )

    if error_msg:
        return jsonify({"workout_plan": [], "message": error_msg})

    return jsonify({"workout_plan": workout_plan})

if __name__ == '__main__':
    app.run(debug=True)