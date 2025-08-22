#!/usr/bin/env python3
"""
Configuration file for Text Scraper
"""

# Scraper Settings
DEFAULT_DELAY = 1.5  # Delay between requests in seconds
DEFAULT_TIMEOUT = 30  # Request timeout in seconds
MAX_RETRIES = 3

# Output Settings
DEFAULT_OUTPUT_DIR = "scraped_content"
SUPPORTED_FORMATS = ['json', 'csv', 'markdown', 'txt']

# Content Extraction Settings
CONTENT_SELECTORS = [
    'article',
    '.content',
    '.post-content',
    '.entry-content',
    '.article-content',
    '.main-content',
    '#content',
    '.text-content',
    'main',
    '.container',
    '.page-content'
]

# Tags to remove during scraping
REMOVE_TAGS = [
    'script', 'style', 'nav', 'header', 'footer',
    'aside', 'form', '.advertisement', '.ads',
    '.navigation', '.menu', '.sidebar', '.comments',
    '.share-buttons', '.social-media'
]

# User agents for different scenarios
USER_AGENTS = {
    'chrome': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'firefox': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'safari': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'edge': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
}

# Logging configuration
LOG_LEVEL = 'INFO'
LOG_FILE = 'scraper.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# Common websites and their specific selectors
SITE_SPECIFIC_SELECTORS = {
    'wikipedia.org': {
        'content': '#mw-content-text',
        'title': '.firstHeading'
    },
    'medium.com': {
        'content': 'article',
        'title': 'h1'
    },
    'stackoverflow.com': {
        'content': '.question, .answer',
        'title': '.question-hyperlink'
    },
    'reddit.com': {
        'content': '.Post',
        'title': 'h3'
    }
}
