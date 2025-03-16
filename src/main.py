#!/usr/bin/env python3
"""
Web Crawler - Main Entry Point
This is the main entry point for the web crawler application.
"""

import argparse
import sys
import json
import os
import re
import datetime
from crawler import WebCrawler, generate_seed_urls_with_gemini
from keyword_processor import KeywordProcessor, download_nltk_data
from database_manager import DatabaseManager

def save_settings_to_log(settings, log_dir="logs"):
    """
    Save crawler settings to a log file.
    
    Args:
        settings (dict): Dictionary containing crawler settings
        log_dir (str): Directory to store log files
    
    Returns:
        str: Path to the created log file
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Generate log filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"crawler_settings_{timestamp}.log"
    log_filepath = os.path.join(log_dir, log_filename)
    
    # Remove sensitive information
    safe_settings = settings.copy()
    # Always remove API key completely, don't even store a redacted version
    if 'gemini_api_key' in safe_settings:
        del safe_settings['gemini_api_key']
    
    # Format the log content
    log_content = "Web Crawler Settings Log\n"
    log_content += "======================\n"
    log_content += f"Timestamp: {datetime.datetime.now().isoformat()}\n\n"
    
    # Add basic settings
    log_content += "Basic Settings:\n"
    log_content += f"  Keywords: {', '.join(safe_settings.get('keywords', []))}\n"
    log_content += f"  Seed URLs: {', '.join(safe_settings.get('seed_urls', []))}\n"
    log_content += f"  Max Depth: {safe_settings.get('max_depth', 3)}\n"
    log_content += f"  Delay: {safe_settings.get('delay', 1.0)} seconds\n"
    log_content += f"  User Agent: {safe_settings.get('user_agent', 'WebCrawler/1.0')}\n\n"
    
    # Add keyword processing settings
    log_content += "Keyword Processing:\n"
    log_content += f"  Use Stemming: {safe_settings.get('use_stemming', False)}\n"
    log_content += f"  Use Lemmatization: {safe_settings.get('use_lemmatization', False)}\n"
    log_content += f"  Remove Stopwords: {safe_settings.get('remove_stopwords', False)}\n"
    log_content += f"  Regex Pattern: {safe_settings.get('regex_pattern', 'None')}\n\n"
    
    # Add content matching settings
    log_content += "Content Matching:\n"
    log_content += f"  Use TF-IDF: {safe_settings.get('use_tfidf', False)}\n"
    log_content += f"  Min Relevance Score: {safe_settings.get('min_relevance_score', 0.1)}\n\n"
    
    # Add domain filtering settings
    log_content += "Domain Filtering:\n"
    log_content += f"  Stay in Domain: {safe_settings.get('stay_in_domain', False)}\n"
    log_content += f"  Allowed Domains: {', '.join(safe_settings.get('allowed_domains', []) or ['None'])}\n"
    log_content += f"  Excluded Domains: {', '.join(safe_settings.get('excluded_domains', []) or ['None'])}\n\n"
    
    # Add checkpoint settings
    log_content += "Checkpoint Settings:\n"
    log_content += f"  Checkpoint Interval: {safe_settings.get('checkpoint_interval', 300)} seconds\n"
    log_content += f"  Checkpoint Directory: {safe_settings.get('checkpoint_dir', 'checkpoints')}\n"
    log_content += f"  Resume From: {safe_settings.get('resume_from', 'None')}\n\n"
    
    # Add Gemini API settings (without the key)
    log_content += "Gemini API Settings:\n"
    log_content += f"  Using Gemini API: {bool('gemini_api_key' in settings and settings['gemini_api_key'])}\n"
    log_content += f"  Number of Seed URLs: {safe_settings.get('num_seed_urls', 5)}\n\n"
    
    # Add database settings
    log_content += "Database Settings:\n"
    log_content += f"  Use Database: {safe_settings.get('use_database', False)}\n"
    log_content += f"  Database Path: {safe_settings.get('db_path', 'crawler.db')}\n\n"
    
    # Write to log file
    with open(log_filepath, 'w') as f:
        f.write(log_content)
    
    print(f"Settings saved to log file: {log_filepath}")
    return log_filepath

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Keyword-based web crawler')
    
    # Basic options
    parser.add_argument('--keywords', '-k', type=str, help='Keywords to search for (comma or space separated)')
    parser.add_argument('--seed-urls', '-s', type=str, help='Seed URLs to start crawling from (comma separated)')
    parser.add_argument('--max-depth', '-d', type=int, default=3, help='Maximum crawl depth (default: 3)')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests in seconds (default: 1.0)')
    parser.add_argument('--output', '-o', type=str, help='Output file to save results (JSON format)')
    parser.add_argument('--user-agent', type=str, default='WebCrawler/1.0 (Educational Project)',
                        help='Custom User-Agent string to use for requests')
    
    # Advanced keyword processing options
    keyword_group = parser.add_argument_group('Keyword Processing Options')
    keyword_group.add_argument('--use-stemming', action='store_true', help='Use stemming for keyword processing')
    keyword_group.add_argument('--use-lemmatization', action='store_true', help='Use lemmatization for keyword processing')
    keyword_group.add_argument('--remove-stopwords', action='store_true', help='Remove stopwords during keyword processing')
    keyword_group.add_argument('--regex-pattern', type=str, help='Use a regular expression pattern for matching')
    
    # Content matching options
    matching_group = parser.add_argument_group('Content Matching Options')
    matching_group.add_argument('--use-tfidf', action='store_true', 
                               help='Use TF-IDF for content matching and relevance scoring')
    matching_group.add_argument('--min-relevance-score', type=float, default=0.03,
                               help='Minimum relevance score for a page to be considered relevant (0.0-1.0)')
    
    # Domain filtering options
    domain_group = parser.add_argument_group('Domain Filtering Options')
    domain_group.add_argument('--stay-in-domain', action='store_true',
                             help='Only crawl pages within the same domain as the seed URLs')
    domain_group.add_argument('--allowed-domains', type=str,
                             help='Comma-separated list of domains to allow crawling (e.g., python.org,wikipedia.org)')
    domain_group.add_argument('--excluded-domains', type=str,
                             help='Comma-separated list of domains to exclude from crawling')
    
    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument('--output-format', type=str, choices=['json', 'csv'], default='json',
                             help='Format for output file (default: json)')
    output_group.add_argument('--pretty-print', action='store_true',
                             help='Pretty print JSON output (only applies to JSON format)')
    output_group.add_argument('--include-content', action='store_true',
                             help='Include page content in output (increases file size)')
    
    # Checkpoint options
    checkpoint_group = parser.add_argument_group('Checkpoint Options')
    checkpoint_group.add_argument('--checkpoint-interval', type=int, default=300, 
                        help='Interval in seconds between checkpoints (default: 300 seconds/5 minutes)')
    checkpoint_group.add_argument('--checkpoint-dir', type=str, default='checkpoints',
                        help='Directory to store checkpoint files (default: checkpoints)')
    checkpoint_group.add_argument('--resume-from', type=str, 
                        help='Resume crawling from a checkpoint file')
    checkpoint_group.add_argument('--list-checkpoints', action='store_true',
                        help='List available checkpoint files and exit')
    
    # Gemini API options
    gemini_group = parser.add_argument_group('Gemini API Options')
    gemini_group.add_argument('--gemini-api-key', type=str,
                             help='Google Gemini API key for generating smart seed URLs')
    gemini_group.add_argument('--generate-seed-urls', action='store_true',
                             help='Generate seed URLs using Google Gemini API')
    gemini_group.add_argument('--num-seed-urls', type=int, default=5,
                             help='Number of seed URLs to generate (default: 5)')
    
    # Database options
    db_group = parser.add_argument_group('Database Options')
    db_group.add_argument('--use-database', action='store_true',
                         help='Store crawl results in a SQLite database')
    db_group.add_argument('--db-path', type=str, default='crawler.db',
                         help='Path to the SQLite database file (default: crawler.db)')
    db_group.add_argument('--query-db', action='store_true',
                         help='Query the database instead of crawling')
    db_group.add_argument('--export-db', type=str,
                         help='Export database to a file (specify output file)')
    db_group.add_argument('--export-format', type=str, choices=['json', 'csv'], default='json',
                         help='Format for database export (default: json)')
    db_group.add_argument('--min-score', type=float, default=0.0,
                         help='Minimum relevance score for database queries (0.0-1.0)')
    db_group.add_argument('--limit', type=int, default=100,
                         help='Maximum number of results to return from database queries')
    db_group.add_argument('--vacuum-db', action='store_true',
                         help='Vacuum the database to reclaim space')
    db_group.add_argument('--db-stats', action='store_true',
                         help='Show database statistics')
    
    # Utility options
    utility_group = parser.add_argument_group('Utility Options')
    utility_group.add_argument('--download-nltk', action='store_true', 
                              help='Download required NLTK data packages')
    utility_group.add_argument('--verbose', '-v', action='count', default=0,
                              help='Increase verbosity level (use multiple times for more verbosity)')
    utility_group.add_argument('--log-dir', type=str, default='logs',
                              help='Directory to store log files (default: logs)')
    utility_group.add_argument('--no-log', action='store_true',
                              help='Disable logging of settings')
    
    return parser.parse_args()

def list_checkpoints(checkpoint_dir):
    """List available checkpoint files."""
    if not os.path.exists(checkpoint_dir):
        print(f"Checkpoint directory '{checkpoint_dir}' does not exist.")
        return
    
    checkpoints = [f for f in os.listdir(checkpoint_dir) if f.startswith("crawler_checkpoint_")]
    
    if not checkpoints:
        print(f"No checkpoint files found in '{checkpoint_dir}'.")
        return
    
    print(f"Available checkpoint files in '{checkpoint_dir}':")
    
    # Sort checkpoints by modification time (newest first)
    checkpoints.sort(key=lambda f: os.path.getmtime(os.path.join(checkpoint_dir, f)), reverse=True)
    
    for i, checkpoint in enumerate(checkpoints, 1):
        checkpoint_path = os.path.join(checkpoint_dir, checkpoint)
        mod_time = os.path.getmtime(checkpoint_path)
        size = os.path.getsize(checkpoint_path) / 1024  # Size in KB
        
        # Try to extract checkpoint type and timestamp from filename
        parts = checkpoint.split('_')
        checkpoint_type = parts[2] if len(parts) > 2 else "unknown"
        
        print(f"{i}. {checkpoint}")
        print(f"   Type: {checkpoint_type}")
        print(f"   Modified: {os.path.getmtime(checkpoint_path)}")
        print(f"   Size: {size:.2f} KB")
        
        # Try to read some basic info from the checkpoint
        try:
            with open(checkpoint_path, 'r') as f:
                data = json.load(f)
                print(f"   URLs visited: {len(data.get('visited', []))}")
                print(f"   URLs in queue: {len(data.get('queue', []))}")
                print(f"   Results: {len(data.get('results', []))}")
                print(f"   Timestamp: {data.get('timestamp', 'unknown')}")
        except Exception as e:
            print(f"   Error reading checkpoint data: {e}")
        
        print()

def save_results_to_file(results, output_file, output_format='json', pretty_print=False, include_content=False):
    """
    Save crawl results to a file.
    
    Args:
        results (list): List of result dictionaries
        output_file (str): Path to the output file
        output_format (str): Format of the output file ('json' or 'csv')
        pretty_print (bool): Whether to pretty print JSON output
        include_content (bool): Whether to include page content in output
    """
    try:
        # Remove content field if not requested
        if not include_content:
            for result in results:
                if 'content' in result:
                    del result['content']
        
        if output_format == 'json':
            with open(output_file, 'w') as f:
                if pretty_print:
                    json.dump(results, f, indent=2)
                else:
                    json.dump(results, f)
            print(f"Results saved to {output_file} in JSON format")
        
        elif output_format == 'csv':
            import csv
            with open(output_file, 'w', newline='') as f:
                # Determine fieldnames from the first result, or use defaults
                if results:
                    fieldnames = list(results[0].keys())
                else:
                    fieldnames = ['url', 'title', 'relevance_score']
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
            print(f"Results saved to {output_file} in CSV format")
        
        else:
            print(f"Unsupported output format: {output_format}")
    
    except Exception as e:
        print(f"Error saving results to file: {e}")

def filter_url_by_domain(url, allowed_domains=None, excluded_domains=None, stay_in_domain=False, seed_domains=None):
    """
    Check if a URL should be crawled based on domain filtering rules.
    
    Args:
        url (str): The URL to check
        allowed_domains (list): List of allowed domains
        excluded_domains (list): List of excluded domains
        stay_in_domain (bool): Whether to stay in the same domain as the seed URLs
        seed_domains (list): List of domains from seed URLs
        
    Returns:
        bool: True if the URL should be crawled, False otherwise
    """
    from urllib.parse import urlparse
    
    # Extract domain from URL
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    
    # Check if domain is in excluded domains
    if excluded_domains and domain in excluded_domains:
        return False
    
    # Check if domain is in allowed domains
    if allowed_domains and domain not in allowed_domains:
        return False
    
    # Check if we should stay in the same domain as the seed URLs
    if stay_in_domain and seed_domains and domain not in seed_domains:
        return False
    
    return True

def query_database(db_manager, args):
    """
    Query the database and display results.
    
    Args:
        db_manager (DatabaseManager): Database manager instance
        args (Namespace): Command line arguments
    """
    if args.db_stats:
        # Show database statistics
        stats = db_manager.get_crawl_statistics()
        print("\nDatabase Statistics:")
        print("===================")
        print(f"Total pages: {stats['total_pages']}")
        print(f"Average relevance score: {stats['avg_relevance']:.4f}")
        print(f"Total crawl sessions: {stats['total_sessions']}")
        print(f"Total crawl time: {stats['total_time_seconds'] / 60:.2f} minutes")
        return
    
    if args.export_db:
        # Export database to file
        if args.export_format == 'json':
            count = db_manager.export_to_json(args.export_db, args.limit)
            print(f"Exported {count} pages to {args.export_db} in JSON format")
        elif args.export_format == 'csv':
            count = db_manager.export_to_csv(args.export_db, args.limit)
            print(f"Exported {count} pages to {args.export_db} in CSV format")
        return
    
    if args.vacuum_db:
        # Vacuum the database
        if db_manager.vacuum_database():
            print("Database vacuumed successfully")
        else:
            print("Failed to vacuum database")
        return
    
    # Query for relevant pages
    pages = db_manager.get_relevant_pages(args.limit, 0, args.min_score)
    
    print("\nRelevant Pages from Database:")
    print("============================")
    
    if not pages:
        print("No relevant pages found in the database.")
    else:
        for i, page in enumerate(pages, 1):
            print(f"{i}. {page['title']}")
            print(f"   URL: {page['url']}")
            print(f"   Relevance Score: {page['relevance_score']:.4f}")
            print(f"   Depth: {page['depth']}")
            print(f"   Crawl Time: {page['crawl_time']}")
            if 'keywords_matched' in page and page['keywords_matched']:
                print(f"   Keywords Matched: {', '.join(page['keywords_matched'])}")
            print()
    
    # Show crawl sessions
    sessions = db_manager.get_crawl_sessions()
    
    print("\nRecent Crawl Sessions:")
    print("====================")
    
    if not sessions:
        print("No crawl sessions found in the database.")
    else:
        for i, session in enumerate(sessions, 1):
            print(f"{i}. Session ID: {session['id']}")
            print(f"   Start Time: {session['start_time']}")
            print(f"   End Time: {session['end_time'] or 'In progress'}")
            print(f"   Keywords: {', '.join(session['keywords'])}")
            print(f"   Pages Crawled: {session['pages_crawled']}")
            print(f"   Relevant Pages Found: {session['relevant_pages_found']}")
            print()

def main(passed_args=None):
    """Main function."""
    # Use passed args if provided, otherwise parse from command line
    args = passed_args if passed_args is not None else parse_arguments()
    
    # Set verbosity level
    verbosity = args.verbose
    
    # Create checkpoint directory if it doesn't exist
    if not os.path.exists(args.checkpoint_dir):
        os.makedirs(args.checkpoint_dir)
    
    # Initialize database manager if requested
    db_manager = None
    if args.use_database or args.query_db or args.export_db or args.vacuum_db or args.db_stats:
        db_manager = DatabaseManager(args.db_path)
        if verbosity > 0:
            print(f"Using database: {args.db_path}")
    
    # Handle database query mode
    if args.query_db or args.export_db or args.vacuum_db or args.db_stats:
        if not db_manager:
            print("Error: Database manager not initialized.")
            return
        query_database(db_manager, args)
        return
    
    # List checkpoints if requested
    if args.list_checkpoints:
        list_checkpoints(args.checkpoint_dir)
        return
    
    # Download NLTK data if requested
    if args.download_nltk:
        download_nltk_data()
        print("NLTK data downloaded successfully.")
        return
    
    # Interactive mode if no keywords provided
    if not args.keywords and not args.resume_from:
        print("Web Crawler - Phase 3")
        print("=====================")
        keywords_input = input("Enter keywords (separated by spaces or commas): ")
    else:
        keywords_input = args.keywords
    
    # If resuming from checkpoint, we might not need keywords
    if not keywords_input and not args.resume_from:
        print("No keywords provided and not resuming from checkpoint. Exiting.")
        return
    
    # Process keywords if provided
    if keywords_input:
        # Process keywords
        keyword_processor = KeywordProcessor(
            use_stemming=args.use_stemming,
            use_lemmatization=args.use_lemmatization,
            remove_stopwords=args.remove_stopwords
        )
        keywords = keyword_processor.process_input(keywords_input)
        
        if not keywords:
            print("No valid keywords provided. Exiting.")
            return
        
        print(f"Searching for: {', '.join(keywords)}")
    else:
        # We'll get keywords from the checkpoint
        keywords = []
    
    # Get seed URLs
    seed_urls = []
    
    # Check if we should generate seed URLs using Gemini API
    if args.generate_seed_urls and args.gemini_api_key:
        if verbosity > 0:
            print(f"Generating seed URLs using Google Gemini API...")
        seed_urls = generate_seed_urls_with_gemini(
            keywords, 
            args.gemini_api_key, 
            num_urls=args.num_seed_urls
        )
    # If seed URLs are provided via command line
    elif args.seed_urls:
        seed_urls = [url.strip() for url in args.seed_urls.split(',')]
    # If not resuming from checkpoint and no seed URLs provided, use default seed URLs
    elif not args.resume_from:
        # Use generic default seed URLs instead of topic-specific ones
        seed_urls = [
            "https://en.wikipedia.org/wiki/Main_Page",
            "https://www.python.org/",
            "https://news.ycombinator.com/",
            "https://github.com/",
            "https://stackoverflow.com/"
        ]
        print("No seed URLs provided. Using default seed URLs.")
    
    # Process domain filtering options
    allowed_domains = None
    if args.allowed_domains:
        allowed_domains = [domain.strip() for domain in args.allowed_domains.split(',')]
        if verbosity > 0:
            print(f"Allowed domains: {', '.join(allowed_domains)}")
    
    excluded_domains = None
    if args.excluded_domains:
        excluded_domains = [domain.strip() for domain in args.excluded_domains.split(',')]
        if verbosity > 0:
            print(f"Excluded domains: {', '.join(excluded_domains)}")
    
    seed_domains = None
    if args.stay_in_domain:
        from urllib.parse import urlparse
        seed_domains = [urlparse(url).netloc for url in seed_urls]
        if verbosity > 0:
            print(f"Staying in seed domains: {', '.join(seed_domains)}")
    
    if not args.resume_from:
        print(f"Starting crawl from {len(seed_urls)} seed URLs")
    
    # Prepare settings for logging
    if not args.no_log:
        settings = {
            'keywords': keywords,
            'seed_urls': seed_urls,
            'max_depth': args.max_depth,
            'delay': args.delay,
            'use_stemming': args.use_stemming,
            'use_lemmatization': args.use_lemmatization,
            'remove_stopwords': args.remove_stopwords,
            'checkpoint_interval': args.checkpoint_interval,
            'checkpoint_dir': args.checkpoint_dir,
            'use_tfidf': args.use_tfidf,
            'min_relevance_score': args.min_relevance_score,
            'user_agent': args.user_agent,
            'stay_in_domain': args.stay_in_domain,
            'allowed_domains': allowed_domains,
            'excluded_domains': excluded_domains,
            'regex_pattern': args.regex_pattern,
            'gemini_api_key': args.gemini_api_key,
            'num_seed_urls': args.num_seed_urls,
            'resume_from': args.resume_from,
            'use_database': args.use_database,
            'db_path': args.db_path if args.use_database else None
        }
        
        # Save settings to log file
        save_settings_to_log(settings, args.log_dir)
    
    # Create and run crawler
    crawler = WebCrawler(
        seed_urls=seed_urls, 
        keywords=keywords, 
        max_depth=args.max_depth, 
        delay=args.delay,
        use_stemming=args.use_stemming,
        use_lemmatization=args.use_lemmatization,
        remove_stopwords=args.remove_stopwords,
        checkpoint_interval=args.checkpoint_interval,
        checkpoint_dir=args.checkpoint_dir,
        use_tfidf=args.use_tfidf,
        min_relevance_score=args.min_relevance_score,
        user_agent=args.user_agent,
        stay_in_domain=args.stay_in_domain,
        allowed_domains=allowed_domains,
        excluded_domains=excluded_domains,
        regex_pattern=args.regex_pattern,
        gemini_api_key=args.gemini_api_key,
        verbose=args.verbose,
        db_manager=db_manager
    )
    
    # Run the crawler
    print(f"Checkpoints will be saved every {args.checkpoint_interval} seconds to '{args.checkpoint_dir}'")
    if args.use_tfidf:
        print(f"Using TF-IDF for content matching with minimum relevance score: {args.min_relevance_score}")
    if args.regex_pattern:
        print(f"Using regex pattern for matching: {args.regex_pattern}")
    if args.use_database:
        print(f"Storing results in database: {args.db_path}")
    print("Press Ctrl+C to stop crawling and save a checkpoint")
    
    results = crawler.crawl(resume_from_checkpoint=args.resume_from)
    
    # Display results
    print("\nResults:")
    print("========")
    
    if not results:
        print("No relevant pages found.")
    else:
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            if 'relevance_score' in result and args.use_tfidf:
                print(f"   Relevance Score: {result['relevance_score']:.4f}")
            if 'depth' in result:
                print(f"   Depth: {result['depth']}")
            if 'crawl_time' in result:
                print(f"   Crawl Time: {result['crawl_time']}")
            print()
    
    print(f"Crawling complete. Visited {len(crawler.visited)} pages.")
    
    # Save results to file if requested
    if args.output:
        save_results_to_file(
            results, 
            args.output, 
            output_format=args.output_format, 
            pretty_print=args.pretty_print,
            include_content=args.include_content
        )
    
    # Show database statistics if using database
    if args.use_database and db_manager:
        stats = db_manager.get_crawl_statistics()
        print("\nDatabase Statistics:")
        print("===================")
        print(f"Total pages in database: {stats['total_pages']}")
        print(f"Average relevance score: {stats['avg_relevance']:.4f}")
        print(f"Total crawl sessions: {stats['total_sessions']}")
        print(f"Total crawl time: {stats['total_time_seconds'] / 60:.2f} minutes")

if __name__ == "__main__":
    main()