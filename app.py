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
    user_prompt = data.get('prompt', '') # Match the key from index.html

    start_time = time.time()

    try:
        keywords = extract_keywords(user_prompt)
        context_plan, _ = workout_service.generate_plan(
            selected_types=keywords["types"],
            selected_sports=keywords["sports"],
            selected_muscle_targets=keywords["muscles"]
        )
        
        db_list = [ex['name'] for ex in context_plan] if context_plan else []
        exercise_context = ", ".join(db_list[:20]) if db_list else "General bodyweight and cardio exercises"

        logger.info(f"AI_START: Prompt length: {len(user_prompt)}")

        # Use 3.3-70b or 3.1-8b. Both support JSON mode well.
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[
                {
                    "role": "system", 
                    "content": f"""You are the 'Workout Wizard'. You MUST output your response in valid JSON format.
                    
        DATABASE EXERCISES (PRIORITIZE THESE):
        {exercise_context}

        CRITICAL SAFETY RULES:
        1. If the user mentions injury or pain, prioritize 'recovery' or 'stability' exercises.
        2. If a request is dangerous, advise seeing a doctor.

        JSON SCHEMA REQUIREMENT:
        Return a JSON object with:
        1. 'intro_note': A helpful, encouraging introductory message or tip (2-3 sentences).
        2. 'days': An array of days. Each day MUST have at least 5 to 8 exercises. Each day has a 'day_title' and an 'exercises' array.
        3. Each exercise has an 'exercise_name', 'reps_sets', and an 'instructions' array.
        4. 'outro_note': A motivational closing message.
        
        Example:
        {{
            "intro_note": "It sounds like you're feeling a bit drained. Here are a few tips to wake up: stretch and hydrate!",
            "days": [
                {{
                    "day_title": "Day 1: Strength",
                    "exercises": [
                        {{
                            "exercise_name": "Push-ups",
                            "reps_sets": "3 x 12",
                            "instructions": ["Keep your back straight.", "Lower until chest touches ground."]
                        }}
                    ]
                }}
            ],
            "outro_note": "Remember to listen to your body and rest when needed!"
        }}"""
                },
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}, 
            temperature=0.1
        )

        duration = time.time() - start_time
        
        ai_plan = completion.choices[0].message.content.strip()
        
        # Safety Net: Strip markdown formatting if the LLM wraps the JSON
        if ai_plan.startswith("```json"):
            ai_plan = ai_plan[7:]
        elif ai_plan.startswith("```"):
            ai_plan = ai_plan[3:]
        if ai_plan.endswith("```"):
            ai_plan = ai_plan[:-3]
            
        ai_plan = ai_plan.strip()

        return jsonify({"success": True, "ai_plan": ai_plan})
    except Exception as e:
        logger.error("AI_Workout_Failure", extra={"custom_dimensions": {"error_details": str(e)}})
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