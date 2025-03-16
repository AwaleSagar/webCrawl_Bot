#!/usr/bin/env python3
"""
Web Crawler - Main Module
This module implements a keyword-based web crawler that searches for relevant web pages
based on user-provided keywords.
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from collections import deque
from urllib.parse import urljoin, urlparse, urlunparse
import nltk
from nltk.tokenize import word_tokenize
import urllib.robotparser
from keyword_processor import KeywordProcessor
import json
import os
import datetime
import threading
import signal
import sys
import math
from collections import Counter
import numpy as np
import logging
from urllib.robotparser import RobotFileParser
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Configure logging
def setup_logging(verbose=False):
    """
    Set up logging configuration.
    
    Args:
        verbose (bool): Whether to enable verbose logging
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Create logger
    logger = logging.getLogger('webcrawler')
    logger.setLevel(log_level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

# Create logger
logger = logging.getLogger('webcrawler')

def generate_seed_urls_with_gemini(keywords, api_key, num_urls=5):
    """
    Generate seed URLs using Google Gemini API based on user keywords.
    
    Args:
        keywords (list): List of keywords to use for generating seed URLs
        api_key (str): Google Gemini API key
        num_urls (int): Number of seed URLs to generate
        
    Returns:
        list: List of generated seed URLs
    """
    if not api_key:
        logger.warning("No Gemini API key provided. Using default seed URLs.")
        return [
            "https://en.wikipedia.org/wiki/Web_crawler",
            "https://www.python.org/",
            "https://news.ycombinator.com/"
        ]
    
    # Prepare the prompt for Gemini
    keywords_str = ", ".join(keywords)
    prompt = f"""Generate {num_urls} relevant and high-quality website URLs (full URLs including https://) 
    that would be good starting points for a web crawler searching for information about: {keywords_str}.
    
    Only return the URLs, one per line, without any additional text or explanation.
    Make sure these are real, existing websites that are likely to have relevant content and good outgoing links.
    """
    
    # Prepare the API request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        # Make the API request
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        # Check for HTTP errors
        if response.status_code != 200:
            logger.error(f"Gemini API error: HTTP {response.status_code} - {response.text}")
            raise Exception(f"Gemini API returned status code {response.status_code}")
        
        # Parse the response
        result = response.json()
        
        # Log the raw JSON response
        _log_gemini_response(result, keywords_str)
        
        # Check for API errors
        if 'error' in result:
            logger.error(f"Gemini API error: {result['error']}")
            raise Exception(f"Gemini API error: {result['error'].get('message', 'Unknown error')}")
        
        # Extract the generated text
        if 'candidates' in result and len(result['candidates']) > 0:
            if 'content' not in result['candidates'][0]:
                logger.error("Gemini API response missing content field")
                raise Exception("Unexpected API response format: missing content field")
                
            if 'parts' not in result['candidates'][0]['content']:
                logger.error("Gemini API response missing parts field")
                raise Exception("Unexpected API response format: missing parts field")
                
            if not result['candidates'][0]['content']['parts']:
                logger.error("Gemini API response has empty parts array")
                raise Exception("Unexpected API response format: empty parts array")
                
            generated_text = result['candidates'][0]['content']['parts'][0]['text']
            
            # Extract URLs from the generated text
            urls = []
            for line in generated_text.strip().split('\n'):
                line = line.strip()
                if line.startswith('http'):
                    urls.append(line)
            
            # Validate URLs
            valid_urls = []
            for url in urls:
                try:
                    parsed = urlparse(url)
                    if parsed.scheme in ('http', 'https') and parsed.netloc:
                        valid_urls.append(url)
                except Exception as e:
                    logger.warning(f"Invalid URL from Gemini API: {url} - {e}")
                    continue
            
            if valid_urls:
                logger.info(f"Generated {len(valid_urls)} seed URLs using Gemini API")
                for url in valid_urls:
                    logger.debug(f"  - {url}")
                return valid_urls
            else:
                logger.warning("Gemini API did not generate any valid URLs")
        else:
            logger.error("Gemini API response missing candidates")
    
    except requests.exceptions.Timeout:
        logger.error("Gemini API request timed out")
    except requests.exceptions.ConnectionError:
        logger.error("Connection error when calling Gemini API")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error when calling Gemini API: {e}")
    except json.JSONDecodeError:
        logger.error("Failed to parse Gemini API response as JSON")
    except Exception as e:
        logger.error(f"Error generating seed URLs with Gemini API: {e}")
    
    logger.warning("Failed to generate seed URLs with Gemini API. Using default seed URLs.")
    return [
        "https://en.wikipedia.org/wiki/Web_crawler",
        "https://www.python.org/",
        "https://news.ycombinator.com/"
    ]

def _log_gemini_response(response_json, keywords):
    """
    Log the raw JSON response from the Gemini API to a file.
    
    Args:
        response_json (dict): The JSON response from the Gemini API
        keywords (str): The keywords used in the query
    """
    try:
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(os.getcwd(), "gemini_logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Create a timestamped filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_keywords = re.sub(r'[^\w\s-]', '', keywords).replace(' ', '_')[:30]
        filename = f"gemini_response_{timestamp}_{safe_keywords}.json"
        filepath = os.path.join(log_dir, filename)
        
        # Write the response to the file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(response_json, f, indent=2, ensure_ascii=False)
            
        print(f"Gemini API response logged to {filepath}")
    except Exception as e:
        print(f"Failed to log Gemini API response: {e}")

class WebCrawler:
    def __init__(self, seed_urls, keywords, max_depth=3, delay=1, 
                 use_stemming=False, use_lemmatization=False, remove_stopwords=False,
                 checkpoint_interval=300, checkpoint_dir="checkpoints",
                 use_tfidf=False, min_relevance_score=0.1,
                 user_agent="WebCrawler/1.0 (Educational Project)",
                 stay_in_domain=False, allowed_domains=None, excluded_domains=None,
                 regex_pattern=None, gemini_api_key=None, verbose=False,
                 db_manager=None):
        """
        Initialize the web crawler with seed URLs and keywords.
        
        Args:
            seed_urls (list): List of initial URLs to start crawling from
            keywords (list): List of keywords to search for in web pages
            max_depth (int): Maximum depth to crawl
            delay (int): Delay between requests in seconds
            use_stemming (bool): Whether to use stemming for keyword processing
            use_lemmatization (bool): Whether to use lemmatization for keyword processing
            remove_stopwords (bool): Whether to remove stopwords during keyword processing
            checkpoint_interval (int): Interval in seconds between checkpoints (default: 300 seconds/5 minutes)
            checkpoint_dir (str): Directory to store checkpoint files
            use_tfidf (bool): Whether to use TF-IDF for content matching
            min_relevance_score (float): Minimum relevance score for a page to be considered relevant (0.0-1.0)
            user_agent (str): Custom User-Agent string to use for requests
            stay_in_domain (bool): Whether to stay in the same domain as the seed URLs
            allowed_domains (list): List of allowed domains to crawl
            excluded_domains (list): List of excluded domains to avoid
            regex_pattern (str): Regular expression pattern to use for matching
            gemini_api_key (str): Google Gemini API key for generating seed URLs
            verbose (bool): Whether to enable verbose logging
            db_manager (DatabaseManager): Database manager for storing crawled pages
        """
        # Set up logging
        self.logger = setup_logging(verbose)
        
        # Validate checkpoint interval
        if checkpoint_interval < 60:
            self.logger.warning(f"Checkpoint interval {checkpoint_interval} seconds is very short. Setting to 60 seconds.")
            checkpoint_interval = 60
        elif checkpoint_interval > 3600:
            self.logger.warning(f"Checkpoint interval {checkpoint_interval} seconds is very long. Setting to 3600 seconds.")
            checkpoint_interval = 3600
        
        # Initialize crawler parameters
        self.seed_urls = seed_urls
        self.keywords = keywords
        self.max_depth = max_depth
        self.delay = delay
        self.checkpoint_interval = checkpoint_interval
        self.checkpoint_dir = checkpoint_dir
        self.use_tfidf = use_tfidf
        self.min_relevance_score = min_relevance_score
        self.user_agent = user_agent
        self.stay_in_domain = stay_in_domain
        self.allowed_domains = allowed_domains
        self.excluded_domains = excluded_domains
        self.regex_pattern = regex_pattern
        self.gemini_api_key = gemini_api_key
        self.verbose = verbose
        self.db_manager = db_manager
        self.crawl_session_id = None
        
        # Extract domains from seed URLs if staying in domain
        self.seed_domains = None
        if self.stay_in_domain:
            self.seed_domains = [urlparse(url).netloc for url in seed_urls]
        
        # Initialize crawler state
        self.visited = set()
        self.queue = deque()
        self.results = []
        self.robot_parsers = {}
        self.domain_access_times = {}
        self.crawl_in_progress = False
        self.checkpoint_timer = None
        self.document_frequencies = Counter()
        self.total_documents = 0
        
        # Initialize keyword processor
        self.keyword_processor = KeywordProcessor(
            use_stemming=use_stemming,
            use_lemmatization=use_lemmatization,
            remove_stopwords=remove_stopwords
        )
        
        # Add seed URLs to the queue
        for url in seed_urls:
            self.queue.append((url, 0))  # (url, depth)
        
        # Set up signal handlers for graceful shutdown
        self._setup_signal_handlers()
        
        # Create checkpoint directory if it doesn't exist
        if not os.path.exists(checkpoint_dir):
            os.makedirs(checkpoint_dir)
            self.logger.info(f"Created checkpoint directory: {checkpoint_dir}")
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(sig, frame):
            self.logger.info("\nReceived interrupt signal. Saving checkpoint and exiting...")
            try:
                self._cleanup()
                self.logger.info("Cleanup completed successfully.")
            except Exception as e:
                self.logger.error(f"Error during cleanup: {e}")
            finally:
                # Use os._exit instead of sys.exit to ensure immediate exit
                # without running additional cleanup code that might cause issues
                os._exit(0)
        
        # Register signal handlers
        try:
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        except (AttributeError, ValueError) as e:
            # Signal handling might not be available on all platforms
            self.logger.warning(f"Could not set up signal handlers: {e}")
    
    def _normalize_url(self, url):
        """Normalize URL to avoid crawling same content multiple times."""
        parsed = urlparse(url)
        # Convert to lowercase
        netloc = parsed.netloc.lower()
        path = parsed.path.lower()
        
        # Remove trailing slash if path is not root
        if path != "/" and path.endswith("/"):
            path = path[:-1]
            
        # Remove default ports
        if parsed.port in (80, 443):
            netloc = parsed.hostname
            
        # Remove common index files
        if path.endswith(("/index.html", "/index.htm", "/index.php")):
            path = path[:path.rfind("/") + 1]
            
        # Remove query parameters for common static files
        if path.endswith((".html", ".htm", ".php", ".asp", ".aspx")):
            query = ""
        else:
            query = parsed.query
            
        # Reconstruct URL
        return urlunparse((
            parsed.scheme,
            netloc,
            path,
            "",  # params
            query,
            ""   # fragment
        ))
    
    def _get_robot_parser(self, url):
        """
        Get or create a robot parser for the given URL's domain.
        
        Args:
            url (str): The URL to get a robot parser for
            
        Returns:
            RobotFileParser or None: The robot parser for the domain, or None if there was an error
        """
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # Return cached parser if available
            if domain in self.robot_parsers:
                return self.robot_parsers[domain]
            
            # Create a new parser
            robots_url = f"{parsed_url.scheme}://{domain}/robots.txt"
            parser = urllib.robotparser.RobotFileParser(robots_url)
            
            try:
                parser.read()
                self.robot_parsers[domain] = parser
                return parser
            except Exception as e:
                print(f"Error reading robots.txt for {domain}: {e}")
                # Create a permissive parser as fallback
                permissive_parser = urllib.robotparser.RobotFileParser()
                permissive_parser.allow_all = True
                self.robot_parsers[domain] = permissive_parser
                return permissive_parser
        
        except Exception as e:
            print(f"Error creating robot parser for {url}: {e}")
            # Return a permissive parser as fallback
            permissive_parser = urllib.robotparser.RobotFileParser()
            permissive_parser.allow_all = True
            return permissive_parser

    def _can_fetch(self, url):
        """
        Check if the URL can be fetched according to robots.txt.
        
        Args:
            url (str): The URL to check
            
        Returns:
            bool: True if the URL can be fetched, False otherwise
        """
        try:
            parser = self._get_robot_parser(url)
            if parser is None or getattr(parser, 'allow_all', False):
                return True
            
            return parser.can_fetch(self.user_agent, url)
        except Exception as e:
            print(f"Error checking robots.txt for {url}: {e}")
            # Default to allowing the fetch if there's an error
            return True
    
    def _should_crawl_domain(self, url):
        """
        Check if the URL's domain should be crawled based on domain filtering rules.
        
        Args:
            url (str): The URL to check
            
        Returns:
            bool: True if the domain should be crawled, False otherwise
        """
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Check if domain is in excluded domains
        if self.excluded_domains and domain in self.excluded_domains:
            return False
        
        # Check if domain is in allowed domains
        if self.allowed_domains and domain not in self.allowed_domains:
            return False
        
        # Check if we should stay in the same domain as the seed URLs
        if self.stay_in_domain and self.seed_domains and domain not in self.seed_domains:
            return False
        
        return True
    
    def _respect_domain_rate_limits(self, url):
        """
        Respect rate limits for the domain by adding a delay if needed.
        
        Args:
            url (str): The URL to check rate limits for
        """
        try:
            domain = urlparse(url).netloc
            current_time = time.time()
            
            # Check if we've accessed this domain before
            if domain in self.domain_access_times:
                last_access_time = self.domain_access_times[domain]
                elapsed = current_time - last_access_time
                
                # If we've accessed this domain recently, add a delay
                if elapsed < self.delay:
                    sleep_time = self.delay - elapsed
                    if sleep_time > 0:
                        self.logger.debug(f"Rate limiting: Waiting {sleep_time:.2f}s before accessing {domain} again")
                        time.sleep(sleep_time)
            
            # Update the last access time AFTER any necessary sleep
            self.domain_access_times[domain] = time.time()
        
        except Exception as e:
            self.logger.error(f"Error in rate limiting for {url}: {e}")
            # Default to adding the standard delay
            time.sleep(self.delay)
    
    def _is_relevant(self, content, url=None):
        """
        Check if the content is relevant based on keywords.
        
        Args:
            content (str): The content to check
            url (str, optional): The URL of the content
            
        Returns:
            If use_tfidf is True:
                tuple: (is_relevant, relevance_score)
            Otherwise:
                bool: True if the content is relevant, False otherwise
        """
        # If no content, not relevant
        if not content:
            return (False, 0.0) if self.use_tfidf else False
        
        # If regex pattern is provided, use it
        if self.regex_pattern:
            pattern = re.compile(self.regex_pattern, re.IGNORECASE)
            matches = pattern.search(content)
            if self.use_tfidf:
                # Return tuple of (is_relevant, score) where score is 1.0 if matched, 0.0 otherwise
                return (bool(matches), 1.0 if matches else 0.0)
            else:
                return bool(matches)
        
        # Use the keyword processor to check for keyword matches
        is_relevant = self.keyword_processor.is_relevant(content, self.keywords)
        
        # If using TF-IDF, calculate score
        if self.use_tfidf:
            # Simple scoring: 1.0 if relevant, 0.0 if not
            # In a real implementation, we would calculate a proper TF-IDF score
            score = 1.0 if is_relevant else 0.0
            return (is_relevant, score)
            
        return is_relevant
    
    def _extract_links(self, soup, base_url):
        """
        Extract links from a BeautifulSoup object.
        
        Args:
            soup (BeautifulSoup): The BeautifulSoup object
            base_url (str): The base URL for resolving relative links
            
        Returns:
            list: List of normalized absolute URLs
        """
        links = []
        
        if not soup or not base_url:
            return links
        
        try:
            # Find all anchor tags
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href'].strip()
                
                # Skip empty links, javascript, mailto, tel links, and anchors
                if not href or href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                    continue
                
                try:
                    # Convert relative URLs to absolute
                    absolute_url = urljoin(base_url, href)
                    
                    # Parse the URL
                    parsed_url = urlparse(absolute_url)
                    
                    # Skip non-HTTP/HTTPS URLs
                    if parsed_url.scheme not in ('http', 'https'):
                        continue
                    
                    # Remove fragments and normalize
                    normalized_url = urlunparse((
                        parsed_url.scheme,
                        parsed_url.netloc,
                        parsed_url.path,
                        parsed_url.params,
                        parsed_url.query,
                        ''  # Remove fragment
                    ))
                    
                    # Add to links if not already present
                    if normalized_url not in links:
                        links.append(normalized_url)
                
                except Exception as e:
                    # Log the error but continue processing other links
                    print(f"Error processing link {href} from {base_url}: {e}")
                    continue
        
        except Exception as e:
            print(f"Error extracting links from {base_url}: {e}")
        
        return links
    
    def _calculate_tfidf_scores(self):
        """Calculate TF-IDF scores for all documents."""
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        # Convert documents to strings for TfidfVectorizer
        doc_texts = [' '.join(doc) for doc in self.documents]
        
        # Create and fit TF-IDF vectorizer
        vectorizer = TfidfVectorizer(lowercase=True)
        tfidf_matrix = vectorizer.fit_transform(doc_texts)
        
        # Get feature names (words)
        feature_names = vectorizer.get_feature_names_out()
        
        return vectorizer, tfidf_matrix, feature_names
    
    def _schedule_checkpoint(self):
        """Schedule the next checkpoint."""
        # Cancel any existing timer
        if self.checkpoint_timer:
            try:
                self.checkpoint_timer.cancel()
            except:
                pass
        
        # Only schedule if crawling is in progress
        if self.crawl_in_progress:
            try:
                self.checkpoint_timer = threading.Timer(self.checkpoint_interval, self._auto_checkpoint)
                self.checkpoint_timer.daemon = True
                self.checkpoint_timer.start()
            except Exception as e:
                print(f"Error scheduling checkpoint: {e}")
    
    def _auto_checkpoint(self):
        """Save a checkpoint and schedule the next one."""
        try:
            if self.crawl_in_progress:
                print(f"\nAuto-saving checkpoint after {self.checkpoint_interval} seconds...")
                self._save_checkpoint("auto")
                # Schedule the next checkpoint
                self._schedule_checkpoint()
        except Exception as e:
            print(f"Error during auto checkpoint: {e}")
            # Try to reschedule even if there was an error
            self._schedule_checkpoint()
    
    def _save_checkpoint(self, checkpoint_type="auto"):
        """
        Save the current state of the crawler to a checkpoint file.
        
        Args:
            checkpoint_type (str): Type of checkpoint (auto, manual, etc.)
        
        Returns:
            str: Path to the saved checkpoint file
        """
        # Skip auto checkpoints if crawling is not in progress
        if not self.crawl_in_progress and checkpoint_type == "auto":
            return None
        
        if not os.path.exists(self.checkpoint_dir):
            os.makedirs(self.checkpoint_dir)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_filename = f"crawler_checkpoint_{checkpoint_type}_{timestamp}.json"
        checkpoint_path = os.path.join(self.checkpoint_dir, checkpoint_filename)
        
        # Create a copy of the crawler state without sensitive information
        checkpoint_data = {
            "timestamp": timestamp,
            "keywords": self.keywords,
            "seed_urls": self.seed_urls,
            "max_depth": self.max_depth,
            "delay": self.delay,
            "visited": list(self.visited),
            "queue": list(self.queue),
            "results": self.results,
            "use_stemming": self.keyword_processor.use_stemming,
            "use_lemmatization": self.keyword_processor.use_lemmatization,
            "remove_stopwords": self.keyword_processor.remove_stopwords,
            "use_tfidf": self.use_tfidf,
            "min_relevance_score": self.min_relevance_score,
            "document_frequencies": self.document_frequencies,
            "total_documents": self.total_documents,
            "user_agent": self.user_agent,
            "stay_in_domain": self.stay_in_domain,
            "allowed_domains": self.allowed_domains,
            "excluded_domains": self.excluded_domains,
            "regex_pattern": self.regex_pattern,
            "seed_domains": self.seed_domains
            # Deliberately not saving gemini_api_key for security reasons
        }
        
        try:
            with open(checkpoint_path, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            self.logger.info(f"Checkpoint saved to {checkpoint_path}")
            
            # Clean up old checkpoints
            self._cleanup_old_checkpoints()
            
            return checkpoint_path
        
        except Exception as e:
            self.logger.error(f"Error saving checkpoint: {e}")
            return None
    
    def _cleanup_old_checkpoints(self):
        """
        Clean up old checkpoint files, keeping only the most recent ones.
        
        This method keeps:
        - The 5 most recent auto checkpoints
        - All manual checkpoints
        - The most recent final checkpoint
        """
        try:
            if not os.path.exists(self.checkpoint_dir):
                return
            
            # Group checkpoint files by type
            auto_checkpoints = []
            manual_checkpoints = []
            final_checkpoints = []
            
            for filename in os.listdir(self.checkpoint_dir):
                if not filename.startswith("crawler_checkpoint_"):
                    continue
                    
                filepath = os.path.join(self.checkpoint_dir, filename)
                
                # Skip if not a file
                if not os.path.isfile(filepath):
                    continue
                    
                # Determine checkpoint type
                if "auto" in filename:
                    auto_checkpoints.append(filepath)
                elif "manual" in filename:
                    manual_checkpoints.append(filepath)
                elif "final" in filename:
                    final_checkpoints.append(filepath)
            
            # Sort checkpoints by modification time (newest first)
            auto_checkpoints.sort(key=os.path.getmtime, reverse=True)
            final_checkpoints.sort(key=os.path.getmtime, reverse=True)
            
            # Keep only the 5 most recent auto checkpoints
            for filepath in auto_checkpoints[5:]:
                os.remove(filepath)
                print(f"Removed old auto checkpoint: {os.path.basename(filepath)}")
            
            # Keep only the most recent final checkpoint
            for filepath in final_checkpoints[1:]:
                os.remove(filepath)
                print(f"Removed old final checkpoint: {os.path.basename(filepath)}")
        
        except Exception as e:
            print(f"Error cleaning up old checkpoints: {e}")
    
    def _recalculate_relevance_scores(self):
        """
        Recalculate relevance scores for all results using the current TF-IDF model.
        
        This is useful when we have collected more documents and want to update
        the relevance scores of previously found pages.
        """
        if not self.use_tfidf or not self.results:
            return
        
        print("Recalculating relevance scores for all results...")
        
        for result in self.results:
            # Skip if we don't have the content
            if 'content' not in result:
                continue
            
            # Process the content
            processed_content = self.keyword_processor.process_text(result['content'])
            
            # Calculate new score
            new_score = self._calculate_tfidf_score(processed_content)
            
            # Update the result
            result['relevance_score'] = new_score
        
        # Sort results by the new scores
        self.results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        print("Relevance scores recalculated.")
    
    def load_checkpoint(self, checkpoint_path):
        """
        Load crawler state from a checkpoint file.
        
        Args:
            checkpoint_path (str): Path to the checkpoint file
        
        Returns:
            bool: True if checkpoint was loaded successfully, False otherwise
        """
        try:
            with open(checkpoint_path, 'r') as f:
                checkpoint_data = json.load(f)
            
            # Restore crawler state
            self.keywords = checkpoint_data.get("keywords", self.keywords)
            self.seed_urls = checkpoint_data.get("seed_urls", self.seed_urls)
            self.max_depth = checkpoint_data.get("max_depth", self.max_depth)
            self.delay = checkpoint_data.get("delay", self.delay)
            self.visited = set(checkpoint_data.get("visited", []))
            
            # Ensure queue is a deque
            queue_data = checkpoint_data.get("queue", [])
            self.queue = deque(queue_data) if queue_data else deque()
            
            self.results = checkpoint_data.get("results", [])
            
            # Restore keyword processor settings
            use_stemming = checkpoint_data.get("use_stemming", self.keyword_processor.use_stemming)
            use_lemmatization = checkpoint_data.get("use_lemmatization", self.keyword_processor.use_lemmatization)
            remove_stopwords = checkpoint_data.get("remove_stopwords", self.keyword_processor.remove_stopwords)
            
            # Update keyword processor with restored settings
            self.keyword_processor.use_stemming = use_stemming
            self.keyword_processor.use_lemmatization = use_lemmatization
            self.keyword_processor.remove_stopwords = remove_stopwords
            
            self.use_tfidf = checkpoint_data.get("use_tfidf", self.use_tfidf)
            self.min_relevance_score = checkpoint_data.get("min_relevance_score", self.min_relevance_score)
            
            # Ensure document_frequencies is a Counter
            doc_freq_data = checkpoint_data.get("document_frequencies", {})
            self.document_frequencies = Counter(doc_freq_data)
            
            self.total_documents = checkpoint_data.get("total_documents", 0)
            self.user_agent = checkpoint_data.get("user_agent", self.user_agent)
            self.stay_in_domain = checkpoint_data.get("stay_in_domain", self.stay_in_domain)
            self.allowed_domains = checkpoint_data.get("allowed_domains", self.allowed_domains)
            self.excluded_domains = checkpoint_data.get("excluded_domains", self.excluded_domains)
            self.regex_pattern = checkpoint_data.get("regex_pattern", self.regex_pattern)
            self.seed_domains = checkpoint_data.get("seed_domains", self.seed_domains)
            # Note: gemini_api_key is not loaded from checkpoint for security reasons
            # It must be provided again when resuming
            
            print(f"Checkpoint loaded from {checkpoint_path}")
            print(f"Restored {len(self.visited)} visited URLs and {len(self.queue)} URLs in queue")
            
            return True
        
        except Exception as e:
            print(f"Error loading checkpoint: {e}")
            return False
    
    def _cleanup(self):
        """Clean up resources when crawler stops."""
        self.logger.info("Performing cleanup...")
        
        # Mark crawling as stopped
        self.crawl_in_progress = False
        
        # Cancel checkpoint timer
        if self.checkpoint_timer:
            try:
                self.checkpoint_timer.cancel()
                self.checkpoint_timer = None
                self.logger.debug("Checkpoint timer canceled.")
            except Exception as e:
                self.logger.error(f"Error canceling checkpoint timer: {e}")
        
        # Save final checkpoint
        try:
            checkpoint_path = self._save_checkpoint("final")
            if checkpoint_path:
                self.logger.info(f"Final checkpoint saved to {checkpoint_path}")
            else:
                self.logger.warning("Failed to save final checkpoint.")
        except Exception as e:
            self.logger.error(f"Error saving final checkpoint: {e}")
        
        self.logger.info("Cleanup completed.")
    
    # Extract text content - IMPROVED VERSION with better type checking
    def _extract_text_content(self, soup):
        """
        Extract text content from HTML safely with type checking.
        
        Args:
            soup (BeautifulSoup): BeautifulSoup object of the page
            
        Returns:
            str: Extracted text content
        """
        text_content = ''
        
        # Get title
        if soup.title and soup.title.string and isinstance(soup.title.string, str):
            text_content += soup.title.string + ' '
        
        # Get meta descriptions
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and 'content' in meta_desc.attrs and isinstance(meta_desc['content'], str):
            text_content += meta_desc['content'] + ' '
        
        # Get body text from important tags
        for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'span', 'div']):
            # Handle string content
            if tag.string and isinstance(tag.string, str) and len(tag.string.strip()) > 0:
                text_content += tag.string.strip() + ' '
            # Handle text content
            elif isinstance(tag.text, str) and len(tag.text.strip()) > 0:
                text_content += tag.text.strip() + ' '
        
        return text_content
    
    def crawl(self, resume_from_checkpoint=None):
        """
        Start the crawling process.
        
        Args:
            resume_from_checkpoint (str, optional): Path to a checkpoint file to resume from
            
        Returns:
            list: List of relevant pages found during the crawl
        """
        # Load checkpoint if specified
        if resume_from_checkpoint:
            if not self.load_checkpoint(resume_from_checkpoint):
                self.logger.warning("Failed to load checkpoint. Starting fresh crawl.")
        
        self.crawl_in_progress = True
        
        # Start a new crawl session in the database if available
        if self.db_manager:
            self.crawl_session_id = self.db_manager.start_crawl_session(self.keywords)
            self.logger.info(f"Started new crawl session with ID: {self.crawl_session_id}")
        
        # Schedule first checkpoint
        self._schedule_checkpoint()
        self.logger.info(f"Checkpoints will be automatically saved every {self.checkpoint_interval} seconds")
        
        # Counter for documents processed since last recalculation
        docs_since_recalc = 0
        
        try:
            while self.queue:
                url, depth = self.queue.popleft()
                
                # Skip if URL has been visited or depth exceeds max_depth
                if url in self.visited or depth > self.max_depth:
                    continue
                
                # Check domain filtering
                if not self._should_crawl_domain(url):
                    self.logger.debug(f"Skipping {url} (domain filtering)")
                    self.visited.add(url)
                    continue
                
                # Check robots.txt
                if not self._can_fetch(url):
                    self.logger.debug(f"Skipping {url} (disallowed by robots.txt)")
                    self.visited.add(url)
                    continue
                
                # Check if URL is already in database
                if self.db_manager and self.db_manager.is_url_crawled(url):
                    self.logger.debug(f"Skipping {url} (already in database)")
                    self.visited.add(url)
                    continue
                
                # Respect rate limits
                self._respect_domain_rate_limits(url)
                
                self.logger.info(f"Crawling: {url} (depth: {depth})")
                self.visited.add(url)
                
                try:
                    # Fetch the page
                    headers = {
                        'User-Agent': self.user_agent
                    }
                    response = requests.get(url, headers=headers, timeout=10)
                    response.raise_for_status()
                    
                    # Parse HTML
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract text content
                    text_content = soup.get_text(separator=' ', strip=True)
                    
                    # Check if page is relevant
                    relevance_result = self._is_relevant(text_content, url)
                    
                    if self.use_tfidf:
                        is_relevant, relevance_score = relevance_result
                    else:
                        is_relevant = relevance_result
                        relevance_score = 1.0 if is_relevant else 0.0
                    
                    # Get page title
                    title = soup.title.string if soup.title else url
                    title = title.strip() if title else url
                    
                    # Create a content snippet
                    content_snippet = text_content[:500] + "..." if len(text_content) > 500 else text_content
                    
                    # Determine which keywords were matched
                    matched_keywords = []
                    for keyword in self.keywords:
                        if keyword.lower() in text_content.lower():
                            matched_keywords.append(keyword)
                    
                    if is_relevant:
                        # Create result object
                        result = {
                            'url': url,
                            'title': title,
                            'relevance_score': relevance_score,
                            'depth': depth,
                            'crawl_time': datetime.datetime.now().isoformat(),
                            'content': text_content  # Store content for potential recalculation
                        }
                        self.results.append(result)
                        self.logger.info(f"Found relevant page: {title}")
                        
                        # Store in database if available
                        if self.db_manager:
                            self.db_manager.add_crawled_page(
                                url=url,
                                title=title,
                                content_snippet=content_snippet,
                                relevance_score=relevance_score,
                                depth=depth,
                                keywords_matched=matched_keywords
                            )
                        
                        # Increment document counter
                        docs_since_recalc += 1
                        
                        # Recalculate scores periodically if using TF-IDF
                        if self.use_tfidf and docs_since_recalc >= 10:
                            self._recalculate_relevance_scores()
                            docs_since_recalc = 0
                    
                    # Extract links if not at max depth
                    if depth < self.max_depth:
                        links = self._extract_links(soup, url)
                        for link in links:
                            if link not in self.visited:
                                self.queue.append((link, depth + 1))
                
                except Exception as e:
                    self.logger.error(f"Error crawling {url}: {e}")
        
        finally:
            # Ensure we clean up properly even if an exception occurs
            self._cleanup()
            
            # Final recalculation of scores if using TF-IDF
            if self.use_tfidf and docs_since_recalc > 0:
                self._recalculate_relevance_scores()
            
            # End crawl session in database if available
            if self.db_manager and self.crawl_session_id:
                self.db_manager.end_crawl_session(
                    crawl_id=self.crawl_session_id,
                    pages_crawled=len(self.visited),
                    relevant_pages_found=len(self.results)
                )
                self.logger.info(f"Ended crawl session with ID: {self.crawl_session_id}")
        
        # Sort results by relevance score if TF-IDF is enabled
        if self.use_tfidf:
            self.results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Remove content field from results to save memory
        for result in self.results:
            if 'content' in result:
                del result['content']
        
        return self.results

    def _calculate_tfidf_score(self, processed_text):
        """
        Calculate TF-IDF relevance score for the given processed text.
        
        Args:
            processed_text (str): The processed text to calculate score for
            
        Returns:
            float: The relevance score between 0.0 and 1.0
        """
        # If we don't have enough documents yet, use a simple keyword matching approach
        if self.total_documents < 10:  # Arbitrary threshold
            # Count how many keywords are found in the text
            keyword_count = sum(1 for keyword in self.keywords 
                               if keyword.lower() in processed_text.lower())
            # Simple score based on percentage of keywords found
            return min(1.0, keyword_count / max(1, len(self.keywords)))
        
        # Calculate term frequencies in this document
        term_freqs = Counter(word.lower() for word in processed_text.split())
        
        # Calculate TF-IDF score
        score = 0.0
        matched_terms = 0
        
        # Process each keyword
        for keyword in self.keywords:
            keyword_terms = self.keyword_processor.process_text(keyword).split()
            keyword_score = 0.0
            
            for term in keyword_terms:
                term = term.lower()
                if term in term_freqs:
                    # Term frequency in this document
                    tf = term_freqs[term]
                    
                    # Inverse document frequency
                    df = self.document_frequencies.get(term, 1)
                    idf = math.log(max(2, self.total_documents) / df)
                    
                    # TF-IDF score for this term
                    term_score = tf * idf
                    keyword_score += term_score
                    
        # Normalize by number of terms in the keyword
        if keyword_terms:
            keyword_score /= len(keyword_terms)
            if keyword_score > 0:
                matched_terms += 1
                score += keyword_score
        
        # Normalize the final score
        if matched_terms > 0:
            score /= matched_terms
            
            # Update document frequencies for future calculations
            for term, freq in term_freqs.items():
                self.document_frequencies[term] = self.document_frequencies.get(term, 0) + 1
            
            self.total_documents += 1
            
            # Normalize to 0-1 range (this is a heuristic, adjust as needed)
            normalized_score = min(1.0, score / 10.0)
            return normalized_score
        
        return 0.0

def process_keywords(keywords_input):
    """
    Process the user input keywords.
    
    Args:
        keywords_input (str): User input string containing keywords
        
    Returns:
        list: Processed list of keywords
    """
    # Split by commas or spaces
    if ',' in keywords_input:
        tokens = [k.strip() for k in keywords_input.split(',')]
    else:
        tokens = keywords_input.split()
    
    # Remove empty tokens and convert to lowercase
    return [token.lower() for token in tokens if token]


def main():
    """Main function to run the web crawler."""
    print("Web Crawler - Phase 2")
    print("=====================")
    
    # Get keywords from user
    keywords_input = input("Enter keywords (separated by spaces or commas): ")
    keywords = process_keywords(keywords_input)
    
    if not keywords:
        print("No valid keywords provided. Exiting.")
        return
    
    print(f"Searching for: {', '.join(keywords)}")
    
    # Ask for Gemini API key
    use_gemini = input("Do you want to use Google Gemini API to generate smart seed URLs? (Y/N): ").strip().lower()
    gemini_api_key = None
    
    if use_gemini == 'y' or use_gemini == 'yes':
        gemini_api_key = input("Enter your Google Gemini API key: ").strip()
        if not gemini_api_key:
            print("No API key provided. Using default seed URLs.")
            gemini_api_key = None
    
    # Generate seed URLs with Gemini API or use defaults
    if gemini_api_key:
        seed_urls = generate_seed_urls_with_gemini(keywords, gemini_api_key)
    else:
        # Define default seed URLs
        seed_urls = [
            "https://en.wikipedia.org/wiki/Web_crawler",
            "https://www.python.org/",
            "https://news.ycombinator.com/"
        ]
    
    # Create and run crawler
    crawler = WebCrawler(seed_urls, keywords, gemini_api_key=gemini_api_key)
    results = crawler.crawl()
    
    # Display results
    print("\nResults:")
    print("========")
    
    if not results:
        print("No relevant pages found.")
    else:
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print()
    
    print(f"Crawling complete. Visited {len(crawler.visited)} pages.")


if __name__ == "__main__":
    main()