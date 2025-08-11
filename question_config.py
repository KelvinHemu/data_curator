# Configuration file for Question Generator
# You can modify these settings as needed

# Google Gemini API Configuration
GEMINI_API_KEY = "AIzaSyB0xMJvzkoJBeE0hHSzzbCgLsBUYFMd7cU"
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

# Default settings
DEFAULT_EXAM_DIR = "tetea_exam_papers"
REQUEST_TIMEOUT = 60  # seconds
MIN_CONTENT_LENGTH = 100  # minimum characters for a valid exam file

# File naming conventions
AI_QUESTIONS_SUFFIX = "_ai_questions.md"
QUESTIONS_SUFFIX = "_questions.md"
