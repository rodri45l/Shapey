"""
Strength Progression Tracker
Track exercises and auto-suggest weight increases
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class StrengthProgressionTracker:
    """Track strength gains and suggest progression"""

    def __init__(self, progressions_path='data/exercise_progressions.json'):
        """Initialize with progressions file"""
        self.progressions_path = progressions_path
        self.data = self._load_progressions()

    def _load_progressions(self):
        """Load exercise progressions"""
        try:
            with open(self.progressions_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {self.progressions_path} not found")
            return None

    def _save_progressions(self):
        """Save updated progressions"""
        if not self.data:
            return False
        try:
            with open(self.progressions_path, 'w') as f:
                json.dump(self.data, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving progressions: {e}")
            return False

    def log_exercise(self, exercise_name, weight_kg, reps, session_name=''):
        """Log an exercise attempt"""
        if not self.data or 'exercises' not in self.data:
            print("Error: Invalid progressions data")
            return False

        exercise = self.data['exercises'].get(exercise_name)
        if not exercise:
            print(f"Error: Exercise '{exercise_name}' not found")
            return False

        # Add to history
        exercise['history'].append({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'weight_kg': weight_kg,
            'reps': reps,
            'session_name': session_name
        })

        # Check if new max
        current_max = exercise['current_max']['weight_kg']
        if weight_kg > current_max or (weight_kg == current_max and reps > exercise['current_max']['reps']):
            exercise['current_max'] = {
                'weight_kg': weight_kg,
                'reps': reps,
                'date': datetime.now().strftime('%Y-%m-%d')
            }

            # Check if new all-time PR
            all_time_pr = exercise['all_time_pr']['weight_kg']
            if weight_kg > all_time_pr:
                exercise['all_time_pr'] = exercise['current_max'].copy()
                print(f"🎉 NEW PR! {exercise_name}: {weight_kg}kg × {reps}")

        # Update progression tracking
        self._update_progression_suggestion(exercise_name, exercise)

        self._save_progressions()
        return True

    def _update_progression_suggestion(self, exercise_name, exercise):
        """Update next suggested weight based on reps"""
        current_weight = exercise['current_max']['weight_kg']
        current_reps = exercise['current_max']['reps']
        increment = exercise['progression_tracking']['increase_increment_kg']

        # If hit target reps (5+), suggest next weight
        if current_reps >= 5:
            exercise['progression_tracking']['next_suggested_weight_kg'] = round(current_weight + increment, 1)
        else:
            exercise['progression_tracking']['next_suggested_weight_kg'] = current_weight

        # Update last increase date
        exercise['progression_tracking']['last_increase_date'] = datetime.now().strftime('%Y-%m-%d')
        exercise['progression_tracking']['weeks_since_increase'] = 0

    def check_stalls(self, weeks=4):
        """Check for exercises that haven't progressed in N weeks"""
        if not self.data or 'exercises' not in self.data:
            return []

        stalled = []
        cutoff_date = datetime.now() - timedelta(weeks=weeks)

        for name, exercise in self.data['exercises'].items():
            if not exercise['history']:
                continue

            # Check if recent sessions exist
            recent_history = [h for h in exercise['history']
                            if datetime.strptime(h['date'], '%Y-%m-%d') > cutoff_date]

            if recent_history:
                # Check if weight/reps improved
                recent_max = max(recent_history, key=lambda x: (x['weight_kg'], x['reps']))
                older_sessions = [h for h in exercise['history']
                                if datetime.strptime(h['date'], '%Y-%m-%d') <= cutoff_date]

                if older_sessions:
                    older_max = max(older_sessions, key=lambda x: (x['weight_kg'], x['reps']))
                    if (recent_max['weight_kg'] == older_max['weight_kg'] and
                        recent_max['reps'] == older_max['reps']):
                        stalled.append({
                            'exercise': exercise['display_name'],
                            'weight_kg': recent_max['weight_kg'],
                            'reps': recent_max['reps'],
                            'weeks_stalled': weeks
                        })

        return stalled

    def get_progression_report(self, exercise_name=None):
        """Get progression report for exercise(s)"""
        if not self.data or 'exercises' not in self.data:
            return None

        if exercise_name:
            exercises = {exercise_name: self.data['exercises'][exercise_name]}
        else:
            exercises = self.data['exercises']

        report = []
        for name, exercise in exercises.items():
            report.append({
                'exercise': exercise['display_name'],
                'current_max': exercise['current_max'],
                'all_time_pr': exercise['all_time_pr'],
                'next_suggested': exercise['progression_tracking']['next_suggested_weight_kg'],
                'weeks_at_current': self._calculate_weeks_at_weight(exercise)
            })

        return report

    def _calculate_weeks_at_weight(self, exercise):
        """Calculate how many weeks at current max weight"""
        if not exercise['history']:
            return 0

        current_max_weight = exercise['current_max']['weight_kg']
        sessions_at_weight = sum(1 for h in exercise['history']
                                if h['weight_kg'] == current_max_weight)

        # Rough estimate: ~2-3 sessions per week
        return sessions_at_weight / 2.5

    def display_all_progressions(self):
        """Display all exercises and suggestions"""
        if not self.data or 'exercises' not in self.data:
            print("No progression data found")
            return

        output = "\n"
        output += "╔════════════════════════════════════════════════════════════╗\n"
        output += "║           STRENGTH PROGRESSION & SUGGESTIONS               ║\n"
        output += "╚════════════════════════════════════════════════════════════╝\n"

        for name, exercise in self.data['exercises'].items():
            current = exercise['current_max']
            suggested = exercise['progression_tracking']['next_suggested_weight_kg']
            all_time = exercise['all_time_pr']

            output += f"\n{exercise['display_name'].upper()}\n"
            output += "─" * 60 + "\n"
            output += f"  Current:    {current['weight_kg']}kg × {current['reps']} reps ({current['date']})\n"
            output += f"  All-Time:   {all_time['weight_kg']}kg × {all_time['reps']} reps\n"
            output += f"  Next:       {suggested}kg (↑ {exercise['progression_tracking']['increase_increment_kg']}kg)\n"

            if suggested > current['weight_kg']:
                output += f"  Status:     ✓ READY TO INCREASE\n"
            else:
                output += f"  Status:     → Keep working toward {current['reps']} reps\n"

        print(output)

        # Check for stalls
        stalled = self.check_stalls(weeks=3)
        if stalled:
            print("\n⚠️  STALLED EXERCISES (No progress in 3 weeks):\n")
            for item in stalled:
                print(f"  • {item['exercise']}: {item['weight_kg']}kg × {item['reps']} (consider form check)")

    def get_weekly_progression(self, days_back=7):
        """Get progression from the last N days"""
        if not self.data or 'exercises' not in self.data:
            return None

        cutoff_date = datetime.now() - timedelta(days=days_back)
        weekly_progress = {}

        for name, exercise in self.data['exercises'].items():
            recent = [h for h in exercise['history']
                     if datetime.strptime(h['date'], '%Y-%m-%d') > cutoff_date]
            if recent:
                best = max(recent, key=lambda x: (x['weight_kg'], x['reps']))
                weekly_progress[exercise['display_name']] = best

        return weekly_progress


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Strength Progression Tracker')
    parser.add_argument('--log', nargs=3, metavar=('EXERCISE', 'WEIGHT', 'REPS'),
                        help='Log an exercise: --log bench_press 100 5')
    parser.add_argument('--exercise', help='Show progression for specific exercise')
    parser.add_argument('--all', action='store_true', help='Show all exercises')
    parser.add_argument('--stalls', type=int, default=3, help='Check for stalls (weeks)')
    parser.add_argument('--week', action='store_true', help='Show weekly progression')

    args = parser.parse_args()

    tracker = StrengthProgressionTracker()

    if args.log:
        exercise_name = args.log[0]
        try:
            weight = float(args.log[1])
            reps = int(args.log[2])
            tracker.log_exercise(exercise_name, weight, reps)
            print(f"✓ Logged: {exercise_name} {weight}kg × {reps}")
        except ValueError:
            print("Error: weight must be number, reps must be integer")
            return

    if args.all or not args.exercise:
        tracker.display_all_progressions()

    if args.exercise:
        report = tracker.get_progression_report(args.exercise)
        if report:
            for item in report:
                print(f"\n{item['exercise']}")
                print(f"  Current: {item['current_max']['weight_kg']}kg × {item['current_max']['reps']}")
                print(f"  Next: {item['next_suggested']}kg")

    if args.week:
        weekly = tracker.get_weekly_progression()
        if weekly:
            print("\nLast 7 Days:\n")
            for exercise, session in weekly.items():
                print(f"  {exercise}: {session['weight_kg']}kg × {session['reps']}")


if __name__ == '__main__':
    main()
