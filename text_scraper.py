#!/usr/bin/env python3
"""
Web Text Scraper
A comprehensive text scraping tool for extracting content from websites.
"""

import requests
from bs4 import BeautifulSoup
import time
import csv
import json
import logging
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
import re
from dataclasses import dataclass
from datetime import datetime
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ScrapedContent:
    """Data class to store scraped content"""
    url: str
    title: str
    text: str
    metadata: Dict
    timestamp: str

class TextScraper:
    """
    A comprehensive web text scraper that can extract content from various websites
    """
    
    def __init__(self, delay: float = 1.0, timeout: int = 30):
        """
        Initialize the scraper
        
        Args:
            delay: Delay between requests in seconds
            timeout: Request timeout in seconds
        """
        self.delay = delay
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Common selectors for different content types
        self.content_selectors = [
            'article',
            '.content',
            '.post-content',
            '.entry-content',
            '.article-content',
            '.main-content',
            '#content',
            '.text-content',
            'main',
            '.container'
        ]
        
        # Tags to remove (ads, navigation, etc.)
        self.remove_tags = [
            'script', 'style', 'nav', 'header', 'footer',
            'aside', 'form', '.advertisement', '.ads',
            '.navigation', '.menu', '.sidebar'
        ]

    def get_page_content(self, url: str) -> Optional[requests.Response]:
        """
        Fetch page content from URL
        
        Args:
            url: URL to scrape
            
        Returns:
            Response object or None if failed
        """
        try:
            logger.info(f"Fetching content from: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def clean_text(self, text: str) -> str:
        """
        Clean extracted text
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        # Remove empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)

    def extract_text_from_html(self, html: str, url: str) -> ScrapedContent:
        """
        Extract text content from HTML
        
        Args:
            html: HTML content
            url: Source URL
            
        Returns:
            ScrapedContent object
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract title
        title = ""
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
        
        # Remove unwanted elements
        for tag in self.remove_tags:
            for element in soup.select(tag):
                element.decompose()
        
        # Try to find main content using selectors
        main_content = None
        for selector in self.content_selectors:
            content = soup.select_one(selector)
            if content:
                main_content = content
                break
        
        # If no specific content area found, use body
        if not main_content:
            main_content = soup.find('body')
        
        # Extract text
        text = ""
        if main_content:
            text = main_content.get_text()
        else:
            text = soup.get_text()
        
        # Clean the text
        text = self.clean_text(text)
        
        # Extract metadata
        metadata = self.extract_metadata(soup)
        
        return ScrapedContent(
            url=url,
            title=title,
            text=text,
            metadata=metadata,
            timestamp=datetime.now().isoformat()
        )

    def extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """
        Extract metadata from the page
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Dictionary containing metadata
        """
        metadata = {}
        
        # Meta tags
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            name = tag.get('name') or tag.get('property')
            content = tag.get('content')
            if name and content:
                metadata[name] = content
        
        # Other useful info
        links = soup.find_all('a', href=True)
        metadata['total_links'] = len(links)
        
        images = soup.find_all('img')
        metadata['total_images'] = len(images)
        
        return metadata

    def scrape_url(self, url: str) -> Optional[ScrapedContent]:
        """
        Scrape a single URL
        
        Args:
            url: URL to scrape
            
        Returns:
            ScrapedContent object or None if failed
        """
        response = self.get_page_content(url)
        if not response:
            return None
        
        try:
            content = self.extract_text_from_html(response.text, url)
            logger.info(f"Successfully scraped {url}")
            return content
        except Exception as e:
            logger.error(f"Error extracting text from {url}: {e}")
            return None

    def scrape_urls(self, urls: List[str]) -> List[ScrapedContent]:
        """
        Scrape multiple URLs
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of ScrapedContent objects
        """
        results = []
        
        for i, url in enumerate(urls):
            logger.info(f"Processing URL {i+1}/{len(urls)}: {url}")
            
            content = self.scrape_url(url)
            if content:
                results.append(content)
            
            # Add delay between requests
            if i < len(urls) - 1:
                time.sleep(self.delay)
        
        return results

    def save_to_json(self, contents: List[ScrapedContent], filename: str):
        """
        Save scraped content to JSON file
        
        Args:
            contents: List of ScrapedContent objects
            filename: Output filename
        """
        data = []
        for content in contents:
            data.append({
                'url': content.url,
                'title': content.title,
                'text': content.text,
                'metadata': content.metadata,
                'timestamp': content.timestamp
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(contents)} articles to {filename}")

    def save_to_csv(self, contents: List[ScrapedContent], filename: str):
        """
        Save scraped content to CSV file
        
        Args:
            contents: List of ScrapedContent objects
            filename: Output filename
        """
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['URL', 'Title', 'Text', 'Timestamp'])
            
            for content in contents:
                writer.writerow([
                    content.url,
                    content.title,
                    content.text[:1000] + '...' if len(content.text) > 1000 else content.text,
                    content.timestamp
                ])
        
        logger.info(f"Saved {len(contents)} articles to {filename}")

    def save_to_markdown(self, contents: List[ScrapedContent], output_dir: str = "scraped_content"):
        """
        Save scraped content to individual markdown files
        
        Args:
            contents: List of ScrapedContent objects
            output_dir: Output directory
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for i, content in enumerate(contents):
            # Create filename from title or URL
            if content.title:
                filename = re.sub(r'[^\w\s-]', '', content.title)
                filename = re.sub(r'[-\s]+', '-', filename)
            else:
                filename = f"scraped_content_{i+1}"
            
            filename = f"{filename}.md"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {content.title}\n\n")
                f.write(f"**URL:** {content.url}\n")
                f.write(f"**Scraped:** {content.timestamp}\n\n")
                f.write("---\n\n")
                f.write(content.text)
        
        logger.info(f"Saved {len(contents)} articles to {output_dir}")

def main():
    """
    Example usage of the TextScraper
    """
    # Initialize scraper
    scraper = TextScraper(delay=1.5)
    
    # Example URLs to scrape
    urls = [
        'https://example.com',
        'https://httpbin.org/html',
        # Add more URLs here
    ]
    
    # Scrape the URLs
    results = scraper.scrape_urls(urls)
    
    if results:
        # Save results in different formats
        scraper.save_to_json(results, 'scraped_content.json')
        scraper.save_to_csv(results, 'scraped_content.csv')
        scraper.save_to_markdown(results, 'scraped_content')
        
        print(f"Successfully scraped {len(results)} URLs")
        for result in results:
            print(f"- {result.title} ({len(result.text)} characters)")
    else:
        print("No content was successfully scraped")

if __name__ == "__main__":
    main()
