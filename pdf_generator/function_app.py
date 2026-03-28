import azure.functions as func
import logging
import json
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="generate_pdf", methods=["POST"])
def generate_pdf(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing PDF generation request.')

    try:
        req_body = req.get_json()
        if isinstance(req_body, str):
            req_body = json.loads(req_body)

        workout_plan = req_body.get('workout_plan', {})
        exercises = workout_plan.get('exercises', [])
        title_text = workout_plan.get('title', 'Your Workout Plan')

        buffer = io.BytesIO()
        # Use SimpleDocTemplate for automatic layout/margins
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        styles = getSampleStyleSheet()
        
        # Custom Styles
        title_style = styles['Heading1']
        title_style.alignment = 1  # Center
        
        item_style = ParagraphStyle(
            'ItemStyle',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            spaceAfter=10
        )

        elements = []
        
        # Add Title
        elements.append(Paragraph(f"<b>{title_text}</b>", title_style))
        elements.append(Spacer(1, 24))

        for ex in exercises:
            name = ex.get('name', '').strip()
            sets = str(ex.get('sets', '')).strip()
            reps = str(ex.get('reps', '')).strip()
            
            # LOGIC: Only show "sets x reps" if they actually contain numbers/info
            # Otherwise, just print the text (for AI plans)
            if sets and reps and sets != "-" and reps != "-":
                stats = f" — <b>{sets} sets x {reps} reps</b>"
            else:
                stats = ""

            # Build the paragraph string
            # We use <b> tags for bolding inside Paragraphs
            text = f"• <b>{name}</b>{stats}"
            
            # If there is equipment info, add it
            equipment = ex.get('equipment', [])
            if equipment and equipment != ["N/A"] and equipment != ["none"]:
                text += f"<br/><font color='grey' size='9'>Equipment: {', '.join(equipment)}</font>"

            elements.append(Paragraph(text, item_style))
            elements.append(Spacer(1, 6))

        # Build PDF
        doc.build(elements)

        buffer.seek(0)
        return func.HttpResponse(
            buffer.read(),
            mimetype="application/pdf",
            headers={"Content-Disposition": "attachment; filename=workout_plan.pdf"}
        )

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(f"Error generating PDF: {str(e)}", status_code=500)