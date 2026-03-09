import azure.functions as func
import json
import logging
from reportlab.pdfgen import canvas
from io import BytesIO

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="generate_pdf", methods=["POST", "OPTIONS"])
def generate_pdf(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('PDF Generation request received.')

    # 1. Handle the browser "Pre-flight" OPTIONS request
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )

    try:
        req_body = req.get_json()
        workout_plan = req_body.get('workout_plan', [])

        # 2. PDF Generation Logic
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 800, "Workout Wizard: Your Plan")
        
        y = 770
        p.setFont("Helvetica", 12)
        for exercise in workout_plan:
            p.drawString(100, y, f"• {exercise.get('name', 'Exercise')}")
            y -= 20
            if y < 50:
                p.showPage()
                y = 800
        
        p.save()
        buffer.seek(0)

        # 3. Return the PDF with CORS headers
        return func.HttpResponse(
            buffer.read(),
            mimetype="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=workout.pdf",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST"
            }
        )

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)