# Formula Tracker 🏎️

A desktop Formula 1 data app built with **Python**, **Tkinter**, **FastF1**, and the **Jolpica F1 API**.

The app lets you load race-weekend data, view race and qualifying results, plot circuit maps, compare driver position changes, inspect tyre strategies, view lap-time distributions, and check WDC/WCC standings.

## Features

- Race results table
- Qualifying results table
- Circuit map visualization
- Driver position changes plot
- Tyre strategy plot
- Team pace comparison
- Lap time distribution plot
- World Drivers' Championship lookup
- World Constructors' Championship lookup

## Project structure

```text
F1-Formula-Tracker/
├── assets/                  # Tkinter button/input images
├── f1_tracker/
│   ├── app.py               # Main Tkinter app controller
│   ├── config.py            # Shared constants and paths
│   ├── services/
│   │   ├── sessions.py      # FastF1 session loading
│   │   └── standings.py     # WDC/WCC API logic
│   ├── ui/
│   │   ├── screens.py       # Tkinter screens
│   │   └── tables.py        # Result/standings table windows
│   └── visualizations/
│       └── plots.py         # FastF1 and Matplotlib plots
├── main.py                  # Entry point
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/F1-Formula-Tracker.git
cd F1-Formula-Tracker
```

Create and activate a virtual environment:

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
python main.py
```

## Usage notes

FastF1 can download a lot of timing data, so the first session load may take a while. The app stores this data in a local `cache/` folder, which is ignored by Git.

For Grand Prix names, use common FastF1 names like:

```text
Monaco
British
Italian
Abu Dhabi
São Paulo
```

For session plots using timing data, use seasons from **2018 onwards**.

## Tech stack

- Python
- Tkinter
- FastF1
- Jolpica F1 API
- Pandas
- Matplotlib
- Seaborn
- NumPy

## Clean-up done

This GitHub-ready version removes:

- PyCharm `.idea/` project files
- `__pycache__/` folders
- `.pyc` files
- FastF1 cache data
- SQLite cache files
- old prototype scripts

It also splits the original single-file app into a cleaner package structure.
