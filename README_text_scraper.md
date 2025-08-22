# Text Scraper

A comprehensive Python-based web text scraper that can extract content from websites with advanced features like URL discovery, content filtering, and multiple output formats.

## Features

- **Basic Text Extraction**: Extract clean text content from web pages
- **Advanced Content Filtering**: Filter content by keywords, word count, etc.
- **URL Discovery**: Automatically discover URLs from sitemaps and crawling
- **Search Integration**: Find URLs using search engines
- **Multiple Output Formats**: JSON, CSV, and Markdown
- **Configurable**: Customizable delays, timeouts, and content selectors
- **Logging**: Comprehensive logging for debugging and monitoring
- **Metadata Extraction**: Extract page metadata and statistics

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements_scraper.txt
```

## Quick Start

### Basic Usage

```python
from text_scraper import TextScraper

# Initialize scraper
scraper = TextScraper(delay=1.0)

# Scrape URLs
urls = ['https://example.com', 'https://httpbin.org/html']
results = scraper.scrape_urls(urls)

# Save results
scraper.save_to_json(results, 'output.json')
scraper.save_to_markdown(results, 'output_dir')
```

### Advanced Usage

```python
from advanced_scraper import AdvancedTextScraper

# Initialize advanced scraper
scraper = AdvancedTextScraper(delay=1.5)

# Scrape with content filters
content_filters = {
    'required_keywords': ['python', 'programming'],
    'excluded_keywords': ['advertisement']
}

results = scraper.batch_scrape_with_filters(
    urls,
    content_filters=content_filters,
    min_word_count=100
)
```

## Command Line Usage

The advanced scraper includes a command-line interface:

```bash
# Scrape specific URLs
python advanced_scraper.py --urls https://example.com https://test.com --output-format json

# Scrape URLs from a file
python advanced_scraper.py --url-file urls.txt --output-format markdown

# Discover URLs from sitemap
python advanced_scraper.py --sitemap https://example.com --max-results 50

# Crawl and scrape URLs
python advanced_scraper.py --crawl https://example.com --max-results 20

# Search and scrape
python advanced_scraper.py --search "python web scraping" --search-engine google --max-results 10

# With content filters
python advanced_scraper.py --urls https://example.com --required-keywords python programming --min-words 200
```

### Command Line Options

- `--urls`: List of URLs to scrape
- `--url-file`: File containing URLs (one per line)
- `--sitemap`: Discover URLs from sitemap
- `--crawl`: Crawl URLs starting from this URL
- `--search`: Search query to find URLs
- `--search-engine`: Search engine (google, bing, duckduckgo)
- `--output-format`: Output format (json, csv, markdown)
- `--output-file`: Output file/directory name
- `--delay`: Delay between requests (seconds)
- `--max-results`: Maximum number of results
- `--min-words`: Minimum word count for content
- `--required-keywords`: Required keywords in content
- `--excluded-keywords`: Keywords to exclude from content

## Configuration

The scraper can be configured through `scraper_config.py`:

- **Delays and Timeouts**: Control request timing
- **Content Selectors**: Define how to find main content
- **Remove Tags**: Specify elements to remove
- **User Agents**: Different browser identities
- **Site-Specific Selectors**: Custom selectors for specific websites

## Output Formats

### JSON
Structured data with full metadata:
```json
{
  "url": "https://example.com",
  "title": "Example Page",
  "text": "Page content...",
  "metadata": {"author": "...", "keywords": "..."},
  "timestamp": "2025-08-22T10:30:00"
}
```

### CSV
Tabular format for analysis:
```csv
URL,Title,Text,Timestamp
https://example.com,Example Page,Page content...,2025-08-22T10:30:00
```

### Markdown
Individual files for each scraped page:
```markdown
# Page Title

**URL:** https://example.com
**Scraped:** 2025-08-22T10:30:00

---

Page content here...
```

## Examples

Run the examples to see the scraper in action:

```bash
python scraper_examples.py
```

This will demonstrate:
- Basic web scraping
- Advanced scraping with filters
- URL discovery
- Custom usage patterns

## Features in Detail

### URL Discovery

1. **Sitemap Discovery**: Automatically find and parse sitemap.xml files
2. **Web Crawling**: Follow links to discover more URLs
3. **Search Integration**: Find URLs using search engines

### Content Filtering

- **Keyword Filtering**: Include/exclude content based on keywords
- **Word Count**: Filter by minimum content length
- **Custom Filters**: Add your own filtering logic

### Content Extraction

- **Smart Content Detection**: Automatically find main content areas
- **Metadata Extraction**: Extract page metadata and statistics
- **Clean Text**: Remove navigation, ads, and other non-content elements

### Error Handling

- **Robust Error Handling**: Continue scraping even if some URLs fail
- **Retry Logic**: Automatically retry failed requests
- **Logging**: Detailed logs for debugging

## Best Practices

1. **Respect robots.txt**: Always check and respect website policies
2. **Use Delays**: Add delays between requests to avoid overwhelming servers
3. **Handle Errors**: Implement proper error handling for production use
4. **Filter Content**: Use content filters to get only relevant information
5. **Monitor Resources**: Watch memory usage when scraping large numbers of URLs

## Troubleshooting

### Common Issues

1. **SSL Errors**: Some sites may have SSL certificate issues
   - Solution: Add SSL verification options

2. **Rate Limiting**: Getting blocked by websites
   - Solution: Increase delays, use different user agents

3. **Content Not Found**: Scraper not finding main content
   - Solution: Customize content selectors in config

4. **Memory Issues**: Running out of memory with large scrapes
   - Solution: Process URLs in batches, clear results periodically

### Debugging

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check the `scraper.log` file for detailed information about what the scraper is doing.

## Legal and Ethical Considerations

- Always respect website terms of service
- Check and follow robots.txt files
- Don't overload servers with too many requests
- Use appropriate delays between requests
- Consider reaching out to website owners for large-scale scraping

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.
