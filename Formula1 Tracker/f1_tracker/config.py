from pathlib import Path

APP_TITLE = "Formula Tracker"
WINDOW_SIZE = "600x600"
PRIMARY_COLOR = "#920F0F"
BACKGROUND_COLOR = "#F8F8F8"
TEXT_COLOR = "#000000"
LIGHT_TEXT_COLOR = "#FFFFFF"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
CACHE_DIR = PROJECT_ROOT / "cache"

JOLPICA_BASE_URL = "https://api.jolpi.ca/ergast/f1"
