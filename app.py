import os
import logging
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from azure.monitor.opentelemetry import configure_azure_monitor
from services.workout_service import WorkoutService
from groq import Groq

# 1. Initialize environment and services
load_dotenv()

# Initialize Groq Client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Configure Azure Monitor
app_insights_string = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
if app_insights_string:
    configure_azure_monitor() 

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Flask(__name__)
workout_service = WorkoutService()

# Metadata for UI filters
EXERCISE_TYPES = ["strength", "stability", "recovery", "cardio", "circuit", "anaerobic", "flexibility"]
SPORTS = ["swimming", "running", "biking", "yoga"]
MUSCLE_TARGETS = ["shoulder", "upper body", "upper back", "chest", "triceps", "core", "full body", "legs", "glutes"]

def extract_keywords(prompt):
    prompt_lower = prompt.lower()
    return {
        "types": [t for t in EXERCISE_TYPES if t in prompt_lower],
        "sports": [s for s in SPORTS if s in prompt_lower],
        "muscles": [m for m in MUSCLE_TARGETS if m in prompt_lower]
    }

@app.route('/')
def index():
    return render_template('index.html', 
                           exercise_types=EXERCISE_TYPES, 
                           sports=SPORTS, 
                           muscle_targets=MUSCLE_TARGETS)

@app.route('/generate_ai_workout', methods=['POST'])
def generate_ai_workout():
    data = request.json
    user_prompt = data.get('prompt', '')

    try:
        keywords = extract_keywords(user_prompt)
        context_plan, _ = workout_service.generate_plan(
            selected_types=keywords["types"],
            selected_sports=keywords["sports"],
            selected_muscle_targets=keywords["muscles"]
        )
        
        exercise_context = ", ".join([ex['name'] for ex in context_plan[:10]]) if context_plan else "general exercises"

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system", 
                    "content": f"""You are the Workout Wizard. Use these exercises: {exercise_context}.
                    Rules: Use '## ' for Day Headers, '### ' for Exercise names, and a SINGLE '*' for details. 
                    No double bullets."""
                },
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return jsonify({"success": True, "ai_plan": completion.choices[0].message.content})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/generate_workout', methods=['POST'])
def generate():
    data = request.json
    plan, error = workout_service.generate_plan(
        data.get('selected_types', []), 
        data.get('selected_sports', []), 
        data.get('selected_muscle_targets', [])
    )
    return jsonify({"workout_plan": plan or [], "message": error})

if __name__ == '__main__':
    app.run(debug=True)