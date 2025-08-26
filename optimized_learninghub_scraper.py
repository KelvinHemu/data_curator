#!/usr/bin/env python3
"""
Optimized scraper for learninghubtz.co.tz
Efficiently scrapes all content while avoiding duplicates
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import logging
import os
import re
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set
from datetime import datetime
from text_scraper import TextScraper, ScrapedContent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OptimizedLearningHubScraper(TextScraper):
    """
    Optimized scraper for learninghubtz.co.tz that avoids duplicate content
    """
    
    def __init__(self, delay: float = 2.0):
        super().__init__(delay)
        self.visited_urls: Set[str] = set()
        self.unique_content_hashes: Set[str] = set()
        
    def normalize_url(self, url: str) -> str:
        """
        Normalize URL by removing anchors and query duplicates
        """
        parsed = urlparse(url)
        # Remove anchor fragments
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        # Keep query parameters but normalize common ones
        if parsed.query:
            # Only keep essential query parameters, ignore navigation anchors
            query_parts = parsed.query.split('&')
            essential_params = []
            for part in query_parts:
                if '=' in part:
                    key, value = part.split('=', 1)
                    # Keep subject and year parameters, ignore navigation
                    if key in ['sub', 'yr', 'sb']:
                        essential_params.append(part)
            
            if essential_params:
                normalized += '?' + '&'.join(essential_params)
        
        return normalized
    
    def is_content_duplicate(self, content: str) -> bool:
        """
        Check if content is duplicate based on hash
        """
        # Create a simple hash of the content
        content_hash = hash(content[:1000])  # Hash first 1000 chars
        
        if content_hash in self.unique_content_hashes:
            return True
        
        self.unique_content_hashes.add(content_hash)
        return False
    
    def discover_urls_smart(self, base_url: str, max_urls: int = 100) -> List[str]:
        """
        Smart URL discovery that avoids duplicates and focuses on content pages
        """
        discovered_urls = set()
        to_visit = [base_url]
        depth = 0
        max_depth = 2
        
        while to_visit and len(discovered_urls) < max_urls and depth <= max_depth:
            current_batch = to_visit[:10]  # Process in batches
            to_visit = to_visit[10:]
            
            for url in current_batch:
                normalized_url = self.normalize_url(url)
                
                if normalized_url in self.visited_urls:
                    continue
                
                self.visited_urls.add(normalized_url)
                logger.info(f"Discovering URLs from: {url}")
                
                try:
                    response = self.get_page_content(url)
                    if not response:
                        continue
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find all links
                    links = soup.find_all('a', href=True)
                    
                    for link in links:
                        href = link['href']
                        absolute_url = urljoin(url, href)
                        parsed_url = urlparse(absolute_url)
                        
                        # Only include URLs from the same domain
                        if parsed_url.netloc != 'learninghubtz.co.tz':
                            continue
                        
                        # Skip certain file types and navigation
                        if any(ext in absolute_url.lower() for ext in ['.pdf', '.doc', '.jpg', '.png', '.css', '.js']):
                            continue
                        
                        # Skip purely navigation anchors
                        if '#' in absolute_url and not any(param in absolute_url for param in ['sub=', 'yr=', 'sb=']):
                            continue
                        
                        normalized_new_url = self.normalize_url(absolute_url)
                        
                        if normalized_new_url not in self.visited_urls:
                            discovered_urls.add(normalized_new_url)
                            
                            # Add to next batch for deeper crawling if it's a content page
                            if any(keyword in absolute_url for keyword in ['exam', 'necta', 'series', 'qns', 'reviews']):
                                to_visit.append(absolute_url)
                    
                    time.sleep(self.delay)
                    
                except Exception as e:
                    logger.error(f"Error discovering URLs from {url}: {e}")
            
            depth += 1
        
        logger.info(f"Discovered {len(discovered_urls)} unique URLs")
        return list(discovered_urls)
    
    def scrape_with_deduplication(self, urls: List[str]) -> List[ScrapedContent]:
        """
        Scrape URLs while removing duplicate content
        """
        results = []
        
        for i, url in enumerate(urls):
            logger.info(f"Scraping URL {i+1}/{len(urls)}: {url}")
            
            content = self.scrape_url(url)
            if not content:
                continue
            
            # Check for duplicate content
            if self.is_content_duplicate(content.text):
                logger.info(f"Skipping duplicate content from: {url}")
                continue
            
            # Only keep content with substantial text
            if len(content.text.split()) < 50:
                logger.info(f"Skipping short content from: {url}")
                continue
            
            results.append(content)
            
            # Add delay between requests
            time.sleep(self.delay)
        
        return results
    
    def save_to_organized_markdown(self, contents: List[ScrapedContent], 
                                 output_dir: str = "learninghubtz_content"):
        """
        Save content to organized markdown files
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Create index file
        index_content = f"# Learning Hub Tanzania - Scraped Content\n\n"
        index_content += f"**Scraped:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        index_content += f"**Total Pages:** {len(contents)}\n\n"
        index_content += "## Content Pages\n\n"
        
        for i, content in enumerate(contents):
            # Create filename from title or URL
            if content.title:
                filename = re.sub(r'[^\w\s-]', '', content.title)
                filename = re.sub(r'[-\s]+', '-', filename)
                filename = filename[:50]  # Limit length
            else:
                # Extract meaningful name from URL
                url_parts = content.url.split('/')
                filename = url_parts[-1] if url_parts[-1] else f"page_{i+1}"
                filename = filename.split('?')[0]  # Remove query params
                filename = re.sub(r'[^\w-]', '', filename)
            
            filename = f"{i+1:03d}_{filename}.md"
            filepath = os.path.join(output_dir, filename)
            
            # Write individual file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {content.title or 'Learning Hub Content'}\n\n")
                f.write(f"**Source:** {content.url}\n")
                f.write(f"**Scraped:** {content.timestamp}\n")
                f.write(f"**Word Count:** {len(content.text.split())}\n\n")
                f.write("---\n\n")
                f.write(content.text)
            
            # Add to index
            index_content += f"{i+1}. [{content.title or filename}]({filename})\n"
            index_content += f"   - **Source:** {content.url}\n"
            index_content += f"   - **Words:** {len(content.text.split())}\n\n"
        
        # Save index file
        with open(os.path.join(output_dir, "INDEX.md"), 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        logger.info(f"Saved {len(contents)} unique pages to {output_dir}")

def main():
    """
    Main scraping function
    """
    print("🚀 Starting optimized scraping of learninghubtz.co.tz")
    
    # Initialize scraper
    scraper = OptimizedLearningHubScraper(delay=1.5)
    
    # Discover URLs smartly
    print("🔍 Discovering URLs...")
    urls = scraper.discover_urls_smart('https://learninghubtz.co.tz', max_urls=200)
    
    print(f"📋 Found {len(urls)} unique URLs to scrape")
    
    # Scrape with deduplication
    print("📄 Scraping content...")
    results = scraper.scrape_with_deduplication(urls)
    
    if results:
        print(f"✅ Successfully scraped {len(results)} unique pages")
        
        # Save to organized markdown
        scraper.save_to_organized_markdown(results, "learninghubtz_content")
        
        print("📁 Content saved to 'learninghubtz_content' directory")
        print(f"📊 Summary:")
        print(f"   - Total URLs discovered: {len(urls)}")
        print(f"   - Unique pages scraped: {len(results)}")
        print(f"   - Total words: {sum(len(r.text.split()) for r in results)}")
        
    else:
        print("❌ No content was successfully scraped")

if __name__ == "__main__":
    main()
