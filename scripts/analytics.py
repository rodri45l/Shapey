"""
Gym Tracker Analytics (Enhanced)
Comprehensive analysis: workouts, weight, strength, and recomposition
"""

import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


def load_workouts(filepath='data/workouts.csv'):
    """Load workout data from CSV"""
    try:
        df = pd.read_csv(filepath)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except FileNotFoundError:
        return None


def load_measurements(filepath='data/measurements.csv'):
    """Load body measurements from CSV"""
    try:
        df = pd.read_csv(filepath)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except FileNotFoundError:
        return None


def load_progressions(filepath='data/exercise_progressions.json'):
    """Load exercise progressions"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def total_workouts(workouts_df):
    """Get total number of workouts"""
    if workouts_df is None or workouts_df.empty:
        return 0
    return len(workouts_df.groupby('date'))


def workout_volume(workouts_df):
    """Calculate total training volume (sets × reps × weight)"""
    if workouts_df is None or workouts_df.empty:
        return 0

    try:
        workouts_df['volume'] = (
            pd.to_numeric(workouts_df.get('sets', 0), errors='coerce') *
            pd.to_numeric(workouts_df.get('reps', 0), errors='coerce') *
            pd.to_numeric(workouts_df.get('weight', 0), errors='coerce')
        )
        return workouts_df['volume'].sum()
    except:
        return 0


def weight_progress(measurements_df):
    """Show weight progress"""
    if measurements_df is None or measurements_df.empty:
        return None

    first_weight = measurements_df.iloc[0]['weight_kg']
    latest_weight = measurements_df.iloc[-1]['weight_kg']
    change = latest_weight - first_weight

    return {
        'start': first_weight,
        'current': latest_weight,
        'change': change
    }


def recomposition_status(measurements_df):
    """Analyze recomposition (weight vs measurements)"""
    if measurements_df is None or measurements_df.empty:
        return None

    if len(measurements_df) < 2:
        return None

    try:
        first = measurements_df.iloc[0]
        latest = measurements_df.iloc[-1]

        status = {
            'weight_change_kg': float(latest['weight_kg']) - float(first['weight_kg']),
            'start_weight': float(first['weight_kg']),
            'current_weight': float(latest['weight_kg']),
        }

        # Measurements
        for measurement in ['waist_cm', 'chest_cm', 'arms_cm', 'thighs_cm']:
            if measurement in measurements_df.columns:
                if pd.notna(first[measurement]) and pd.notna(latest[measurement]):
                    try:
                        status[f'{measurement}_change'] = (
                            float(latest[measurement]) - float(first[measurement])
                        )
                    except (ValueError, TypeError):
                        pass

        return status
    except:
        return None


def strength_progress(progressions_data):
    """Get strength progress summary"""
    if not progressions_data or 'exercises' not in progressions_data:
        return []

    progress = []
    for name, exercise in progressions_data['exercises'].items():
        try:
            pr = exercise['all_time_pr']
            progress.append({
                'exercise': exercise['display_name'],
                'max_weight': pr['weight_kg'],
                'max_reps': pr['reps'],
                'next_target': exercise['progression_tracking']['next_suggested_weight_kg']
            })
        except KeyError:
            continue

    return sorted(progress, key=lambda x: x['max_weight'], reverse=True)


def display_weekly_summary(days=7):
    """Display comprehensive weekly summary"""
    workouts = load_workouts()
    measurements = load_measurements()
    progressions = load_progressions()

    print("\n")
    print("╔═══════════════════════════════════════════════════════════╗")
    print(f"║           WEEKLY SUMMARY (Last {days} Days)              ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")

    # WORKOUTS
    if workouts is not None and not workouts.empty:
        recent_workouts = workouts[workouts['date'] >= datetime.now() - timedelta(days=days)]
        print(f"TRAINING:")
        print("─" * 60)
        print(f"  Total Sessions: {len(recent_workouts.groupby('date'))}")
        print(f"  Total Exercises: {len(recent_workouts)}")
        print()

    # WEIGHT
    if measurements is not None and not measurements.empty:
        weight = weight_progress(measurements)
        print(f"WEIGHT:")
        print("─" * 60)
        print(f"  Current: {weight['current']:.1f}kg ({weight['change']:+.1f}kg total)")

        recent_weight = measurements[measurements['date'] >= datetime.now() - timedelta(days=days)]
        if len(recent_weight) > 1:
            weekly_change = float(recent_weight.iloc[-1]['weight_kg']) - float(recent_weight.iloc[0]['weight_kg'])
            print(f"  This Week: {weekly_change:+.1f}kg")
        print()

    # RECOMPOSITION
    if measurements is not None and not measurements.empty:
        recomp = recomposition_status(measurements)
        if recomp:
            print(f"RECOMPOSITION:")
            print("─" * 60)

            has_measurements = False
            for key in ['waist_cm', 'chest_cm', 'arms_cm', 'thighs_cm']:
                if f'{key}_change' in recomp:
                    change = recomp[f'{key}_change']
                    label = key.replace('_', ' ').title()
                    arrow = "↓" if change < 0 else "↑" if change > 0 else "→"
                    print(f"  {label:.<30} {change:+.1f}cm {arrow}")
                    has_measurements = True

            if not has_measurements:
                print("  (No measurement data - add with --log command)")
            print()

    # STRENGTH
    if progressions:
        strength = strength_progress(progressions)
        if strength:
            print(f"TOP LIFTS:")
            print("─" * 60)
            for lift in strength[:5]:
                print(f"  {lift['exercise']:.<20} {lift['max_weight']:.1f}kg x{lift['max_reps']} " +
                      f"(→ {lift['next_target']:.1f}kg)")
        print()


def display_full_report():
    """Display full analytics report"""
    workouts = load_workouts()
    measurements = load_measurements()
    progressions = load_progressions()

    print("\n")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║             FULL GYM TRACKER ANALYTICS                   ║")
    print("╚═══════════════════════════════════════════════════════════╝\n")

    # Summary
    print(f"Total Workouts: {total_workouts(workouts)}")
    print()

    # Weight
    if measurements is not None:
        weight = weight_progress(measurements)
        if weight:
            print("Weight Progress:")
            print(f"  Starting: {weight['start']:.1f} kg")
            print(f"  Current:  {weight['current']:.1f} kg")
            print(f"  Change:   {weight['change']:+.1f} kg")
            print()

    # Strength
    if progressions:
        strength = strength_progress(progressions)
        if strength:
            print("Strength Progress (Top 5):")
            for lift in strength[:5]:
                print(f"  {lift['exercise']:.<25} {lift['max_weight']:>6.1f}kg x{lift['max_reps']}")
            print()

    display_weekly_summary(days=7)


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Gym Tracker Analytics')
    parser.add_argument('--full', action='store_true', help='Show full report')
    parser.add_argument('--week', action='store_true', help='Show weekly summary (default)')
    parser.add_argument('--days', type=int, default=7, help='Days to analyze for weekly')

    args = parser.parse_args()

    if args.full:
        display_full_report()
    else:
        display_weekly_summary(args.days)


if __name__ == '__main__':
    main()
