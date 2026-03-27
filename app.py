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
# Ensure GROQ_API_KEY is set in your .env or Azure Environment Variables
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Configure Azure Monitor for Application Insights
app_insights_string = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
if app_insights_string:
    configure_azure_monitor() 
else:
    print("Warning: APPLICATIONINSIGHTS_CONNECTION_STRING not found. Azure Monitor disabled.")

# 2. Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Flask(__name__)
workout_service = WorkoutService()

# Constants for Keyword Extraction based on your database schema
EXERCISE_TYPES = ["strength", "stability", "recovery", "cardio", "circuit", "anaerobic", "flexibility"]
SPORTS = ["swimming", "running", "biking", "yoga"]
MUSCLE_TARGETS = ["shoulder", "upper body", "upper back", "chest", "triceps", "core", "full body", "legs", "glutes"]

def extract_keywords(prompt):
    """
    Phase 3 Logic: Scans the user's natural language input to match 
    categories in the workout database.
    """
    prompt_lower = prompt.lower()
    found_types = [t for t in EXERCISE_TYPES if t in prompt_lower]
    found_sports = [s for s in SPORTS if s in prompt_lower]
    found_muscles = [m for m in MUSCLE_TARGETS if m in prompt_lower]
    
    # Safety Guardrail: If user mentions pain/injury, prioritize recovery exercises
    if any(word in prompt_lower for word in ["pain", "hurt", "sore", "injury"]):
        if "recovery" not in found_types:
            found_types.append("recovery")
            
    return found_types, found_sports, found_muscles

@app.route('/')
def index():
    # Lists used to populate the manual filter UI
    exercise_types = EXERCISE_TYPES
    sports = SPORTS + ["none"]
    muscle_targets = MUSCLE_TARGETS

    return render_template('index.html', 
                           exercise_types=exercise_types, 
                           sports=sports, 
                           muscle_targets=muscle_targets)

@app.route('/generate_ai_workout', methods=['POST'])
def generate_ai_workout():
    """
    Phase 3: AI Synthesis Engine (RAG Implementation)
    Retrieves real exercises from the DB and feeds them to the AI.
    """
    data = request.json
    user_prompt = data.get('prompt', "")

    if not user_prompt:
        return jsonify({"success": False, "error": "No prompt provided"}), 400

    try:
        # 1. RETRIEVAL: Match user keywords to database categories
        f_types, f_sports, f_muscles = extract_keywords(user_prompt)
        
        # Query the WorkoutService (CosmosDB) for approved exercises
        approved_exercises, error = workout_service.generate_plan(f_types, f_sports, f_muscles)

        # 2. AUGMENTATION: Build the context for the AI
        if approved_exercises:
            exercise_context = "Use ONLY these approved exercises from our database:\n"
            exercise_context += "\n".join([
                f"- {ex['name']} (Equipment: {', '.join(ex['equipment'])})" 
                for ex in approved_exercises
            ])
        else:
            # Fallback if no specific matches are found in the database
            exercise_context = "No specific database matches found. Suggest general safe movements."

        # 3. GENERATION: Call Groq with the contextualized prompt
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system", 
                    "content": f"""You are the Workout Wizard AI. 
                    Use ONLY these exercises: {exercise_context}
                    
                    STRICT FORMATTING RULES:
                    1. Use '## Day Name' for main day headers (e.g., ## Monday: Endurance).
                    2. Use '### Exercise Name' for specific exercises.
                    3. ALWAYS use bolding for **Warm-up** and **Cool-down**.
                    4. Each instruction MUST be a separate bullet point starting with '- '.
                    5. Do not add extra empty lines between an exercise title and its first bullet.
                    """
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
    """Manual filter workout generation (Standard Phase 2 logic)"""
    data = request.json
    selected_types = data.get('selected_types', [])
    selected_sports = data.get('selected_sports', [])
    selected_muscle_targets = data.get('selected_muscle_targets', [])

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