#!/usr/bin/env python3
"""
Advanced Text Scraper with URL discovery and batch processing
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import logging
from urllib.parse import urljoin, urlparse, urlencode
from typing import List, Dict, Optional, Set
import re
from datetime import datetime
import os
import argparse
from scraper_config import *
from text_scraper import TextScraper, ScrapedContent

# Setup logger
logger = logging.getLogger(__name__)

class AdvancedTextScraper(TextScraper):
    """
    Enhanced text scraper with URL discovery and advanced features
    """
    
    def __init__(self, delay: float = DEFAULT_DELAY, timeout: int = DEFAULT_TIMEOUT):
        super().__init__(delay, timeout)
        self.visited_urls: Set[str] = set()
        
    def discover_urls_from_sitemap(self, base_url: str) -> List[str]:
        """
        Discover URLs from sitemap.xml
        
        Args:
            base_url: Base URL of the website
            
        Returns:
            List of discovered URLs
        """
        sitemap_urls = [
            urljoin(base_url, '/sitemap.xml'),
            urljoin(base_url, '/sitemap_index.xml'),
            urljoin(base_url, '/robots.txt')
        ]
        
        urls = []
        
        for sitemap_url in sitemap_urls:
            try:
                response = self.get_page_content(sitemap_url)
                if response:
                    if 'robots.txt' in sitemap_url:
                        # Extract sitemap URLs from robots.txt
                        for line in response.text.split('\n'):
                            if line.lower().startswith('sitemap:'):
                                sitemap_url = line.split(':', 1)[1].strip()
                                response = self.get_page_content(sitemap_url)
                                if response:
                                    urls.extend(self._parse_sitemap(response.text))
                    else:
                        urls.extend(self._parse_sitemap(response.text))
            except Exception as e:
                logger.warning(f"Could not process sitemap {sitemap_url}: {e}")
        
        return list(set(urls))
    
    def _parse_sitemap(self, sitemap_content: str) -> List[str]:
        """
        Parse sitemap XML content
        
        Args:
            sitemap_content: XML content of sitemap
            
        Returns:
            List of URLs found in sitemap
        """
        urls = []
        soup = BeautifulSoup(sitemap_content, 'xml')
        
        # Handle sitemap index
        sitemaps = soup.find_all('sitemap')
        for sitemap in sitemaps:
            loc = sitemap.find('loc')
            if loc:
                urls.append(loc.text.strip())
        
        # Handle URL entries
        url_entries = soup.find_all('url')
        for url_entry in url_entries:
            loc = url_entry.find('loc')
            if loc:
                urls.append(loc.text.strip())
        
        return urls
    
    def discover_urls_from_page(self, url: str, max_depth: int = 1, 
                               same_domain_only: bool = True) -> List[str]:
        """
        Discover URLs by crawling links from a page
        
        Args:
            url: Starting URL
            max_depth: Maximum crawling depth
            same_domain_only: Only follow links within same domain
            
        Returns:
            List of discovered URLs
        """
        discovered_urls = set()
        to_visit = [(url, 0)]
        base_domain = urlparse(url).netloc
        
        while to_visit:
            current_url, depth = to_visit.pop(0)
            
            if current_url in self.visited_urls or depth > max_depth:
                continue
            
            self.visited_urls.add(current_url)
            response = self.get_page_content(current_url)
            
            if not response:
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                absolute_url = urljoin(current_url, href)
                
                # Filter URLs
                parsed_url = urlparse(absolute_url)
                
                if same_domain_only and parsed_url.netloc != base_domain:
                    continue
                
                if parsed_url.scheme not in ['http', 'https']:
                    continue
                
                discovered_urls.add(absolute_url)
                
                if depth < max_depth:
                    to_visit.append((absolute_url, depth + 1))
            
            time.sleep(self.delay)
        
        return list(discovered_urls)
    
    def scrape_search_results(self, search_engine: str, query: str, 
                            num_results: int = 10) -> List[str]:
        """
        Scrape URLs from search engine results
        
        Args:
            search_engine: Search engine ('google', 'bing', 'duckduckgo')
            query: Search query
            num_results: Number of results to get
            
        Returns:
            List of URLs from search results
        """
        urls = []
        
        if search_engine.lower() == 'google':
            search_url = f"https://www.google.com/search?{urlencode({'q': query, 'num': num_results})}"
        elif search_engine.lower() == 'bing':
            search_url = f"https://www.bing.com/search?{urlencode({'q': query, 'count': num_results})}"
        elif search_engine.lower() == 'duckduckgo':
            search_url = f"https://duckduckgo.com/html/?{urlencode({'q': query})}"
        else:
            logger.error(f"Unsupported search engine: {search_engine}")
            return urls
        
        response = self.get_page_content(search_url)
        if not response:
            return urls
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract URLs based on search engine
        if search_engine.lower() == 'google':
            for result in soup.find_all('div', class_='g'):
                link = result.find('a', href=True)
                if link and '/url?q=' in link['href']:
                    url = link['href'].split('/url?q=')[1].split('&')[0]
                    urls.append(url)
        elif search_engine.lower() == 'bing':
            for result in soup.find_all('li', class_='b_algo'):
                link = result.find('a', href=True)
                if link:
                    urls.append(link['href'])
        elif search_engine.lower() == 'duckduckgo':
            for result in soup.find_all('a', class_='result__a'):
                if result.get('href'):
                    urls.append(result['href'])
        
        return urls[:num_results]
    
    def batch_scrape_with_filters(self, urls: List[str], 
                                 content_filters: Dict = None,
                                 min_word_count: int = 100) -> List[ScrapedContent]:
        """
        Scrape URLs with content filtering
        
        Args:
            urls: List of URLs to scrape
            content_filters: Dictionary of filters to apply
            min_word_count: Minimum word count for content
            
        Returns:
            List of filtered ScrapedContent objects
        """
        results = []
        content_filters = content_filters or {}
        
        for url in urls:
            content = self.scrape_url(url)
            if not content:
                continue
            
            # Apply filters
            if len(content.text.split()) < min_word_count:
                logger.info(f"Skipping {url}: content too short")
                continue
            
            # Apply keyword filters
            if 'required_keywords' in content_filters:
                if not any(keyword.lower() in content.text.lower() 
                          for keyword in content_filters['required_keywords']):
                    logger.info(f"Skipping {url}: missing required keywords")
                    continue
            
            if 'excluded_keywords' in content_filters:
                if any(keyword.lower() in content.text.lower() 
                      for keyword in content_filters['excluded_keywords']):
                    logger.info(f"Skipping {url}: contains excluded keywords")
                    continue
            
            results.append(content)
        
        return results

def create_scraper_cli():
    """
    Create command-line interface for the scraper
    """
    parser = argparse.ArgumentParser(description='Advanced Text Scraper')
    
    parser.add_argument('--urls', nargs='+', help='URLs to scrape')
    parser.add_argument('--url-file', help='File containing URLs (one per line)')
    parser.add_argument('--sitemap', help='Discover URLs from sitemap')
    parser.add_argument('--crawl', help='Crawl URLs starting from this URL')
    parser.add_argument('--search', help='Search query to find URLs')
    parser.add_argument('--search-engine', default='google', 
                       choices=['google', 'bing', 'duckduckgo'],
                       help='Search engine to use')
    parser.add_argument('--output-format', default='json',
                       choices=['json', 'csv', 'markdown'],
                       help='Output format')
    parser.add_argument('--output-file', default='scraped_content',
                       help='Output file/directory name')
    parser.add_argument('--delay', type=float, default=DEFAULT_DELAY,
                       help='Delay between requests')
    parser.add_argument('--max-results', type=int, default=10,
                       help='Maximum number of results')
    parser.add_argument('--min-words', type=int, default=100,
                       help='Minimum word count for content')
    parser.add_argument('--required-keywords', nargs='+',
                       help='Required keywords in content')
    parser.add_argument('--excluded-keywords', nargs='+',
                       help='Keywords to exclude from content')
    
    return parser

def main():
    """
    Main function for CLI usage
    """
    parser = create_scraper_cli()
    args = parser.parse_args()
    
    # Initialize scraper
    scraper = AdvancedTextScraper(delay=args.delay)
    
    # Collect URLs
    urls = []
    
    if args.urls:
        urls.extend(args.urls)
    
    if args.url_file:
        try:
            with open(args.url_file, 'r') as f:
                urls.extend([line.strip() for line in f if line.strip()])
        except FileNotFoundError:
            logger.error(f"URL file not found: {args.url_file}")
            return
    
    if args.sitemap:
        discovered = scraper.discover_urls_from_sitemap(args.sitemap)
        urls.extend(discovered[:args.max_results])
        logger.info(f"Discovered {len(discovered)} URLs from sitemap")
    
    if args.crawl:
        discovered = scraper.discover_urls_from_page(args.crawl, max_depth=2)
        urls.extend(discovered[:args.max_results])
        logger.info(f"Discovered {len(discovered)} URLs from crawling")
    
    if args.search:
        discovered = scraper.scrape_search_results(
            args.search_engine, args.search, args.max_results
        )
        urls.extend(discovered)
        logger.info(f"Found {len(discovered)} URLs from search")
    
    if not urls:
        logger.error("No URLs provided")
        return
    
    # Remove duplicates
    urls = list(set(urls))
    logger.info(f"Scraping {len(urls)} unique URLs")
    
    # Set up content filters
    content_filters = {}
    if args.required_keywords:
        content_filters['required_keywords'] = args.required_keywords
    if args.excluded_keywords:
        content_filters['excluded_keywords'] = args.excluded_keywords
    
    # Scrape content
    results = scraper.batch_scrape_with_filters(
        urls, content_filters, args.min_words
    )
    
    if not results:
        logger.warning("No content was successfully scraped")
        return
    
    # Save results
    if args.output_format == 'json':
        scraper.save_to_json(results, f"{args.output_file}.json")
    elif args.output_format == 'csv':
        scraper.save_to_csv(results, f"{args.output_file}.csv")
    elif args.output_format == 'markdown':
        scraper.save_to_markdown(results, args.output_file)
    
    logger.info(f"Successfully scraped {len(results)} articles")

if __name__ == "__main__":
    main()
