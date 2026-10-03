"""
Configuration settings for WhatsApp Analytics Project
"""

from pathlib import Path

# ==================================================
# PROJECT DIRECTORIES
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FOLDER = BASE_DIR / "data"
OUTPUT_FOLDER = BASE_DIR / "output"
ASSETS_FOLDER = BASE_DIR / "assets"
TEMP_FOLDER = BASE_DIR / "temp"

# ==================================================
# CHAT SETTINGS
# ==================================================

CONVERSATION_GAP_HOURS = 8

SUPPORTED_LANGUAGES = [
    "English",
    "Hindi",
    "Marathi"
]

SUPPORTED_FILE_EXTENSION = ".txt"

# ==================================================
# VISUALIZATION SETTINGS
# ==================================================

FIGURE_WIDTH = 14
FIGURE_HEIGHT = 8

TOP_WORDS = 30
TOP_EMOJIS = 20
TOP_TOPICS = 15

# ==================================================
# RESPONSE TIME SETTINGS
# ==================================================

FAST_REPLY_SECONDS = 60
LATE_REPLY_HOURS = 24

# ==========================
# AI Configuration
# ==========================

# ==========================
# AI Configuration
# ==========================

AI_CONFIG = {
    "provider": "openai",
    "model": "gpt-4.1-mini",
    "temperature": 0.2,
    "max_tokens": 1500,
}
