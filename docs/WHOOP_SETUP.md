# WHOOP Data Connector Setup Guide

This guide will help you set up the WHOOP connector to automatically sync your fitness data.

## Prerequisites

- WHOOP account and wearable
- Internet connection
- Python 3.7+

## Step 1: Create WHOOP Developer Application

1. Go to [WHOOP Developer Portal](https://developer.whoop.com)
2. Sign in with your WHOOP account
3. Create a new application
4. Fill in the application details:
   - **App Name**: Gym Tracker
   - **Description**: Personal gym and fitness tracker
   - **Redirect URI**: `http://localhost:8000/callback`
5. Copy your **Client ID** and **Client Secret**

## Step 2: Configure Credentials

1. Open `config/whoop_config.json`
2. Replace the placeholders:
   ```json
   "client_id": "YOUR_WHOOP_CLIENT_ID",      // <- Replace with your Client ID
   "client_secret": "YOUR_WHOOP_CLIENT_SECRET" // <- Replace with your Client Secret
   ```
3. Save the file

## Step 3: Get Access Token

Run the connector to get your authorization URL:

```bash
python src/whoop_connector.py --latest
```

You'll see a URL. Copy and paste it into your browser, then authorize the application.

After authorization, you'll be redirected with an access code. Extract the token from the callback URL.

## Step 4: Use the Connector

### Get Latest Metrics
```bash
python src/whoop_connector.py --token YOUR_ACCESS_TOKEN --latest
```

### Save Metrics to CSV
```bash
python src/whoop_connector.py --token YOUR_ACCESS_TOKEN --save
```

### Fetch Specific Data
```bash
# Fetch sleep data
python src/whoop_connector.py --token YOUR_ACCESS_TOKEN --fetch-sleep --days 30

# Fetch recovery data
python src/whoop_connector.py --token YOUR_ACCESS_TOKEN --fetch-recovery --days 30

# Fetch cycles data (strain, HRV, RHR)
python src/whoop_connector.py --token YOUR_ACCESS_TOKEN --fetch-cycles --days 30
```

## Data Synced

The connector syncs the following metrics:

- **HRV** (Heart Rate Variability): Indicates nervous system balance
- **RHR** (Resting Heart Rate): Your baseline heart rate
- **Strain**: Daily exertion score
- **Sleep**: Hours and quality rating
- **Recovery**: Recovery score based on HRV, RHR, and sleep
- **Sleep Quality**: Sleep efficiency and restorative rating

## Metrics Output Format

When saved to CSV (`data/whoop_metrics.csv`):

```
date,hrv,rhr,strain,sleep_hours,sleep_quality,recovery_score
2026-04-19,45,62,8.2,7.5,0.85,72
```

## Environment Variable (Optional)

Instead of passing `--token` each time, you can set an environment variable:

```bash
export WHOOP_ACCESS_TOKEN="your_token_here"
python src/whoop_connector.py --latest
```

## Troubleshooting

### "WHOOP credentials not configured"
- Make sure you've updated `config/whoop_config.json` with your actual credentials

### "Authentication failed"
- Verify your Client ID and Client Secret are correct
- Check your internet connection

### "Connection error"
- Ensure you're connected to the internet
- WHOOP API might be temporarily unavailable

## API Rate Limits

WHOOP API has rate limits:
- 600 requests per hour for development accounts
- 6000 requests per hour for production accounts

Fetching 30 days of data uses approximately 3-4 requests.

## Data Privacy

All your data is stored locally. The connector only sends authorized requests to WHOOP's API using your access token.

---

For more information, visit [WHOOP API Documentation](https://developer.whoop.com/docs)
