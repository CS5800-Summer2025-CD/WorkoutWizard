import azure.functions as func
import logging
import json
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="generate_pdf", methods=["POST"])
def generate_pdf(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processing a PDF generation request.')

    try:
        # 1. Attempt to extract the JSON body
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = json.loads(req.get_body().decode('utf-8'))

        # 2. Robust check for double-encoded strings
        if isinstance(req_body, str):
            req_body = json.loads(req_body)

        # 3. Extract workout data
        workout_plan = req_body.get('workout_plan')
        if not workout_plan:
            return func.HttpResponse("Error: No workout_plan found in request body.", status_code=400)

        # 4. Create the PDF in memory
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # PDF Title Styling
        p.setFont("Helvetica-Bold", 16)
        p.drawString(70, height - 50, f"Workout Plan: {workout_plan.get('title', 'My Workout')}")
        
        y_position = height - 80
        exercises = workout_plan.get('exercises', [])

        for ex in exercises:
            name = str(ex.get('name', '')).strip()
            sets = str(ex.get('sets', '')).strip()
            reps = str(ex.get('reps', '')).strip()

            # Determine if this is a structured DB exercise or an AI instruction line
            # If sets/reps are empty or just whitespace, we treat it as an AI text line
            if not sets or sets == "undefined" or not reps or reps == "undefined":
                # AI mode: Print the name and reps as a single descriptive line
                # (The index.html 'chunkText' helper puts the main text in 'reps')
                line = f"{name} {reps}".strip()
                p.setFont("Helvetica", 11)
            else:
                # Manual DB mode: Print standard format
                line = f"- {name}: {sets} sets x {reps} reps"
                p.setFont("Helvetica-Bold", 12)

            # Draw the line
            p.drawString(70, y_position, line)
            y_position -= 20

            # Simple page break logic
            if y_position < 50:
                p.showPage()
                y_position = height - 50
                p.setFont("Helvetica", 11)

        p.showPage()
        p.save()

        # 5. Return the PDF file
        buffer.seek(0)
        return func.HttpResponse(
            buffer.read(),
            mimetype="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=workout_plan.pdf"
            }
        )

    except Exception as e:
        logging.error(f"Error generating PDF: {str(e)}")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)