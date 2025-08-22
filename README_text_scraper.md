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

The advanced scraper includes a command-line interface with various methods to discover and scrape content:

### 1. Scrape Specific URLs
```bash
python advanced_scraper.py --urls https://example.com https://test.com --output-format json
```
**What it does:**
- Takes a list of specific URLs that you provide
- Scrapes the text content from each website
- Saves results in JSON format with structured data (title, text, metadata, timestamp)
- Perfect when you know exactly which websites to scrape

### 2. Scrape URLs from a File
```bash
python advanced_scraper.py --url-file urls.txt --output-format markdown
```
**What it does:**
- Reads URLs from a text file (one URL per line)
- Scrapes all URLs listed in the file
- Saves each page as a separate Markdown file
- Ideal for batch processing many URLs without typing them all

**Example `urls.txt` file:**
```
https://example.com
https://test.com
https://another-site.com
```

### 3. Discover URLs from Sitemap
```bash
python advanced_scraper.py --sitemap https://example.com --max-results 50
```
**What it does:**
- Automatically finds and parses the sitemap.xml file from the website
- Extracts up to 50 URLs from the sitemap
- Scrapes all discovered URLs systematically
- Great for comprehensive website scraping using the site's own URL index

### 4. Crawl and Scrape URLs
```bash
python advanced_scraper.py --crawl https://example.com --max-results 20
```
**What it does:**
- Starts at the given URL and follows links found on that page
- Discovers new URLs by crawling through the website like a mini search engine
- Limits discovery to maximum 20 URLs
- Scrapes all discovered URLs automatically
- Perfect for exploring websites and finding related content

### 5. Search and Scrape
```bash
python advanced_scraper.py --search "python web scraping" --search-engine google --max-results 10
```
**What it does:**
- Searches Google (or Bing/DuckDuckGo) for your query
- Extracts the first 10 URLs from search results
- Scrapes content from those search result pages
- Excellent for research on specific topics or finding expert content
- Supports multiple search engines for different perspectives

### 6. Content Filtering
```bash
python advanced_scraper.py --urls https://example.com --required-keywords python programming --min-words 200
```
**What it does:**
- Scrapes the specified URL(s)
- Only keeps content that contains ALL required keywords ("python" AND "programming")
- Only keeps content with at least 200 words
- Filters out short articles, irrelevant content, or spam
- Ensures you get only high-quality, relevant content

### Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--urls` | List of specific URLs to scrape | `--urls https://site1.com https://site2.com` |
| `--url-file` | File containing URLs (one per line) | `--url-file my_urls.txt` |
| `--sitemap` | Discover URLs from website sitemap | `--sitemap https://example.com` |
| `--crawl` | Crawl and discover URLs from starting page | `--crawl https://example.com` |
| `--search` | Search query to find URLs via search engines | `--search "machine learning"` |
| `--search-engine` | Search engine to use (google, bing, duckduckgo) | `--search-engine google` |
| `--output-format` | Output format (json, csv, markdown) | `--output-format json` |
| `--output-file` | Output file/directory name | `--output-file results` |
| `--delay` | Delay between requests (seconds) | `--delay 2.0` |
| `--max-results` | Maximum number of results to process | `--max-results 50` |
| `--min-words` | Minimum word count for content | `--min-words 100` |
| `--required-keywords` | Keywords that MUST be in content | `--required-keywords python data` |
| `--excluded-keywords` | Keywords to exclude from content | `--excluded-keywords spam ads` |

### Real-World Usage Examples

**Research and Data Collection:**
```bash
# Research articles about AI ethics
python advanced_scraper.py --search "AI ethics research" --search-engine google --max-results 15 --min-words 500 --output-format markdown

# Scrape a news website comprehensively
python advanced_scraper.py --sitemap https://news-site.com --max-results 100 --required-keywords technology --output-format json
```

**Content Quality Control:**
```bash
# Get only high-quality programming tutorials
python advanced_scraper.py --search "python tutorial" --min-words 300 --required-keywords code example --excluded-keywords advertisement spam

# Filter competitor analysis content
python advanced_scraper.py --crawl https://competitor.com --max-results 30 --required-keywords product feature --min-words 200
```

**Batch Processing:**
```bash
# Process a large list of academic papers
python advanced_scraper.py --url-file academic_papers.txt --min-words 1000 --output-format markdown --delay 3.0
```

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

## Practical Use Cases and Workflows

### 📊 **Research and Academic Work**

**Scenario**: Collecting research papers on "machine learning ethics"
```bash
# Step 1: Find relevant papers
python advanced_scraper.py --search "machine learning ethics research papers" --search-engine google --max-results 20 --min-words 1000 --output-format json --output-file ml_ethics_research

# Step 2: Filter for academic quality
python advanced_scraper.py --url-file academic_urls.txt --required-keywords methodology conclusion references --min-words 2000 --excluded-keywords blog opinion --output-format markdown
```

### 🏢 **Business Intelligence**

**Scenario**: Monitoring competitor websites
```bash
# Comprehensive competitor analysis
python advanced_scraper.py --crawl https://competitor.com --max-results 50 --required-keywords product feature pricing --min-words 200 --delay 3.0 --output-format json

# News monitoring about your industry
python advanced_scraper.py --search "fintech innovation 2025" --search-engine bing --max-results 15 --required-keywords technology startup --output-format markdown
```

### 📰 **Content Aggregation**

**Scenario**: Building a news aggregator
```bash
# Scrape multiple news sites
python advanced_scraper.py --sitemap https://technews.com --max-results 30 --required-keywords technology AI blockchain --min-words 300 --output-format json

# Filter for breaking news
python advanced_scraper.py --search "breaking tech news today" --max-results 10 --required-keywords "breaking" "today" --output-format markdown
```

### 🎓 **Educational Content Collection**

**Scenario**: Gathering programming tutorials
```bash
# High-quality programming tutorials
python advanced_scraper.py --search "python advanced tutorial" --required-keywords code example project --min-words 500 --excluded-keywords advertisement subscribe --max-results 25

# Comprehensive documentation scraping
python advanced_scraper.py --sitemap https://docs.python.org --max-results 100 --required-keywords function class method --output-format markdown
```

### 🔍 **Market Research**

**Scenario**: Product review analysis
```bash
# Product reviews and comparisons
python advanced_scraper.py --search "iPhone 15 review comparison" --required-keywords review rating pros cons --min-words 400 --excluded-keywords affiliate sponsored --max-results 20

# Industry trend analysis
python advanced_scraper.py --crawl https://industry-blog.com --required-keywords trend forecast analysis --min-words 600 --output-format json
```

### 🛠 **Custom Workflows**

**Multi-step Research Workflow:**
```bash
# Step 1: Broad search for initial URLs
python advanced_scraper.py --search "sustainable energy solutions" --max-results 50 --output-format json --output-file initial_research

# Step 2: Extract URLs and create focused list
# (manually review and create focused_urls.txt)

# Step 3: Deep scrape with strict filters
python advanced_scraper.py --url-file focused_urls.txt --required-keywords renewable solar wind --min-words 800 --excluded-keywords advertisement marketing --output-format markdown --output-file final_research
```

## Features in Detail

### URL Discovery Methods

#### 1. **Sitemap Discovery**
- Automatically finds and parses `sitemap.xml` files
- Follows sitemap index files for large websites
- Extracts URLs systematically from website's own URL index
- **Use case**: Comprehensive scraping of entire websites

#### 2. **Web Crawling**
- Follows links to discover more URLs organically
- Respects same-domain restrictions (configurable)
- Supports depth-limited crawling to prevent infinite loops
- **Use case**: Exploring related content and discovering hidden pages

#### 3. **Search Integration**
- Integrates with Google, Bing, and DuckDuckGo
- Finds URLs based on search queries
- Extracts actual content URLs from search results
- **Use case**: Research and topic-based content discovery

### Content Filtering System

#### **Keyword Filtering**
```python
# Include content only if it contains specific keywords
content_filters = {
    'required_keywords': ['python', 'programming', 'tutorial'],  # Must contain ALL
    'excluded_keywords': ['advertisement', 'spam', 'click here']  # Must contain NONE
}
```

#### **Quality Filtering**
- **Word Count**: Filter by minimum/maximum content length
- **Content Structure**: Detect and filter low-quality pages
- **Custom Logic**: Add your own filtering functions

#### **Example Filtering Scenarios**
```bash
# Academic research papers only
--min-words 2000 --required-keywords research paper methodology --excluded-keywords blog opinion

# High-quality tutorials only  
--min-words 500 --required-keywords code example tutorial --excluded-keywords advertisement subscribe

# News articles about specific topics
--required-keywords "climate change" policy --excluded-keywords opinion editorial --min-words 300
```

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

### Common Issues and Solutions

#### 1. **SSL/Connection Errors**
```
Error: SSL certificate verify failed
```
**Solutions:**
- Some sites have SSL certificate issues
- Increase delay between requests: `--delay 3.0`
- Try different user agents in configuration

#### 2. **Rate Limiting/Getting Blocked**
```
Error: 429 Too Many Requests or 403 Forbidden
```
**Solutions:**
- Increase delays: `--delay 5.0` or higher
- Use different user agents in `scraper_config.py`
- Reduce `--max-results` to smaller batches
- Check website's `robots.txt` for crawl rules

#### 3. **Content Not Found**
```
Warning: Scraper not finding main content
```
**Solutions:**
- Customize content selectors in `scraper_config.py`
- Add site-specific selectors for particular websites
- Check if the site uses JavaScript (requires different tools)

#### 4. **Memory Issues**
```
Error: Memory usage too high
```
**Solutions:**
- Process URLs in smaller batches
- Use `--max-results` to limit scope
- Clear results periodically in custom scripts
- Consider using streaming processing for large datasets

#### 5. **Search Engine Blocking**
```
Error: Search results not found
```
**Solutions:**
- Try different search engines: `--search-engine bing` or `--search-engine duckduckgo`
- Add longer delays between search requests
- Use more specific search queries

### Debugging Tips

#### Enable Detailed Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Check Log Files
- Monitor `scraper.log` for detailed execution information
- Look for specific error patterns and URLs that fail
- Check network connectivity and DNS resolution

#### Test with Simple URLs First
```bash
# Test with a simple, reliable URL first
python advanced_scraper.py --urls https://httpbin.org/html --output-format json

# Then gradually add complexity
python advanced_scraper.py --urls https://httpbin.org/html --required-keywords Herman --min-words 100
```

### Performance Optimization

#### For Large-Scale Scraping
```bash
# Use longer delays to be respectful
--delay 2.0

# Process in smaller batches
--max-results 20

# Save incrementally to avoid data loss
--output-format json --output-file batch_001
```

#### For Speed (Use Responsibly)
```bash
# Shorter delays for cooperative sites
--delay 0.5

# Larger batches for efficient processing
--max-results 100
```

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
