import azure.functions as func
import logging
import json
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_LEFT

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="generate_pdf", methods=["POST"])
def generate_pdf(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing PDF generation with text wrapping.')

    try:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = json.loads(req.get_body().decode('utf-8'))

        if isinstance(req_body, str):
            req_body = json.loads(req_body)

        workout_plan = req_body.get('workout_plan')
        if not workout_plan:
            return func.HttpResponse("Error: No workout_plan found.", status_code=400)

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Define Styles
        styles = getSampleStyleSheet()
        styleN = styles["Normal"]
        styleN.alignment = TA_LEFT
        styleN.fontSize = 11
        styleN.leading = 14 # Line spacing

        styleB = ParagraphStyle('BoldStyle', parent=styleN, fontName='Helvetica-Bold', fontSize=12, leading=16)

        # Title
        p.setFont("Helvetica-Bold", 16)
        p.drawString(70, height - 50, f"Workout Plan: {workout_plan.get('title', 'My Workout')}")
        
        y_position = height - 80
        margin_x = 70
        max_width = width - 140 # 70 points margin on each side

        for ex in workout_plan.get('exercises', []):
            name = str(ex.get('name', '')).strip()
            sets = str(ex.get('sets', '')).strip()
            reps = str(ex.get('reps', '')).strip()

            # Prepare the text line
            if not sets or sets == "undefined" or not reps or reps == "undefined":
                line_text = name
                current_style = styleN
            else:
                line_text = f"<b>{name}</b>: {sets} sets x {reps} reps"
                current_style = styleB

            # Create a Paragraph object for wrapping
            para = Paragraph(line_text, current_style)
            w, h = para.wrap(max_width, height) # Find out how much space it needs

            # Page break check
            if y_position - h < 50:
                p.showPage()
                y_position = height - 50
                # Re-apply title or header if desired on new pages

            # Draw the wrapped paragraph
            para.drawOn(p, margin_x, y_position - h)
            y_position -= (h + 10) # Move down by height of text plus a small gap

        p.showPage()
        p.save()

        buffer.seek(0)
        return func.HttpResponse(
            buffer.read(),
            mimetype="application/pdf",
            headers={"Content-Disposition": "attachment; filename=workout_plan.pdf"}
        )

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)