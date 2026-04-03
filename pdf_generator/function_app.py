import azure.functions as func
import logging
import json
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.colors import HexColor

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="generate_pdf", methods=["POST"])
def generate_pdf(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing professional PDF generation request.')

    try:
        # 1. Parse Request Body
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = json.loads(req.get_body().decode('utf-8'))

        if isinstance(req_body, str):
            req_body = json.loads(req_body)

        workout_plan = req_body.get('workout_plan')
        if not workout_plan:
            return func.HttpResponse("Error: No workout_plan found.", status_code=400)

        # 2. Setup PDF Document
        buffer = io.BytesIO()
        # Margins: 72 points = 1 inch
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter,
            rightMargin=72, 
            leftMargin=72, 
            topMargin=72, 
            bottomMargin=72
        )
        
        # 3. Define Visual Styles
        styles = getSampleStyleSheet()
        
        # Title Style (The "Workout Plan: Title" at the top)
        style_title = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=HexColor("#1e3a8a"), # Navy Blue
            spaceAfter=20
        )

        # Day Header (## Day 1)
        style_day = ParagraphStyle(
            'DayHeader',
            parent=styles['Heading2'],
            fontSize=14,
            fontName='Helvetica-Bold',
            textColor=HexColor("#1e3a8a"),
            spaceBefore=15,
            spaceAfter=8,
            borderPadding=5
        )

        # Exercise Name (### Push-ups)
        style_ex = ParagraphStyle(
            'ExName',
            parent=styles['Normal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            spaceBefore=8,
            spaceAfter=4,
            leading=14
        )

        # Instruction Lines (- Do 3 sets)
        style_instr = ParagraphStyle(
            'Instruction',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            leftIndent=20,       # Indent instructions for better hierarchy
            firstLineIndent=-10, # Hang the bullet/dash slightly
            spaceBefore=2,
            leading=12
        )

        # Standard Text (for lines without markers)
        style_plain = ParagraphStyle(
            'Plain',
            parent=styles['Normal'],
            fontSize=10,
            leading=12,
            spaceBefore=2
        )

        # 4. Build the Content (Story)
        story = []
        
        # Add the Main Title
        title_text = f"Workout Plan: {workout_plan.get('title', 'Wizard Strategy')}"
        story.append(Paragraph(title_text, style_title))

        exercises = workout_plan.get('exercises', [])
        
        for ex in exercises:
            name = str(ex.get('name', '')).strip()
            sets = str(ex.get('sets', '')).strip()
            reps = str(ex.get('reps', '')).strip()

            # --- PARSING LOGIC ---
            
            # 1. Handle Day Headers (##)
            if name.startswith('##'):
                clean_day = name.replace('##', '').strip()
                story.append(Paragraph(clean_day, style_day))
            
            # 2. Handle Exercise Names (###)
            elif name.startswith('###'):
                clean_ex = name.replace('###', '').strip()
                story.append(Paragraph(clean_ex, style_ex))
            
            # 3. Handle Bulleted Instructions (- or *)
            elif name.startswith('- ') or name.startswith('* '):
                # Replace markdown dash with a nice bullet character
                clean_instr = "• " + name[2:].strip()
                story.append(Paragraph(clean_instr, style_instr))
            
            # 4. Handle Structured DB Exercises (manual mode)
            # This covers the case where 'sets' and 'reps' are populated
            elif sets and sets != "undefined" and sets != "AI_MODE":
                db_line_name = f"<b>{name}</b>"
                db_line_stats = f"• {sets} sets x {reps} reps"
                story.append(Paragraph(db_line_name, style_ex))
                story.append(Paragraph(db_line_stats, style_instr))

            # 5. Fallback for any other plain text line
            elif name:
                story.append(Paragraph(name, style_plain))

        # 5. Generate PDF
        doc.build(story)

        # 6. Return response
        buffer.seek(0)
        return func.HttpResponse(
            buffer.read(),
            mimetype="application/pdf",
            headers={"Content-Disposition": "attachment; filename=Workout_Wizard_Plan.pdf"}
        )

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(f"Error generating PDF: {str(e)}", status_code=500)