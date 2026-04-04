import azure.functions as func
import logging
import json
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="generate_pdf", methods=["POST"])
def generate_pdf(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing professional PDF generation request.')

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
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter,
            rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72
        )
        
        styles = getSampleStyleSheet()
        
        style_title = ParagraphStyle(
            'TitleStyle', parent=styles['Heading1'], fontSize=18,
            textColor=HexColor("#1e3a8a"), spaceAfter=20
        )

        style_day = ParagraphStyle(
            'DayHeader', parent=styles['Heading2'], fontSize=14,
            fontName='Helvetica-Bold', textColor=HexColor("#1e3a8a"),
            spaceBefore=15, spaceAfter=8
        )

        style_ex = ParagraphStyle(
            'ExName', parent=styles['Normal'], fontSize=11,
            fontName='Helvetica-Bold', spaceBefore=8, spaceAfter=4, leading=14
        )

        style_instr = ParagraphStyle(
            'Instruction', parent=styles['Normal'], fontSize=10,
            fontName='Helvetica', leftIndent=20, firstLineIndent=-10,
            spaceBefore=2, leading=12
        )

        style_plain = ParagraphStyle(
            'Plain', parent=styles['Normal'], fontSize=10, leading=12, spaceBefore=2
        )

        story = []
        
        title_text = f"Workout Plan: {workout_plan.get('title', 'Wizard Strategy')}"
        story.append(Paragraph(title_text, style_title))

        exercises = workout_plan.get('exercises', [])
        
        for ex in exercises:
            name = str(ex.get('name', '')).strip()
            sets = str(ex.get('sets', '')).strip()
            reps = str(ex.get('reps', '')).strip()

            # --- UPDATED PARSING LOGIC ---
            
            # 1. Check for Exercise Names (###) first
            if name.startswith('###'):
                clean_ex = name.lstrip('#').strip() # Removes all # symbols
                story.append(Paragraph(clean_ex, style_ex))
            
            # 2. Check for Day Headers (## or #)
            elif name.startswith('#'):
                clean_day = name.lstrip('#').strip() # Removes all # symbols
                story.append(Paragraph(clean_day, style_day))
            
            # 3. Handle Bulleted Instructions (- or *)
            elif name.startswith('- ') or name.startswith('* '):
                clean_instr = "• " + name[2:].strip()
                story.append(Paragraph(clean_instr, style_instr))
            
            # 4. Handle Structured DB Exercises
            elif sets and sets != "undefined" and sets != "AI_MODE":
                story.append(Paragraph(name, style_ex))
                story.append(Paragraph(f"• {sets} sets x {reps} reps", style_instr))

            # 5. Fallback for plain text
            elif name:
                story.append(Paragraph(name, style_plain))

        doc.build(story)
        buffer.seek(0)
        return func.HttpResponse(
            buffer.read(),
            mimetype="application/pdf",
            headers={"Content-Disposition": "attachment; filename=Workout_Plan.pdf"}
        )

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)