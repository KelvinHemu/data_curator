#!/usr/bin/env python3
"""
Configuration file for PDF Text Extraction Pipeline
"""

import os

# Google Gemini API Configuration
GEMINI_API_KEY = "AIzaSyBa5KjgQ2jCc0ld7r_TEbPJM0uwPxQHeBs"

# You can also override with environment variable if needed
if os.getenv('GEMINI_API_KEY'):
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Default settings
DEFAULT_OUTPUT_DIR = "Markdown"  # Changed to relative path for Windows
DEFAULT_LANGUAGE = "swa+eng"
DEFAULT_QUALITY = "balanced"

# API Settings
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
MAX_RETRIES = 3
REQUEST_TIMEOUT = 60
