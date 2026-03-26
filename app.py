import os
import logging
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from azure.monitor.opentelemetry import configure_azure_monitor
from services.workout_service import WorkoutService
from groq import Groq  # New import for Phase 3

# 1. Initialize environment and services
load_dotenv()

# Initialize Groq Client using the variable name set in Azure/Environment
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

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
    exercise_types = ["strength", "stability", "recovery", "cardio", "circuit", "anaerobic", "flexibility"]
    sports = ["swimming", "running", "biking", "yoga", "none"]
    muscle_targets = ["shoulder", "upper body", "upper back", "chest", "triceps", "core", "full body", "legs", "glutes"]

    return render_template('index.html', 
                           exercise_types=exercise_types, 
                           sports=sports, 
                           muscle_targets=muscle_targets)

# New AI Route for Phase 3
@app.route('/generate_ai_workout', methods=['POST'])
def generate_ai_workout():
    data = request.json
    user_prompt = data.get('prompt')

    if not user_prompt:
        return jsonify({"success": False, "error": "No prompt provided"}), 400

    try:
        # AI Logic: The System prompt provides the "Safety Guardrails" [cite: 55]
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {
                    "role": "system", 
                    "content": "You are the Workout Wizard AI. Create a customized workout plan based on the user's specific constraints (time, injury, equipment). Always provide sets and reps. If a request sounds dangerous or like a medical emergency, advise them to see a doctor."
                },
                {"role": "user", "content": user_prompt}
            ]
        )
        ai_plan = completion.choices[0].message.content
        return jsonify({"success": True, "ai_plan": ai_plan})
    except Exception as e:
        logger.error(f"AI Generation Error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/generate_workout', methods=['POST'])
def generate():
    data = request.json
    selected_types = data.get('selected_types', [])
    selected_sports = data.get('selected_sports', [])
    selected_muscle_targets = data.get('selected_muscle_targets', [])

    logger.info(f"Generating workout for: {selected_types}, {selected_sports}, {selected_muscle_targets}")

    if not selected_types and not selected_sports and not selected_muscle_targets:
        return jsonify({
            "workout_plan": [],
            "message": "Please select at least one attribute to generate a workout."
        }), 200

    plan, error = workout_service.generate_plan(
        selected_types, 
        selected_sports, 
        selected_muscle_targets
    )

    if error:
        return jsonify({
            "workout_plan": [],
            "message": error
        }), 200

    return jsonify({"workout_plan": plan})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)