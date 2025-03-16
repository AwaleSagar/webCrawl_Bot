# Web Crawler with Database Integration

This web crawler application allows you to search the web for pages related to specific keywords. It now includes database integration for storing and querying crawled data.

## Features

- Keyword-based web crawling
- TF-IDF relevance scoring
- Domain filtering
- Checkpoint saving and resuming
- SQLite database integration
- Command-line interface for database queries
- Smart seed URL generation with Google Gemini API

## Functionality Overview

### Core Capabilities
- **Keyword-Based Crawling**: Find web pages relevant to your specified keywords
- **Smart Seed URL Generation**: Use Google Gemini API to generate intelligent starting points
- **Relevance Scoring**: TF-IDF algorithm to rank pages by relevance to your keywords
- **Content Processing**: Extract and analyze text content from HTML pages
- **Link Extraction**: Discover and follow links to related content
- **Domain Filtering**: Include or exclude specific domains from crawling
- **Rate Limiting**: Respect website rate limits to avoid overloading servers
- **Robots.txt Compliance**: Follow web crawling etiquette standards

### Data Management
- **Database Storage**: Save all crawled data to SQLite database
- **Checkpoint System**: Save and resume crawls from where you left off
- **API Response Logging**: Store Gemini API responses for future reference
- **Data Export**: Export crawled data to JSON or CSV formats

### User Interface
- **Command-Line Interface**: Comprehensive CLI for all crawler operations
- **Database Queries**: Search and filter crawled pages by various criteria
- **Statistics Reporting**: Get insights about your crawling sessions
- **Batch File Launchers**: Easy-to-use batch files for Windows users

### Advanced Features
- **Natural Language Processing**: Stemming, lemmatization, and stopword removal
- **Concurrent Crawling**: Process multiple pages simultaneously
- **Custom HTTP Headers**: Set user agent and other HTTP headers
- **Proxy Support**: Use proxies for crawling if needed
- **Security Features**: API key protection in checkpoints and logs

## Installation

1. Clone the repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Download NLTK data (if using stemming, lemmatization, or stopword removal):

```bash
python src/main.py --download-nltk
```

## Usage

### Basic Crawling

```bash
python src/main.py --keywords "your keywords here" --max-depth 3
```

### Crawling with Database Storage

```bash
python src/main.py --keywords "your keywords here" --use-database --db-path crawler.db
```

### Using Google Gemini API for Smart Seed URLs

The crawler can use Google's Gemini API to generate intelligent seed URLs based on your keywords:

1. Get a Gemini API key:
   - Go to https://ai.google.dev/
   - Sign up for Google AI Studio
   - Create an API key in the Google AI Studio console

2. Use the API key when running the crawler:

```bash
python src/main.py --keywords "machine learning" --gemini-api-key YOUR_API_KEY --generate-seed-urls
```

Additional options:
- `--num-seed-urls`: Number of seed URLs to generate (default: 5)

The Gemini API responses will be logged to the `gemini_logs` directory for future reference.

### Combined Usage (API + Database)

To use both Gemini API for seed URLs and database storage:

```bash
python src/main.py --keywords "your topic" --gemini-api-key YOUR_API_KEY --generate-seed-urls --use-database --db-path crawler.db
```

### Database Query Options

You can query the database directly from the main script:

```bash
python src/main.py --query-db --db-path crawler.db
```

Or use the dedicated CLI tool:

```bash
python src/cli.py --db-path crawler.db stats
```

### CLI Commands

The `cli.py` script provides several commands for interacting with the database:

- `stats`: Show database statistics
- `query`: Query the database for pages
- `recent`: Show recently crawled pages
- `sessions`: Show crawl sessions
- `export`: Export database to a file
- `vacuum`: Vacuum the database to reclaim space

Examples:

```bash
# Show database statistics
python src/cli.py --db-path crawler.db stats

# Query pages with minimum relevance score
python src/cli.py --db-path crawler.db query --min-score 0.5

# Show recent pages
python src/cli.py --db-path crawler.db recent --limit 20

# Show crawl sessions
python src/cli.py --db-path crawler.db sessions

# Export to JSON
python src/cli.py --db-path crawler.db export output.json --format json

# Export to CSV
python src/cli.py --db-path crawler.db export output.csv --format csv

# Vacuum the database
python src/cli.py --db-path crawler.db vacuum
```

## Common Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--keywords` | Keywords to search for | Required |
| `--max-pages` | Maximum pages to crawl | 100 |
| `--max-depth` | Maximum crawl depth | 3 |
| `--checkpoint-interval` | Seconds between checkpoints | 300 |
| `--use-tfidf` | Use TF-IDF for relevance scoring | False |
| `--min-score` | Minimum relevance score (0.0-1.0) | 0.1 |
| `--use-stemming` | Use word stemming | False |
| `--use-lemmatization` | Use word lemmatization | False |
| `--remove-stopwords` | Remove common stopwords | False |
| `--allowed-domains` | Only crawl these domains | None |
| `--excluded-domains` | Skip these domains | None |
| `--user-agent` | Custom user agent string | Default |
| `--timeout` | Request timeout in seconds | 10 |
| `--delay` | Seconds between requests to same domain | 1 |
| `--concurrent` | Number of concurrent requests | 5 |
| `--use-database` | Store results in database | False |
| `--db-path` | Path to database file | crawler.db |
| `--gemini-api-key` | Google Gemini API key | None |
| `--generate-seed-urls` | Use Gemini to generate seed URLs | False |
| `--num-seed-urls` | Number of seed URLs to generate | 5 |

## Database Schema

The crawler uses SQLite with the following schema:

### crawled_pages

- `id`: Primary key
- `url`: URL of the page (unique)
- `title`: Title of the page
- `content_snippet`: Short excerpt of the page content
- `relevance_score`: Calculated relevance score (0.0-1.0)
- `depth`: Crawl depth at which the page was found
- `crawl_time`: When the page was crawled
- `keywords_matched`: Which keywords were matched in the content

### crawl_metadata

- `id`: Primary key
- `start_time`: When the crawl started
- `end_time`: When the crawl ended
- `keywords`: Keywords used for the crawl
- `pages_crawled`: Total number of pages crawled
- `relevant_pages_found`: Number of relevant pages found

## Advanced Options

For a full list of options, run:

```bash
python src/main.py --help
```

Or for the CLI tool:

```bash
python src/cli.py --help
```

## Performance Considerations

- The database uses indexes on URL, relevance score, and crawl time for efficient queries
- Batch operations are used where possible for better performance
- The database is automatically vacuumed to reclaim space when using the `vacuum` command

## Disclaimer

**AI-Generated Content**: This entire project, including all code, documentation, and configuration files, was generated using AI language models (Claude 3.7 Sonnet and Google Gemini 2.0 Flash). While extensive testing has been performed, please be aware of the following:

- **Code Review**: All generated code should be reviewed before deployment in production environments.
- **Security Considerations**: While security best practices have been implemented, a thorough security audit is recommended for sensitive applications.
- **Ethical Usage**: This web crawler should be used responsibly and ethically:
  - Respect website terms of service and robots.txt directives
  - Do not use for scraping copyrighted content without permission
  - Implement reasonable rate limiting to avoid overloading websites
  - Be transparent about your crawler's identity with an appropriate user agent
  - Do not use collected data for harmful purposes

**Limitations**: AI-generated code may contain subtle bugs or edge cases that weren't anticipated during generation. If you encounter issues, please review the code carefully and make necessary adjustments.

**Contributions**: Feel free to improve, modify, and adapt this code to your specific needs. Contributions to enhance functionality, fix bugs, or improve documentation are welcome. 