#!/usr/bin/env python3
"""
Example usage of the text scraper
"""

from text_scraper import TextScraper
from advanced_scraper import AdvancedTextScraper
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

def example_basic_scraping():
    """
    Example of basic web scraping
    """
    print("=== Basic Web Scraping Example ===")
    
    # Initialize scraper
    scraper = TextScraper(delay=1.0)
    
    # URLs to scrape
    urls = [
        'https://httpbin.org/html',
        'https://example.com',
        # Add more URLs here
    ]
    
    # Scrape the URLs
    results = scraper.scrape_urls(urls)
    
    if results:
        print(f"Successfully scraped {len(results)} URLs")
        
        # Save in different formats
        scraper.save_to_json(results, 'basic_scraped.json')
        scraper.save_to_markdown(results, 'basic_scraped')
        
        # Display results
        for result in results:
            print(f"\nTitle: {result.title}")
            print(f"URL: {result.url}")
            print(f"Text length: {len(result.text)} characters")
            print(f"Preview: {result.text[:200]}...")
    else:
        print("No content was scraped")

def example_advanced_scraping():
    """
    Example of advanced web scraping with filters
    """
    print("\n=== Advanced Web Scraping Example ===")
    
    # Initialize advanced scraper
    scraper = AdvancedTextScraper(delay=1.5)
    
    # Example: Scrape with content filters
    urls = [
        'https://httpbin.org/html',
        'https://example.com',
    ]
    
    # Set up content filters
    content_filters = {
        'required_keywords': ['example', 'test'],  # Content must contain these words
        'excluded_keywords': ['advertisement', 'spam']  # Content must not contain these
    }
    
    # Scrape with filters
    results = scraper.batch_scrape_with_filters(
        urls, 
        content_filters=content_filters,
        min_word_count=50
    )
    
    if results:
        print(f"Successfully scraped {len(results)} URLs with filters")
        scraper.save_to_json(results, 'filtered_scraped.json')
    else:
        print("No content passed the filters")

def example_url_discovery():
    """
    Example of URL discovery
    """
    print("\n=== URL Discovery Example ===")
    
    scraper = AdvancedTextScraper()
    
    # Example: Discover URLs from a website
    base_url = "https://example.com"
    
    try:
        # Try to discover URLs from sitemap
        sitemap_urls = scraper.discover_urls_from_sitemap(base_url)
        print(f"Found {len(sitemap_urls)} URLs from sitemap")
        
        # Try to discover URLs by crawling
        crawled_urls = scraper.discover_urls_from_page(base_url, max_depth=1)
        print(f"Found {len(crawled_urls)} URLs from crawling")
        
        # Combine and scrape
        all_urls = list(set(sitemap_urls + crawled_urls))[:5]  # Limit to 5 for demo
        
        if all_urls:
            results = scraper.scrape_urls(all_urls)
            print(f"Scraped {len(results)} discovered URLs")
            scraper.save_to_json(results, 'discovered_content.json')
        
    except Exception as e:
        print(f"URL discovery failed: {e}")

def example_custom_usage():
    """
    Example of custom scraper usage for specific needs
    """
    print("\n=== Custom Usage Example ===")
    
    scraper = TextScraper()
    
    # Scrape a single URL
    url = "https://httpbin.org/html"
    content = scraper.scrape_url(url)
    
    if content:
        print(f"Scraped: {content.title}")
        print(f"Metadata: {content.metadata}")
        
        # Custom processing
        word_count = len(content.text.split())
        print(f"Word count: {word_count}")
        
        # Save individual file
        filename = f"single_scrape_{content.timestamp.split('T')[0]}.json"
        scraper.save_to_json([content], filename)
        print(f"Saved to {filename}")

def main():
    """
    Run all examples
    """
    print("Text Scraper Examples")
    print("====================")
    
    try:
        example_basic_scraping()
        example_advanced_scraping()
        example_url_discovery()
        example_custom_usage()
        
        print("\n=== All Examples Completed ===")
        print("Check the output files:")
        print("- basic_scraped.json")
        print("- basic_scraped/ (markdown files)")
        print("- filtered_scraped.json")
        print("- discovered_content.json")
        print("- single_scrape_*.json")
        
    except Exception as e:
        print(f"Error running examples: {e}")

if __name__ == "__main__":
    main()
