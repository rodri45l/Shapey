"""
Generate a PDF of the weekly gym routine from routine.json
"""

import json
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def load_routine(filepath='data/routine.json'):
    """Load routine from JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filepath} not found")
        return None


def create_styles():
    """Create custom styles for the PDF"""
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    day_style = ParagraphStyle(
        'DayTitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=12,
        spaceBefore=12
    )

    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#2ca02c'),
        spaceAfter=8,
        spaceBefore=8
    )

    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=4
    )

    return {
        'title': title_style,
        'day': day_style,
        'section': section_style,
        'normal': normal_style
    }


def create_overview_table(routine):
    """Create overview table of weekly routine"""
    days = list(routine['weekly_routine'].keys())

    data = [['Day', 'Focus', 'Gym', 'Running', 'Protein (g)']]

    for day in days:
        session = routine['weekly_routine'][day]
        gym = '✓' if session['gym_session']['enabled'] else '—'
        running = '✓' if session['running_session']['enabled'] else '—'
        protein = session['protein_intake_grams']

        data.append([
            day,
            session['day_name'],
            gym,
            running,
            str(protein)
        ])

    table = Table(data, colWidths=[1.2*inch, 1.5*inch, 0.8*inch, 0.8*inch, 1*inch])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    return table


def format_exercise(exercise, styles):
    """Format exercise details"""
    weight_str = f" @ {exercise['weight_kg']} kg" if exercise['weight_kg'] != 'bodyweight' else " (bodyweight)"
    text = f"• {exercise['name']}: {exercise['sets']}x{exercise['reps']}{weight_str}"
    return Paragraph(text, styles['normal'])


def create_day_page(day_name, session, routine_data, styles):
    """Create content for a single day page"""
    content = []

    # Day title
    content.append(Paragraph(f"{day_name}", styles['day']))
    content.append(Spacer(1, 0.1*inch))

    # Gym session
    if session['gym_session']['enabled']:
        content.append(Paragraph("💪 Gym Session", styles['section']))
        content.append(Paragraph(
            f"Duration: {session['gym_session']['duration_minutes']} minutes",
            styles['normal']
        ))
        content.append(Spacer(1, 0.1*inch))

        for exercise in session['gym_session']['exercises']:
            content.append(format_exercise(exercise, styles))

        content.append(Spacer(1, 0.2*inch))

    # Running session
    if session['running_session']['enabled']:
        running = session['running_session']
        content.append(Paragraph("🏃 Running Session", styles['section']))
        content.append(Paragraph(
            f"Type: {running['type'].capitalize()} | Duration: {running['duration_minutes']} min",
            styles['normal']
        ))
        content.append(Paragraph(
            f"Distance: {running['distance_km']} km | Pace: {running['pace_kmh']} km/h",
            styles['normal']
        ))
        content.append(Spacer(1, 0.2*inch))

    # Protein intake
    content.append(Paragraph("🍗 Protein Intake", styles['section']))
    content.append(Paragraph(
        f"Target: {session['protein_intake_grams']} grams",
        styles['normal']
    ))

    return content


def create_stats_page(routine_data, styles):
    """Create the stats summary page"""
    stats = routine_data['user_stats']
    content = []

    content.append(Paragraph("📊 Your Stats", styles['title']))
    content.append(Spacer(1, 0.2*inch))

    # Create stats table
    stats_data = [
        ['Metric', 'Value'],
        ['Current Weight', f"{stats['current_weight_kg']} kg"],
        ['Body Fat %', f"{stats['body_fat_percent']}%"],
        ['Resting Heart Rate', f"{stats['resting_heart_rate']} bpm"],
        ['HRV (Heart Rate Variability)', f"{stats['hrv']} ms"],
        ['Last Sleep', f"{stats['last_sleep_hours']} hours"],
        ['Last Updated', stats['last_updated']]
    ]

    stats_table = Table(stats_data, colWidths=[2.5*inch, 2.5*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ca02c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))

    content.append(stats_table)

    return content


def generate_pdf(input_file='data/routine.json', output_file='routine.pdf'):
    """Generate PDF from routine.json"""

    routine_data = load_routine(input_file)
    if routine_data is None:
        return

    # Create PDF
    doc = SimpleDocTemplate(
        output_file,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    styles = create_styles()
    story = []

    # Title page with overview
    story.append(Paragraph("Weekly Gym Routine", styles['title']))
    story.append(Spacer(1, 0.3*inch))
    story.append(create_overview_table(routine_data))
    story.append(PageBreak())

    # One page per day
    days = list(routine_data['weekly_routine'].keys())
    for day in days:
        session = routine_data['weekly_routine'][day]
        day_content = create_day_page(day, session, routine_data, styles)
        story.extend(day_content)
        story.append(PageBreak())

    # Stats page
    stats_content = create_stats_page(routine_data, styles)
    story.extend(stats_content)

    # Build PDF
    doc.build(story)
    print(f"✓ PDF generated successfully: {output_file}")


if __name__ == '__main__':
    generate_pdf()
