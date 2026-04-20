# Gym Tracker

A personal gym routine tracker to monitor your progress, track your current weight, and analyze your fitness data over time.

## Current Training Block

Rugby return-to-play (Inside Centre / #12). Starting point: 177cm, 95kg, ~30% BF.
Priority order: **body recomp → strength retention → rugby-specific conditioning**.

Fixed constraints:

- Mon–Fri midday slots: gym (locked)
- Friday evening: busy most weeks

Current-phase modalities: **gym, plyos, Z2 running, VO2 running**. Sprints/RSA
and contact prep are deferred to a later block.

Weekly layout (see `data/routine.json` for full detail):

| Day | Morning | Midday | Evening |
|-----|---------|--------|---------|
| Mon | Z2 run 45min | Push A | — |
| Tue | Z2 run 30min | Pull A | — |
| Wed | — | Legs | — (recover) |
| Thu | — | Push B | — |
| Fri | — | Plyos + Core | busy |
| Sat | VO2 4x4 run 25min | — | — |
| Sun | — | — | — (full rest) |

## Features

- Track daily workouts and exercises
- Monitor current weight and body metrics
- View analytics and progress reports
- Generate insights from your fitness data

## Directory Structure

```
.
├── data/              # Workout logs and user data (CSV/JSON)
├── scripts/           # Analytics and utility scripts
├── src/               # Source code for the application
├── docs/              # Documentation
├── config/            # Configuration files
├── logs/              # Application logs
├── README.md          # This file
└── .gitignore         # Git ignore file
```

## Getting Started

1. Clone this repository
2. Set up your data directory with initial measurements
3. Run scripts to track your progress

## Scripts

Analytics scripts are located in the `scripts/` directory to help you:
- Analyze workout frequency
- Track weight progress
- Generate progress reports
- Visualize fitness trends

## Data Format

Store your workout data in `data/` directory. Formats supported:
- CSV files for workout logs
- JSON for configuration and metrics

## Usage

Run scripts from the project root:
```bash
python scripts/[script_name].py
```

## License

Personal project
