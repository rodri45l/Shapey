"""
Macro Calculator for Rugby Training
Calculate protein, carbs, and fats based on weight and training goals
"""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class MacroCalculator:
    """Calculate macros for fat loss + strength gain"""

    def __init__(self, config_path='config/config.json'):
        """Initialize with user profile"""
        self.config = self._load_config(config_path)
        self.user = self.config.get('user', {}) if self.config else {}

    def _load_config(self, config_path):
        """Load user config"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Warning: Could not load {config_path}")
            return None

    def calculate_macros(self, weight_kg=None, goal='fat_loss_strength_gain', activity='rugby_training'):
        """
        Calculate daily macro targets

        Args:
            weight_kg: Current body weight in kg (uses config if not provided)
            goal: 'fat_loss_strength_gain' (default), 'strength_focus', 'muscle_gain'
            activity: 'rugby_training' (default), 'light', 'moderate'

        Returns:
            dict with protein, carbs, fats, calories
        """
        if weight_kg is None:
            # Try to get from measurements or config
            weight_kg = self._get_current_weight()

        if not weight_kg:
            print("Error: Weight not found. Provide weight_kg or add to measurements.csv")
            return None

        # Base calculations
        if goal == 'fat_loss_strength_gain':
            # Higher protein for fat loss, enough carbs for training, deficit calories
            protein_g_per_kg = 2.2  # High protein for satiety + muscle retention
            carbs_g_per_kg = 3.5    # Moderate carbs for training (rugby = high intensity)
            fats_g_per_kg = 1.0     # Standard fats (~30% calories)
            calorie_multiplier = 1.4  # Moderate activity (rugby) with deficit
            deficit_cal = 500        # ~500 cal deficit = 0.5kg/week fat loss

        elif goal == 'strength_focus':
            protein_g_per_kg = 2.0
            carbs_g_per_kg = 4.0    # Higher carbs for gym performance
            fats_g_per_kg = 1.0
            calorie_multiplier = 1.5
            deficit_cal = 250        # Smaller deficit to preserve strength

        else:  # muscle_gain
            protein_g_per_kg = 1.8
            carbs_g_per_kg = 4.0
            fats_g_per_kg = 1.1
            calorie_multiplier = 1.6
            deficit_cal = 0          # No deficit for muscle gain

        # Calculate amounts
        protein_g = weight_kg * protein_g_per_kg
        carbs_g = weight_kg * carbs_g_per_kg
        fats_g = weight_kg * fats_g_per_kg

        # Calculate calories
        calories_from_macros = (protein_g * 4) + (carbs_g * 4) + (fats_g * 9)
        calories_with_activity = int(weight_kg * 24 * calorie_multiplier)  # ~24 cal/kg BMR

        # Apply deficit
        final_calories = calories_with_activity - deficit_cal

        return {
            'weight_kg': weight_kg,
            'goal': goal,
            'activity': activity,
            'protein_g': round(protein_g, 1),
            'carbs_g': round(carbs_g, 1),
            'fats_g': round(fats_g, 1),
            'calories': final_calories,
            'calories_breakdown': {
                'protein_cal': round(protein_g * 4, 0),
                'carbs_cal': round(carbs_g * 4, 0),
                'fats_cal': round(fats_g * 9, 0)
            },
            'macro_percentages': {
                'protein_percent': round((protein_g * 4 / final_calories) * 100, 1),
                'carbs_percent': round((carbs_g * 4 / final_calories) * 100, 1),
                'fats_percent': round((fats_g * 9 / final_calories) * 100, 1)
            }
        }

    def adjust_for_activity_day(self, base_macros, day_type='strength'):
        """
        Adjust macros based on training type

        Args:
            base_macros: Output from calculate_macros
            day_type: 'strength', 'cardio', 'mixed', 'rest'

        Returns:
            Adjusted macros dict
        """
        adjusted = base_macros.copy()

        if day_type == 'strength':
            # High carbs for gym
            adjusted['carbs_g'] = base_macros['carbs_g'] * 1.1
            adjusted['protein_g'] = base_macros['protein_g'] * 1.05
            adjusted['calories'] = int(base_macros['calories'] * 1.08)

        elif day_type == 'cardio':
            # Very high carbs for running/rugby drills
            adjusted['carbs_g'] = base_macros['carbs_g'] * 1.25
            adjusted['protein_g'] = base_macros['protein_g']
            adjusted['calories'] = int(base_macros['calories'] * 1.1)

        elif day_type == 'mixed':
            # Moderate increase for gym + cardio day
            adjusted['carbs_g'] = base_macros['carbs_g'] * 1.15
            adjusted['protein_g'] = base_macros['protein_g'] * 1.05
            adjusted['calories'] = int(base_macros['calories'] * 1.09)

        elif day_type == 'rest':
            # Slightly lower on rest days
            adjusted['carbs_g'] = base_macros['carbs_g'] * 0.85
            adjusted['protein_g'] = base_macros['protein_g'] * 1.1  # Maintain protein
            adjusted['calories'] = int(base_macros['calories'] * 0.9)

        # Recalculate percentages
        total_cal = (adjusted['protein_g'] * 4) + (adjusted['carbs_g'] * 4) + (adjusted['fats_g'] * 9)
        adjusted['macro_percentages'] = {
            'protein_percent': round((adjusted['protein_g'] * 4 / total_cal) * 100, 1),
            'carbs_percent': round((adjusted['carbs_g'] * 4 / total_cal) * 100, 1),
            'fats_percent': round((adjusted['fats_g'] * 9 / total_cal) * 100, 1)
        }

        return adjusted

    def _get_current_weight(self):
        """Get most recent weight from measurements.csv"""
        try:
            with open('data/measurements.csv', 'r') as f:
                lines = f.readlines()
                if len(lines) < 2:
                    return None
                # Last line (most recent)
                last_line = lines[-1].strip().split(',')
                return float(last_line[1])  # weight_kg is second column
        except (FileNotFoundError, ValueError, IndexError):
            return None

    def format_output(self, macros):
        """Format macros for display"""
        if not macros:
            return None

        output = f"""
╔════════════════════════════════════════╗
║        MACRO TARGETS (Daily)           ║
╠════════════════════════════════════════╣
║ Goal: {macros['goal'].replace('_', ' ').title():.<32} ║
║ Weight: {macros['weight_kg']:.1f}kg {'':<25} ║
╠════════════════════════════════════════╣
║ PROTEIN:  {macros['protein_g']:>6.1f}g ({macros['macro_percentages']['protein_percent']:>5.1f}%)      ║
║ CARBS:    {macros['carbs_g']:>6.1f}g ({macros['macro_percentages']['carbs_percent']:>5.1f}%)      ║
║ FATS:     {macros['fats_g']:>6.1f}g ({macros['macro_percentages']['fats_percent']:>5.1f}%)      ║
╠════════════════════════════════════════╣
║ TOTAL CALORIES: {macros['calories']:>26} ║
║ Breakdown: {macros['calories_breakdown']['protein_cal']:.0f}P + {macros['calories_breakdown']['carbs_cal']:.0f}C + {macros['calories_breakdown']['fats_cal']:.0f}F ║
╚════════════════════════════════════════╝
"""
        return output


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Macro Calculator for Rugby Training')
    parser.add_argument('--weight', type=float, help='Body weight in kg (auto-detects from measurements.csv if not provided)')
    parser.add_argument('--goal', default='fat_loss_strength_gain',
                        choices=['fat_loss_strength_gain', 'strength_focus', 'muscle_gain'],
                        help='Training goal')
    parser.add_argument('--activity', default='rugby_training',
                        choices=['light', 'moderate', 'rugby_training'],
                        help='Activity level')
    parser.add_argument('--day-type', default='strength',
                        choices=['strength', 'cardio', 'mixed', 'rest'],
                        help='Adjust macros for specific day type')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    calc = MacroCalculator()
    macros = calc.calculate_macros(args.weight, args.goal, args.activity)

    if not macros:
        return

    if args.day_type != 'strength':
        macros = calc.adjust_for_activity_day(macros, args.day_type)

    if args.json:
        print(json.dumps(macros, indent=2))
    else:
        print(calc.format_output(macros))


if __name__ == '__main__':
    main()
