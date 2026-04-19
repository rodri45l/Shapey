"""
Body Recomposition Tracker
Track how weight and measurements change - the key to fat loss + muscle gain
"""

import csv
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class RecompositionTracker:
    """Track body recomposition (weight + measurements)"""

    def __init__(self, measurements_path='data/measurements.csv'):
        """Initialize with measurements file"""
        self.measurements_path = measurements_path
        self.data = self._load_measurements()

    def _load_measurements(self):
        """Load measurements from CSV"""
        try:
            with open(self.measurements_path, 'r') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except FileNotFoundError:
            print(f"Error: {self.measurements_path} not found")
            return []

    def log_measurement(self, weight_kg, body_fat_percent=None, waist_cm=None,
                       chest_cm=None, arms_cm=None, thighs_cm=None, notes=''):
        """Log body measurement"""
        try:
            with open(self.measurements_path, 'a') as f:
                writer = csv.DictWriter(f, fieldnames=['date', 'weight_kg', 'weight_lbs',
                                                       'body_fat_percent', 'waist_cm',
                                                       'chest_cm', 'arms_cm', 'thighs_cm', 'notes'])

                weight_lbs = round(weight_kg * 2.20462, 1)
                writer.writerow({
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'weight_kg': weight_kg,
                    'weight_lbs': weight_lbs,
                    'body_fat_percent': body_fat_percent or '',
                    'waist_cm': waist_cm or '',
                    'chest_cm': chest_cm or '',
                    'arms_cm': arms_cm or '',
                    'thighs_cm': thighs_cm or '',
                    'notes': notes
                })

            # Reload data
            self.data = self._load_measurements()
            return True

        except IOError as e:
            print(f"Error logging measurement: {e}")
            return False

    def get_recomposition_summary(self, days_back=30):
        """Get recomposition summary over N days"""
        if not self.data or len(self.data) < 2:
            print("Not enough measurement data")
            return None

        cutoff_date = datetime.now() - timedelta(days=days_back)

        # Filter data
        recent = []
        for row in self.data:
            try:
                row_date = datetime.strptime(row['date'], '%Y-%m-%d')
                if row_date > cutoff_date:
                    recent.append(row)
            except (ValueError, KeyError):
                continue

        if not recent:
            return None

        # Get first and last
        try:
            first = recent[0]
            last = recent[-1]

            summary = {
                'start_date': first['date'],
                'end_date': last['date'],
                'weight_change_kg': round(float(last['weight_kg']) - float(first['weight_kg']), 1),
                'weight_start_kg': float(first['weight_kg']),
                'weight_end_kg': float(last['weight_kg']),
            }

            # Measurements
            for measurement in ['waist_cm', 'chest_cm', 'arms_cm', 'thighs_cm']:
                if first.get(measurement) and last.get(measurement):
                    try:
                        change = round(float(last[measurement]) - float(first[measurement]), 1)
                        summary[f'{measurement}_change'] = change
                        summary[f'{measurement}_start'] = float(first[measurement])
                        summary[f'{measurement}_end'] = float(last[measurement])
                    except (ValueError, TypeError):
                        pass

            # Body fat %
            if first.get('body_fat_percent') and last.get('body_fat_percent'):
                try:
                    change = round(float(last['body_fat_percent']) - float(first['body_fat_percent']), 1)
                    summary['body_fat_change'] = change
                    summary['body_fat_start'] = float(first['body_fat_percent'])
                    summary['body_fat_end'] = float(last['body_fat_percent'])
                except (ValueError, TypeError):
                    pass

            return summary

        except (ValueError, KeyError, IndexError) as e:
            print(f"Error processing measurements: {e}")
            return None

    def is_good_recomposition(self, weight_change_kg, measurements_change):
        """Determine if recomposition is happening (losing fat, gaining muscle)"""
        # Weight stable or slight loss + measurements decreasing = fat loss
        # Weight stable or slight gain + measurements increasing/stable = muscle gain
        # Weight loss + measurements decreasing = good recomposition for fat loss goal

        if not measurements_change:
            return None

        net_measurement_change = sum([v for k, v in measurements_change.items() if 'change' in k])

        if weight_change_kg < -1 and net_measurement_change < 0:
            return "EXCELLENT: Losing weight + losing measurements = fat loss"
        elif weight_change_kg < 0 and net_measurement_change <= 0:
            return "GOOD: Losing weight and maintaining/decreasing measurements"
        elif abs(weight_change_kg) < 1 and net_measurement_change < 0:
            return "GOOD: Weight stable, measurements decreasing = recomposition"
        elif weight_change_kg > 0 and net_measurement_change >= 0:
            return "GOOD: Gaining weight and measurements = muscle + fat gain"
        else:
            return "WATCH: Inconsistent changes, ensure nutrition is on track"

    def display_recomposition_report(self, days_back=30):
        """Display formatted recomposition report"""
        summary = self.get_recomposition_summary(days_back)

        if not summary:
            print("Not enough data for recomposition report")
            return

        output = f"\n"
        output += "╔═══════════════════════════════════════════════════════════╗\n"
        output += "║           BODY RECOMPOSITION REPORT ({} days)          ║\n".format(days_back)
        output += "║                    (Fat Loss + Strength Gain)             ║\n"
        output += "╚═══════════════════════════════════════════════════════════╝\n\n"

        # Weight section
        output += "WEIGHT:\n"
        output += "─" * 60 + "\n"
        output += f"  {summary['weight_start_kg']:.1f}kg → {summary['weight_end_kg']:.1f}kg"
        output += f" ({summary['weight_change_kg']:+.1f}kg)\n\n"

        # Measurements section
        output += "MEASUREMENTS:\n"
        output += "─" * 60 + "\n"

        measurements = {
            'waist_cm': ('Waist (cm)', '↓ indicates fat loss'),
            'chest_cm': ('Chest (cm)', '↑ indicates muscle gain'),
            'arms_cm': ('Arms (cm)', '↑ indicates muscle gain'),
            'thighs_cm': ('Thighs (cm)', '↑ indicates muscle/leg gains'),
        }

        has_measurements = False
        for key, (label, note) in measurements.items():
            if f'{key}_change' in summary:
                start = summary[f'{key}_start']
                end = summary[f'{key}_end']
                change = summary[f'{key}_change']
                has_measurements = True
                arrow = "↑" if change > 0 else "↓" if change < 0 else "→"
                output += f"  {label:.<20} {start:.1f} → {end:.1f} ({change:+.1f}cm) {arrow}\n"

        if not has_measurements:
            output += "  (No measurement data yet - add measurements to track recomposition)\n"

        # Body fat section
        if 'body_fat_change' in summary:
            output += f"\nBODY FAT:\n"
            output += "─" * 60 + "\n"
            output += f"  {summary['body_fat_start']:.1f}% → {summary['body_fat_end']:.1f}%"
            output += f" ({summary['body_fat_change']:+.1f}%)\n"

        # Analysis
        output += f"\nANALYSIS:\n"
        output += "─" * 60 + "\n"

        measurements_change = {k: v for k, v in summary.items() if 'change' in k and k != 'weight_change_kg'}
        status = self.is_good_recomposition(summary['weight_change_kg'], measurements_change)
        if status:
            output += f"  {status}\n"

        output += f"\nRECOMMENDATION:\n"
        output += "─" * 60 + "\n"

        if summary['weight_change_kg'] < -0.5:
            output += "  ✓ Weight loss on track (~0.5kg/week)\n"
        elif summary['weight_change_kg'] > 0.5:
            output += "  → Consider increasing deficit if fat loss is goal\n"
        else:
            output += "  ✓ Weight change is minimal (good for recomposition)\n"

        if summary.get('waist_cm_change', 0) < 0:
            output += "  ✓ Waist decreasing (good fat loss indicator)\n"
        elif summary.get('waist_cm_change', 0) > 0:
            output += "  ⚠️  Waist increasing (check nutrition)\n"

        print(output)

    def get_latest_measurements(self):
        """Get most recent measurements"""
        if not self.data:
            return None

        try:
            latest = self.data[-1]
            return {
                'date': latest['date'],
                'weight_kg': float(latest['weight_kg']),
                'body_fat_percent': float(latest['body_fat_percent']) if latest.get('body_fat_percent') else None,
                'waist_cm': float(latest['waist_cm']) if latest.get('waist_cm') else None,
                'chest_cm': float(latest['chest_cm']) if latest.get('chest_cm') else None,
                'arms_cm': float(latest['arms_cm']) if latest.get('arms_cm') else None,
                'thighs_cm': float(latest['thighs_cm']) if latest.get('thighs_cm') else None,
            }
        except (ValueError, IndexError, KeyError):
            return None


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Body Recomposition Tracker')
    parser.add_argument('--log', type=float, metavar='WEIGHT_KG',
                        help='Log weight: --log 75.0')
    parser.add_argument('--waist', type=float, help='Waist measurement (cm)')
    parser.add_argument('--chest', type=float, help='Chest measurement (cm)')
    parser.add_argument('--arms', type=float, help='Arms measurement (cm)')
    parser.add_argument('--thighs', type=float, help='Thighs measurement (cm)')
    parser.add_argument('--fat', type=float, help='Body fat percentage')
    parser.add_argument('--notes', default='', help='Notes for this entry')
    parser.add_argument('--report', type=int, default=30, help='Days to analyze')
    parser.add_argument('--latest', action='store_true', help='Show latest measurements')

    args = parser.parse_args()

    tracker = RecompositionTracker()

    if args.log:
        tracker.log_measurement(
            weight_kg=args.log,
            waist_cm=args.waist,
            chest_cm=args.chest,
            arms_cm=args.arms,
            thighs_cm=args.thighs,
            body_fat_percent=args.fat,
            notes=args.notes
        )
        print(f"✓ Logged: {args.log}kg")

    if args.latest:
        latest = tracker.get_latest_measurements()
        if latest:
            print(f"\nLatest ({latest['date']}):")
            print(f"  Weight: {latest['weight_kg']}kg")
            if latest['body_fat_percent']:
                print(f"  Body Fat: {latest['body_fat_percent']}%")
            if latest['waist_cm']:
                print(f"  Waist: {latest['waist_cm']}cm")
            if latest['chest_cm']:
                print(f"  Chest: {latest['chest_cm']}cm")
            if latest['arms_cm']:
                print(f"  Arms: {latest['arms_cm']}cm")
            if latest['thighs_cm']:
                print(f"  Thighs: {latest['thighs_cm']}cm")

    if not args.log:
        tracker.display_recomposition_report(args.report)


if __name__ == '__main__':
    main()
