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
            # Fallback for raw string bodies
            req_body = json.loads(req.get_body().decode('utf-8'))

        # 2. Robust check: ensure req_body is a dictionary, not a double-encoded string
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

        # PDF Styling and Content
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, height - 50, f"Workout Plan: {workout_plan.get('title', 'My Workout')}")
        
        p.setFont("Helvetica", 12)
        y_position = height - 80
        
        exercises = workout_plan.get('exercises', [])
        for ex in exercises:
            line = f"- {ex.get('name')}: {ex.get('sets')} sets x {ex.get('reps')} reps"
            p.drawString(100, y_position, line)
            y_position -= 20
            if y_position < 50:  # Simple page break logic
                p.showPage()
                y_position = height - 50

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