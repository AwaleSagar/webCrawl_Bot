#!/usr/bin/env python3
"""
Test script for the web crawler.
This script tests the basic functionality of the web crawler.
"""

import sys
import os
import unittest

# Add the src directory to the path so we can import modules correctly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Now import the modules from the current directory
from crawler import WebCrawler
from keyword_processor import KeywordProcessor, download_nltk_data

class TestCrawler(unittest.TestCase):
    """Test cases for the WebCrawler class."""
    
    def test_crawler_initialization(self):
        """Test that the crawler initializes correctly."""
        # Test keywords
        keywords_input = "python programming"
        
        # Process keywords
        keyword_processor = KeywordProcessor()
        keywords = keyword_processor.process_input(keywords_input)
        
        # Test with a single seed URL and limited depth
        seed_urls = ["https://www.python.org/"]
        max_depth = 1
        delay = 1
        
        # Create crawler
        crawler = WebCrawler(seed_urls, keywords, max_depth=max_depth, delay=delay)
        
        # Assert initialization was correct
        self.assertEqual(crawler.seed_urls, seed_urls)
        self.assertEqual(crawler.max_depth, max_depth)
        self.assertEqual(crawler.delay, delay)
        self.assertEqual(crawler.keywords, keywords)

def test_crawler():
    """Test the web crawler with a simple example."""
    print("Testing Web Crawler")
    print("==================")
    
    # Test keywords
    keywords_input = "python programming"
    
    # Process keywords
    keyword_processor = KeywordProcessor()
    keywords = keyword_processor.process_input(keywords_input)
    
    print(f"Keywords: {', '.join(keywords)}")
    
    # Test with a single seed URL and limited depth
    seed_urls = ["https://www.python.org/"]
    max_depth = 1
    delay = 1
    
    print(f"Seed URL: {seed_urls[0]}")
    print(f"Max depth: {max_depth}")
    
    # Create and run crawler
    crawler = WebCrawler(seed_urls, keywords, max_depth=max_depth, delay=delay)
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
    
    return len(results) > 0

if __name__ == "__main__":
    success = test_crawler()
    sys.exit(0 if success else 1) 