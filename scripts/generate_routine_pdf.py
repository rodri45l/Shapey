"""
Generate a PDF of the weekly gym routine from routine.json (Enhanced)
Now includes: Macros, Strength Progression, Body Metrics
"""

import json
import csv
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


def load_progressions(filepath='data/exercise_progressions.json'):
    """Load exercise progressions"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def load_latest_measurements(filepath='data/measurements.csv'):
    """Load latest measurements"""
    try:
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            return rows[-1] if rows else None
    except FileNotFoundError:
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
        # Handle both old and new format
        protein = session.get('protein_intake_grams', session.get('nutrition', {}).get('protein_g', '—'))

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

        # Display protocol if available
        if running.get('protocol'):
            content.append(Paragraph(
                f"Protocol: {running['protocol']}",
                styles['normal']
            ))

        # Display old format if available
        if running.get('distance_km') and running.get('pace_kmh'):
            content.append(Paragraph(
                f"Distance: {running['distance_km']} km | Pace: {running['pace_kmh']} km/h",
                styles['normal']
            ))

        # Display modality if available
        if running.get('modality'):
            content.append(Paragraph(
                f"Modality: {running['modality']}",
                styles['normal']
            ))

        if running.get('notes'):
            content.append(Paragraph(
                f"Notes: {running['notes']}",
                styles['normal']
            ))

        content.append(Spacer(1, 0.2*inch))

    # Nutrition targets
    nutrition = session.get('nutrition', {})
    protein = nutrition.get('protein_g', 209)
    carbs = nutrition.get('carbs_g', 332)
    fats = nutrition.get('fats_g', 95)

    content.append(Paragraph("🍗 Nutrition Targets", styles['section']))
    content.append(Paragraph(
        f"Protein: {protein}g | Carbs: {carbs}g | Fats: {fats}g",
        styles['normal']
    ))

    if nutrition.get('notes'):
        content.append(Paragraph(
            f"Note: {nutrition['notes']}",
            styles['normal']
        ))

    return content


def create_macro_section(routine_data, styles):
    """Create macro targets section"""
    content = []

    content.append(Paragraph("🥗 Daily Macro Targets", styles['section']))
    content.append(Spacer(1, 0.1*inch))

    days = list(routine_data['weekly_routine'].keys())
    macro_data = [['Day', 'Protein', 'Carbs', 'Fats', 'Calories']]

    for day in days:
        session = routine_data['weekly_routine'][day]
        nutrition = session.get('nutrition', {})
        protein = nutrition.get('protein_g', 209)
        carbs = nutrition.get('carbs_g', 332)
        fats = nutrition.get('fats_g', 95)
        day_type = 'Gym' if session['gym_session']['enabled'] else 'Cardio' if session['running_session']['enabled'] else 'Rest'

        macro_data.append([
            day,
            f"{protein}g",
            f"{carbs}g",
            f"{fats}g",
            day_type
        ])

    macro_table = Table(macro_data, colWidths=[1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.4*inch])
    macro_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff9500')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffe6cc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff5e6')]),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))

    content.append(macro_table)
    content.append(Spacer(1, 0.15*inch))

    return content


def create_strength_progression_section(progressions, styles):
    """Create strength progression and suggestions"""
    content = []

    content.append(Paragraph("💪 Strength Progression", styles['section']))
    content.append(Spacer(1, 0.1*inch))

    if progressions and 'exercises' in progressions:
        strength_data = [['Exercise', 'Current Max', 'Next Target']]

        for name, exercise in progressions['exercises'].items():
            try:
                current = exercise['current_max']['weight_kg']
                next_target = exercise['progression_tracking']['next_suggested_weight_kg']
                display_name = exercise['display_name']

                strength_data.append([
                    display_name,
                    f"{current} kg",
                    f"{next_target} kg"
                ])
            except KeyError:
                continue

        if len(strength_data) > 1:
            strength_table = Table(strength_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
            strength_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d62728')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffe6e6')),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff0f0')]),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))

            content.append(strength_table)
            content.append(Spacer(1, 0.15*inch))

    return content


def create_measurements_section(measurements, styles):
    """Create body measurements summary"""
    content = []

    content.append(Paragraph("📏 Body Measurements", styles['section']))
    content.append(Spacer(1, 0.1*inch))

    if measurements:
        try:
            meas_data = [
                ['Metric', 'Current'],
                ['Weight', f"{measurements.get('weight_kg', 'N/A')} kg"],
            ]

            if measurements.get('body_fat_percent'):
                meas_data.append(['Body Fat', f"{measurements['body_fat_percent']}%"])

            for key, label in [('waist_cm', 'Waist'), ('chest_cm', 'Chest'), ('arms_cm', 'Arms'), ('thighs_cm', 'Thighs')]:
                if measurements.get(key):
                    meas_data.append([label, f"{measurements[key]} cm"])

            meas_table = Table(meas_data, colWidths=[2*inch, 2*inch])
            meas_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('PADDING', (0, 0), (-1, -1), 8),
            ]))

            content.append(meas_table)
            content.append(Spacer(1, 0.15*inch))

        except Exception as e:
            content.append(Paragraph(f"Error loading measurements: {e}", styles['normal']))

    return content


def create_stats_page(routine_data, progressions, measurements, styles):
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
    """Generate PDF from routine.json (Enhanced)"""

    routine_data = load_routine(input_file)
    if routine_data is None:
        return

    # Load additional data
    progressions = load_progressions()
    measurements = load_latest_measurements()

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

    # Macro targets page
    story.append(Paragraph("Weekly Nutrition Plan", styles['title']))
    story.append(Spacer(1, 0.2*inch))
    story.extend(create_macro_section(routine_data, styles))

    # Strength progression page
    if progressions:
        story.append(Paragraph("Strength Progress", styles['title']))
        story.append(Spacer(1, 0.2*inch))
        story.extend(create_strength_progression_section(progressions, styles))

    # Body measurements page
    if measurements:
        story.append(Paragraph("Body Metrics", styles['title']))
        story.append(Spacer(1, 0.2*inch))
        story.extend(create_measurements_section(measurements, styles))

    story.append(PageBreak())

    # One page per day
    days = list(routine_data['weekly_routine'].keys())
    for day in days:
        session = routine_data['weekly_routine'][day]
        day_content = create_day_page(day, session, routine_data, styles)
        story.extend(day_content)
        story.append(PageBreak())

    # Stats page
    stats_content = create_stats_page(routine_data, progressions, measurements, styles)
    story.extend(stats_content)

    # Build PDF
    doc.build(story)
    print(f"✓ PDF generated successfully: {output_file}")


if __name__ == '__main__':
    generate_pdf()
