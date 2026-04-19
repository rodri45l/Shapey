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
        # Handle both cardio_session and running_session keys
        cardio_session = session.get('cardio_session') or session.get('running_session')
        cardio = '✓' if cardio_session and cardio_session.get('enabled') else '—'
        # Handle both old and new format
        protein = session.get('protein_intake_grams', session.get('nutrition', {}).get('protein_g', '—'))

        data.append([
            day,
            session['day_name'],
            gym,
            cardio,
            str(protein)
        ])

    table = Table(data, colWidths=[1*inch, 2.5*inch, 0.8*inch, 0.8*inch, 1*inch])

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

    # Cardio session (handles both cardio_session and running_session keys)
    cardio_session = session.get('cardio_session') or session.get('running_session')
    if cardio_session and cardio_session.get('enabled'):
        content.append(Paragraph("🏃 Cardio Session", styles['section']))
        content.append(Paragraph(
            f"Type: {cardio_session['type']} | Duration: {cardio_session['duration_minutes']} min",
            styles['normal']
        ))

        # Display timing if available
        if cardio_session.get('timing'):
            content.append(Paragraph(
                f"Timing: {cardio_session['timing']}",
                styles['normal']
            ))

        # Display protocol if available
        if cardio_session.get('protocol'):
            content.append(Paragraph(
                f"Protocol: {cardio_session['protocol']}",
                styles['normal']
            ))

        # Display modality if available
        if cardio_session.get('modality'):
            content.append(Paragraph(
                f"Modality: {cardio_session['modality']}",
                styles['normal']
            ))

        if cardio_session.get('notes'):
            content.append(Paragraph(
                f"Notes: {cardio_session['notes']}",
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

        # Determine day type
        has_gym = session['gym_session']['enabled']
        cardio_session = session.get('cardio_session') or session.get('running_session')
        has_cardio = cardio_session and cardio_session.get('enabled') if cardio_session else False

        if has_gym and has_cardio:
            day_type = 'Gym+Cardio'
        elif has_gym:
            day_type = 'Gym'
        elif has_cardio:
            day_type = 'Cardio'
        else:
            day_type = 'Rest'

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


def create_analytics_section(styles):
    """Create analytics: body composition, fat loss timeline, weekly projections"""
    content = []

    content.append(Paragraph("📊 Analytics & Progress Tracking", styles['title']))
    content.append(Spacer(1, 0.2*inch))

    # Body Composition Stats
    content.append(Paragraph("Your Current Body Composition (177cm height)", styles['section']))
    content.append(Spacer(1, 0.1*inch))

    comp_data = [
        ['Metric', 'Value', 'Status'],
        ['Weight', '95.0 kg', 'Starting point'],
        ['BMI', '30.3', 'Obese (goal: <25)'],
        ['Body Fat %', '30%', '28.5 kg fat mass'],
        ['Lean Mass', '66.5 kg', 'Target: preserve'],
        ['Daily Deficit', '500 cal', '~0.5kg/week fat loss']
    ]

    comp_table = Table(comp_data, colWidths=[1.8*inch, 1.2*inch, 2.2*inch])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#e6f2ff')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f9ff')]),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))

    content.append(comp_table)
    content.append(Spacer(1, 0.2*inch))

    # Fat Loss Timeline
    content.append(Paragraph("Fat Loss Timeline to Goals", styles['section']))
    content.append(Spacer(1, 0.1*inch))

    timeline_data = [
        ['Target', 'Body Fat %', 'Weight', 'Fat to Lose', 'Timeline', 'Decent Shape?'],
        ['Minimum', '20%', '90kg', '10.5kg', '21 weeks', '✓ Yes'],
        ['Good', '18%', '88kg', '12.7kg', '25 weeks', '✓✓ Yes'],
        ['Excellent', '16%', '85kg', '14.9kg', '30 weeks', '✓✓✓ Yes']
    ]

    timeline_table = Table(timeline_data, colWidths=[1.1*inch, 1.1*inch, 0.9*inch, 1.1*inch, 1.1*inch, 1.2*inch])
    timeline_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ca02c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#e6ffe6')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5fff5')]),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))

    content.append(timeline_table)
    content.append(Spacer(1, 0.2*inch))

    # Weekly Projections
    content.append(Paragraph("Expected Progress by Week", styles['section']))
    content.append(Spacer(1, 0.1*inch))

    projection_data = [
        ['Week', 'Expected Weight', 'Est. Body Fat %', 'Status'],
        ['0 (Now)', '95.0 kg', '30.0%', 'Starting'],
        ['4', '93.0 kg', '29.2%', 'Adjusting'],
        ['8', '91.0 kg', '28.4%', 'Noticing changes'],
        ['12', '89.0 kg', '27.6%', 'Looking leaner'],
        ['16', '87.0 kg', '26.8%', 'Decent shape'],
        ['20', '85.0 kg', '26.0%', 'Good shape'],
        ['24', '83.0 kg', '25.2%', 'Very good shape']
    ]

    projection_table = Table(projection_data, colWidths=[1.2*inch, 1.5*inch, 1.5*inch, 1.8*inch])
    projection_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff9500')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffe6cc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff5e6')]),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))

    content.append(projection_table)
    content.append(Spacer(1, 0.15*inch))

    content.append(Paragraph("Key Note: Assumes 0.5kg/week fat loss, consistent training + nutrition + sleep", styles['normal']))

    return content


def create_fasting_nutrition_section(styles):
    """Create fasting nutrition guide section"""
    content = []

    content.append(Paragraph("🍗 Intermittent Fasting + Protein Protocol", styles['title']))
    content.append(Spacer(1, 0.2*inch))

    content.append(Paragraph("Your Setup", styles['section']))
    setup_text = "210g Protein/Day | 3 Meals (Lunch, Snack, Dinner) | 2 Scoops HSN Clear Whey (Peach)"
    content.append(Paragraph(setup_text, styles['normal']))
    content.append(Spacer(1, 0.15*inch))

    # Daily breakdown
    content.append(Paragraph("Daily Protein Distribution", styles['section']))
    content.append(Spacer(1, 0.1*inch))

    fasting_data = [
        ['Meal', 'Protein', 'Portion', 'Example'],
        ['Lunch', '80g', '280g chicken', 'Breast fillets + rice'],
        ['Snack', '50g', '2 scoops shake', 'HSN Clear Whey'],
        ['Dinner', '100g', '320g beef/salmon', 'Lean meat + potato'],
        ['TOTAL', '230g', '-', '~2000-2100 cal']
    ]

    fasting_table = Table(fasting_data, colWidths=[1.2*inch, 1*inch, 1.3*inch, 1.8*inch])
    fasting_table.setStyle(TableStyle([
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

    content.append(fasting_table)
    content.append(Spacer(1, 0.2*inch))

    # Key tips
    content.append(Paragraph("Success Tips", styles['section']))
    tips = [
        "• <b>Consistency:</b> Same portions every day = easier to hit 210g",
        "• <b>Meal Prep:</b> Cook chicken/meat in batches 3-4x per week",
        "• <b>Timing:</b> Lunch 11am-1pm, Snack 3-4pm, Dinner 7-8pm (example)",
        "• <b>Friday Plyos:</b> Move to afternoon if possible (fasted morning training = muscle loss risk)",
        "• <b>HSN Shake:</b> Mix with water (low cal) or milk (more calories)"
    ]

    for tip in tips:
        content.append(Paragraph(tip, styles['normal']))

    content.append(Spacer(1, 0.15*inch))

    # Shopping list
    content.append(Paragraph("Weekly Shopping", styles['section']))
    shopping_text = "<b>Protein:</b> 1.5-2kg chicken + 1.2-1.5kg beef/salmon | <b>Carbs:</b> Rice, sweet potatoes | <b>Est. Cost:</b> €50-60/month"
    content.append(Paragraph(shopping_text, styles['normal']))

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

    # Fasting Nutrition page
    story.extend(create_fasting_nutrition_section(styles))
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

    # Analytics page
    story.extend(create_analytics_section(styles))
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
