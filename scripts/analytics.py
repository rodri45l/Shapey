"""
Gym Tracker Analytics
Analyze workout data and generate progress reports
"""

import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def load_workouts(filepath='data/workouts.csv'):
    """Load workout data from CSV"""
    try:
        df = pd.read_csv(filepath)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except FileNotFoundError:
        print(f"Error: {filepath} not found")
        return None


def load_measurements(filepath='data/measurements.csv'):
    """Load body measurements from CSV"""
    try:
        df = pd.read_csv(filepath)
        df['date'] = pd.to_datetime(df['date'])
        return df
    except FileNotFoundError:
        print(f"Error: {filepath} not found")
        return None


def total_workouts(workouts_df):
    """Get total number of workouts"""
    if workouts_df is None:
        return 0
    return len(workouts_df.groupby('date'))


def weight_progress(measurements_df):
    """Show weight progress"""
    if measurements_df is None or measurements_df.empty:
        print("No measurements data available")
        return

    first_weight = measurements_df.iloc[0]['weight_kg']
    latest_weight = measurements_df.iloc[-1]['weight_kg']
    change = latest_weight - first_weight

    print(f"Weight Progress:")
    print(f"  Starting: {first_weight:.1f} kg")
    print(f"  Current:  {latest_weight:.1f} kg")
    print(f"  Change:   {change:+.1f} kg")


if __name__ == '__main__':
    print("=== Gym Tracker Analytics ===\n")

    workouts = load_workouts()
    measurements = load_measurements()

    if workouts is not None:
        print(f"Total Workouts: {total_workouts(workouts)}")

    print()
    weight_progress(measurements)
