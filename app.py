import os
import logging
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from azure.monitor.opentelemetry import configure_azure_monitor
from services.workout_service import WorkoutService
from groq import Groq
import time

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

    # --- 1. START TIMER ---
    start_time = time.time()

    try:
        # Extract keywords to pull relevant exercises from your DB
        keywords = extract_keywords(user_prompt)
        context_plan, _ = workout_service.generate_plan(
            selected_types=keywords["types"],
            selected_sports=keywords["sports"],
            selected_muscle_targets=keywords["muscles"]
        )
        
        # Pull more exercises from DB to give the AI a better library (increased to 20)
        db_list = [ex['name'] for ex in context_plan] if context_plan else []
        exercise_context = ", ".join(db_list[:20]) if db_list else "General bodyweight and cardio exercises"

        # --- 2. LOG START OF PROCESS ---
        logger.info(f"AI_START: Prompt length: {len(user_prompt)}")

        # In your generate_ai_workout route:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system", 
                    "content": f"""You are the 'Workout Wizard'. Create a structured workout plan.
                    
        DATABASE EXERCISES (PRIORITIZE THESE):
        {exercise_context}

        STRICT FORMATTING RULES:
        1. Use '## ' for Day/Section headers (e.g., ## Day 1: Strength).
        2. Use '### ' for Exercise names (e.g., ### Push-ups).
        3. Use a single dash '- ' for each instruction/detail line beneath an exercise.
        4. Leave ONE blank line between exercises for readability.
        5. NO BOLDING (no **), NO LATEX ($), NO markdown tables.
        6. Use 'x' for multiplication (e.g., 3 x 12)."""
                },
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )

        # --- 3. CALCULATE SPEED AND SEND SUCCESS TO AZURE ---
        duration = time.time() - start_time
        logger.info("AI_Workout_Generated", extra={
            "custom_dimensions": {
                "duration_seconds": duration,
                "prompt_length": len(user_prompt),
                "db_context_size": len(db_list)
            }
        })
                
        ai_plan = completion.choices[0].message.content
        return jsonify({"success": True, "ai_plan": ai_plan})
    except Exception as e:
        # --- 4. SEND FAILURE TO AZURE ---
        logger.error("AI_Workout_Failure", extra={
            "custom_dimensions": {"error_details": str(e)}
        })
        
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