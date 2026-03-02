import os
import logging
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from azure.monitor.opentelemetry import configure_azure_monitor
from services.workout_service import WorkoutService

# 1. Initialize environment and services
load_dotenv()

# Check if the connection string exists before trying to configure monitor
app_insights_string = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
if app_insights_string:
    configure_azure_monitor() 
else:
    print("Warning: APPLICATIONINSIGHTS_CONNECTION_STRING not found. Azure Monitor disabled.")

# 2. Setup standard Python logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
    data = request.json
    
    selected_types = data.get('selected_types', [])
    selected_sports = data.get('selected_sports', [])
    selected_muscle_targets = data.get('selected_muscle_targets', [])

    # Log the request
    logger.info(f"Generating workout for: {selected_types}, {selected_sports}, {selected_muscle_targets}")

    # GUARD: If the user didn't select anything, don't query Cosmos DB.
    # This prevents the "fetch all" behavior and returns the message for the UI.
    if not selected_types and not selected_sports and not selected_muscle_targets:
        return jsonify({
            "workout_plan": [],
            "message": "Please select at least one attribute to generate a workout."
        }), 200

    # The service handles the cloud query via Cosmos SDK
    plan, error = workout_service.generate_plan(
        selected_types, 
        selected_sports, 
        selected_muscle_targets
    )

    if error:
        # Note: We return 200 because the "request" worked, there just were no matches.
        return jsonify({
            "workout_plan": [],
            "message": error
        }), 200

    return jsonify({"workout_plan": plan})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)