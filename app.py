import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
# Use the folder-based import as discussed
from services.workout_service import WorkoutService

# 1. Initialize environment and services
load_dotenv()
app = Flask(__name__)
workout_service = WorkoutService()

@app.route('/')
def index():
    # These lists repopulate the Exercise Types, Sports, and Muscle Targets in your HTML
    exercise_types = ["strength", "stability", "recovery", "cardio", "circuit", "anaerobic", "flexibility"]
    sports = ["swimming", "running", "biking", "yoga", "none"]
    muscle_targets = ["shoulder", "upper body", "upper back", "chest", "triceps", "core", "full body", "legs", "glutes"]

    return render_template('index.html', 
                           exercise_types=exercise_types, 
                           sports=sports, 
                           muscle_targets=muscle_targets)

@app.route('/generate_workout', methods=['POST'])
def generate():
    # This endpoint matches the fetch() call in your index.html
    data = request.json
    selected_types = data.get('selected_types', [])
    selected_sports = data.get('selected_sports', [])
    selected_muscle_targets = data.get('selected_muscle_targets', [])

    # The service now handles the cloud query via Cosmos SDK
    plan, error = workout_service.generate_plan(
        selected_types, 
        selected_sports, 
        selected_muscle_targets
    )

    if error:
        return jsonify({"message": error}), 400

    return jsonify({"workout_plan": plan})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)