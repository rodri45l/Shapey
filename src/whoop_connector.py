"""
WHOOP Data Connector
Fetch and sync data from WHOOP API
"""

import json
import requests
import os
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class WHOOPConnector:
    """Connector for WHOOP API"""

    def __init__(self, config_path='config/whoop_config.json'):
        """Initialize WHOOP connector with config"""
        self.config = self._load_config(config_path)
        self.access_token = None
        self.user_id = None

    def _load_config(self, config_path):
        """Load configuration from file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {config_path} not found")
            return None
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {config_path}")
            return None

    def _validate_credentials(self):
        """Check if credentials are configured"""
        if not self.config:
            return False

        client_id = self.config['whoop_api'].get('client_id')
        client_secret = self.config['whoop_api'].get('client_secret')

        if client_id == 'YOUR_WHOOP_CLIENT_ID' or client_secret == 'YOUR_WHOOP_CLIENT_SECRET':
            print("\n⚠️  WHOOP credentials not configured!")
            print("To set up WHOOP connector:")
            print("1. Go to https://developer.whoop.com")
            print("2. Create an application and get Client ID & Secret")
            print("3. Update config/whoop_config.json with your credentials")
            print("4. Run this script again\n")
            return False

        return True

    def authenticate(self, access_token=None):
        """Authenticate with WHOOP API"""
        if not self._validate_credentials():
            return False

        if access_token:
            self.access_token = access_token
            print("✓ Using provided access token")
            return self._verify_token()

        print("Authentication required. Visit this URL and authorize:")
        print(self._get_auth_url())
        print("\nAfter authorization, provide the access token using --token flag")
        return False

    def _get_auth_url(self):
        """Get OAuth authorization URL"""
        config = self.config['whoop_api']
        return (f"{config['api_base_url']}/oauth/oauth2/authorize?"
                f"client_id={config['client_id']}&"
                f"scope=read:cycles%20read:recovery%20read:sleep%20read:profile&"
                f"redirect_uri={config['redirect_uri']}&"
                f"response_type=code")

    def _verify_token(self):
        """Verify access token is valid"""
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(
                f"{self.config['whoop_api']['api_base_url']}/api/v4.0/user/profile/basic",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.user_id = data.get('user_id')
                print(f"✓ Authenticated as user: {self.user_id}")
                return True
            else:
                print(f"✗ Authentication failed: {response.status_code}")
                return False

        except requests.RequestException as e:
            print(f"✗ Connection error: {e}")
            return False

    def get_sleep_data(self, days=30):
        """Fetch sleep data for last N days"""
        if not self.access_token:
            print("Error: Not authenticated")
            return None

        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')

            response = requests.get(
                f"{self.config['whoop_api']['api_base_url']}/api/v4.0/user/{self.user_id}/sleep",
                headers=headers,
                params={'start': start_date, 'end': end_date},
                timeout=10
            )

            if response.status_code == 200:
                return response.json().get('records', [])
            else:
                print(f"Error fetching sleep data: {response.status_code}")
                return None

        except requests.RequestException as e:
            print(f"Error fetching sleep data: {e}")
            return None

    def get_recovery_data(self, days=30):
        """Fetch recovery data for last N days"""
        if not self.access_token:
            print("Error: Not authenticated")
            return None

        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')

            response = requests.get(
                f"{self.config['whoop_api']['api_base_url']}/api/v4.0/user/{self.user_id}/recovery",
                headers=headers,
                params={'start': start_date, 'end': end_date},
                timeout=10
            )

            if response.status_code == 200:
                return response.json().get('records', [])
            else:
                print(f"Error fetching recovery data: {response.status_code}")
                return None

        except requests.RequestException as e:
            print(f"Error fetching recovery data: {e}")
            return None

    def get_cycles_data(self, days=30):
        """Fetch cycle data (strain, HRV, RHR) for last N days"""
        if not self.access_token:
            print("Error: Not authenticated")
            return None

        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')

            response = requests.get(
                f"{self.config['whoop_api']['api_base_url']}/api/v4.0/user/{self.user_id}/cycles",
                headers=headers,
                params={'start': start_date, 'end': end_date},
                timeout=10
            )

            if response.status_code == 200:
                return response.json().get('records', [])
            else:
                print(f"Error fetching cycles data: {response.status_code}")
                return None

        except requests.RequestException as e:
            print(f"Error fetching cycles data: {e}")
            return None

    def get_latest_metrics(self):
        """Get latest HRV, RHR, sleep, recovery metrics"""
        metrics = {}

        # Fetch cycles data for HRV and RHR
        cycles = self.get_cycles_data(days=1)
        if cycles and len(cycles) > 0:
            latest_cycle = cycles[0]
            metrics['hrv'] = latest_cycle.get('metrics', {}).get('avg_heart_rate', None)
            metrics['rhr'] = latest_cycle.get('metrics', {}).get('resting_heart_rate', None)
            metrics['strain'] = latest_cycle.get('score', {}).get('strain', None)

        # Fetch sleep data
        sleep = self.get_sleep_data(days=1)
        if sleep and len(sleep) > 0:
            latest_sleep = sleep[0]
            sleep_hours = (latest_sleep.get('end') - latest_sleep.get('start')) / 3600 if 'end' in latest_sleep else None
            metrics['sleep_hours'] = sleep_hours
            metrics['sleep_quality'] = latest_sleep.get('score', {}).get('quality_rating', None)

        # Fetch recovery data
        recovery = self.get_recovery_data(days=1)
        if recovery and len(recovery) > 0:
            latest_recovery = recovery[0]
            metrics['recovery_score'] = latest_recovery.get('score', {}).get('recovery_score', None)

        return metrics

    def save_metrics_to_csv(self, output_path='data/whoop_metrics.csv'):
        """Save latest metrics to CSV"""
        metrics = self.get_latest_metrics()

        if not metrics:
            print("No metrics to save")
            return False

        csv_path = Path(output_path)
        csv_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if file exists to add header
        file_exists = csv_path.exists()
        date_str = datetime.now().strftime('%Y-%m-%d')

        try:
            with open(csv_path, 'a') as f:
                if not file_exists:
                    f.write('date,hrv,rhr,strain,sleep_hours,sleep_quality,recovery_score\n')

                f.write(f"{date_str},{metrics.get('hrv', '')},{metrics.get('rhr', '')}")
                f.write(f",{metrics.get('strain', '')},{metrics.get('sleep_hours', '')}")
                f.write(f",{metrics.get('sleep_quality', '')},{metrics.get('recovery_score', '')}\n")

            print(f"✓ Metrics saved to {output_path}")
            return True

        except IOError as e:
            print(f"Error saving metrics: {e}")
            return False


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='WHOOP Data Connector')
    parser.add_argument('--token', help='WHOOP access token')
    parser.add_argument('--fetch-sleep', action='store_true', help='Fetch sleep data')
    parser.add_argument('--fetch-recovery', action='store_true', help='Fetch recovery data')
    parser.add_argument('--fetch-cycles', action='store_true', help='Fetch cycles data')
    parser.add_argument('--latest', action='store_true', help='Get latest metrics')
    parser.add_argument('--save', action='store_true', help='Save metrics to CSV')
    parser.add_argument('--days', type=int, default=30, help='Number of days to fetch')

    args = parser.parse_args()

    connector = WHOOPConnector()

    if not connector.authenticate(args.token):
        print("Failed to authenticate with WHOOP")
        return

    if args.latest:
        metrics = connector.get_latest_metrics()
        print("\nLatest Metrics:")
        for key, value in metrics.items():
            print(f"  {key}: {value}")

    if args.save:
        connector.save_metrics_to_csv()

    if args.fetch_sleep:
        sleep_data = connector.get_sleep_data(args.days)
        if sleep_data:
            print(f"\nFetched {len(sleep_data)} sleep records")

    if args.fetch_recovery:
        recovery_data = connector.get_recovery_data(args.days)
        if recovery_data:
            print(f"\nFetched {len(recovery_data)} recovery records")

    if args.fetch_cycles:
        cycles_data = connector.get_cycles_data(args.days)
        if cycles_data:
            print(f"\nFetched {len(cycles_data)} cycle records")


if __name__ == '__main__':
    main()
