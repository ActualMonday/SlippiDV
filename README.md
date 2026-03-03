# SlippiDV

Slippi Data Visualizer (**SlippiDV**) is a local analytics tool for **Super Smash Bros. Melee Slippi replays**.

It parses `.slp` replay files and generates an interactive dashboard showing gameplay statistics such as:

- Win rate
- Damage per stock
- Neutral win rate
- Kill percent distributions
- Opponent statistics
- Time-based performance trends

The application consists of three components:

| Component | Purpose |
|--------|--------|
| **Parser (Node.js)** | Reads `.slp` files and builds a structured match database |
| **Electron App** | Provides a desktop interface to run the parser and launch the dashboard |
| **Bokeh Dashboard (Python)** | Displays interactive statistics and charts |

---

# Features

- Parse thousands of Slippi replay files automatically
- Only processes **new matches** after the first parse
- Interactive statistics dashboard
- Progress tracking while parsing
- Works completely **offline**

---

# Requirements

Users must have:

- Slippi replay files (`.slp`)
- Windows OS (currently tested on Windows)

For developers:

- Node.js
- Python 3.10+
- pip

---

# How It Works

## 1. Electron Launcher

The Electron application provides a GUI to:

- Select your Slippi replay folder
- Enter your Slippi connect code
- Run the parser
- Launch the statistics dashboard

---

## 2. Parser

The parser scans your Slippi replay directory and extracts statistics from each game.

Results are stored locally in a JSON database.

Future parses only process **new replay files**, making updates much faster.

| <img width="978" height="628" alt="image" src="https://github.com/user-attachments/assets/5c59a5b0-9343-43d3-9a19-1a5f4b99a8a3" /> | <img width="979" height="631" alt="ElectronParserApp3_alpha" src="https://github.com/user-attachments/assets/4c9111bc-6524-46a7-ae80-56c35e2fe247" /> |
|--------|--------|

---

## 3. Bokeh Dashboard

The dashboard loads the parsed database and provides interactive visualizations including:

- Time-based performance charts
- Move usage distributions
- Matchup statistics
- Individual opponent tracking

### Overview Tab
![Overview](https://github.com/user-attachments/assets/6717bd26-b4ea-45ad-8b93-468e4626432f)

### Match Up Tab
![Matchup](https://github.com/user-attachments/assets/0cb149e2-d465-4da6-b610-6990698fb5ae)

### Kill/Death Percent Tab
![KillPercent](https://github.com/user-attachments/assets/9aee0015-9e1c-4c29-a26c-581c5ca87bb5)

### More To Come!

I have much more ideas including time-series plots, ranked tab, and depending on the user-base perhaps percentile in the future! The main focus now is getting this shipped with an installer, and prettying up the launcher app :)

---

# Running the Application

## No finalized build just yet (~1 week of alpha testers).

## Using the Desktop App (Recommended)

1. Launch **SlippiDV**
2. Select your **Slippi replay folder**
3. Enter your **Slippi connect code** (example: `MON#864`)
4. Click **Run Parser**
5. Once parsing completes, click **Launch Dashboard**

---

# First Parse vs Later Parses

The **first parse** processes every replay file and may take several minutes depending on your library size.

Example:

| Replay Files | Parse Time |
|-------------|------------|
| 6,000 | ~10 minutes |
| 50,000 | longer |

Future parses are fast because only **new games** are processed.

---

# Repository Structure

```
SlippiDV/
│
├ app/
│  ├ bokeh_app/       # Python dashboard code
│  ├ electron/        # Electron desktop app
│  ├ parser/          # Slippi replay parser
│  └ user_data/       # Generated database (not tracked in git)
│
├ dev/                # Development experiments
├ example_data/       # Small sample datasets
├ screenshots/        # UI screenshots
│
└ README.md
```

---

# Development Setup

## Install parser dependencies

```
cd app/parser
npm install
```

## Install Electron dependencies

```
cd ../electron
npm install
```

## Run Electron app

```
npm start
```

---

# Dashboard Development

Install Python dependencies:

```
pip install -r requirements.txt
```

Run the dashboard:

```
python app/bokeh_app/main.py
```

---

# Data Privacy

All data processing happens **locally**.

SlippiDV does not upload or transmit replay data.

Future updates may change this only to create "percentile" statistics, only of averaged basic stats given enough user interest / sample size.

---

# Alpha Testing Status

SlippiDV is currently in **alpha development**.

Some features and UI elements may change.

Bug reports and feedback are welcome.

---

# Acknowledgements

- Slippi Replay Project
- SlippiJS (`@slippi/slippi-js`)
- Bokeh visualization library
- Electron framework

