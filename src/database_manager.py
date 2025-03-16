#!/usr/bin/env python3
"""
Database Manager for Web Crawler
Handles all database operations for storing and retrieving crawled data.
"""

import os
import sqlite3
import json
import datetime
from contextlib import contextmanager

class DatabaseManager:
    """Manages database operations for the web crawler."""
    
    def __init__(self, db_path="crawler.db"):
        """
        Initialize the database manager.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.initialize_database()
    
    def initialize_database(self):
        """Create database tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create crawled_pages table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS crawled_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                content_snippet TEXT,
                relevance_score REAL,
                depth INTEGER,
                crawl_time TIMESTAMP,
                keywords_matched TEXT
            )
            ''')
            
            # Create crawl_metadata table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS crawl_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                keywords TEXT,
                pages_crawled INTEGER,
                relevant_pages_found INTEGER
            )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_url ON crawled_pages(url)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_relevance ON crawled_pages(relevance_score)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_crawl_time ON crawled_pages(crawl_time)')
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        
        Yields:
            sqlite3.Connection: Database connection
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            # Return dictionary-like rows
            conn.row_factory = sqlite3.Row
            yield conn
        finally:
            if conn:
                conn.close()
    
    def start_crawl_session(self, keywords):
        """
        Start a new crawl session and return its ID.
        
        Args:
            keywords (list): List of keywords for this crawl
            
        Returns:
            int: ID of the created crawl session
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Convert keywords list to JSON string
            keywords_json = json.dumps(keywords)
            
            # Insert new crawl session
            cursor.execute('''
            INSERT INTO crawl_metadata 
            (start_time, keywords, pages_crawled, relevant_pages_found) 
            VALUES (?, ?, 0, 0)
            ''', (datetime.datetime.now().isoformat(), keywords_json))
            
            # Get the ID of the inserted row
            crawl_id = cursor.lastrowid
            conn.commit()
            
            return crawl_id
    
    def end_crawl_session(self, crawl_id, pages_crawled, relevant_pages_found):
        """
        Update a crawl session with end time and statistics.
        
        Args:
            crawl_id (int): ID of the crawl session
            pages_crawled (int): Total number of pages crawled
            relevant_pages_found (int): Number of relevant pages found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Update crawl session
            cursor.execute('''
            UPDATE crawl_metadata 
            SET end_time = ?, pages_crawled = ?, relevant_pages_found = ? 
            WHERE id = ?
            ''', (datetime.datetime.now().isoformat(), pages_crawled, relevant_pages_found, crawl_id))
            
            conn.commit()
    
    def add_crawled_page(self, url, title, content_snippet, relevance_score, depth, keywords_matched):
        """
        Add a crawled page to the database.
        
        Args:
            url (str): URL of the page
            title (str): Title of the page
            content_snippet (str): Snippet of the page content
            relevance_score (float): Relevance score (0.0-1.0)
            depth (int): Crawl depth
            keywords_matched (list): List of keywords matched in the content
            
        Returns:
            bool: True if the page was added, False if it already exists
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # Convert keywords_matched list to JSON string
                keywords_matched_json = json.dumps(keywords_matched)
                
                # Insert new page
                cursor.execute('''
                INSERT INTO crawled_pages 
                (url, title, content_snippet, relevance_score, depth, crawl_time, keywords_matched) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (url, title, content_snippet, relevance_score, depth, 
                      datetime.datetime.now().isoformat(), keywords_matched_json))
                
                conn.commit()
                return True
            
            except sqlite3.IntegrityError:
                # Page already exists (unique constraint violation)
                return False
    
    def update_crawled_page(self, url, title, content_snippet, relevance_score, depth, keywords_matched):
        """
        Update an existing crawled page in the database.
        
        Args:
            url (str): URL of the page
            title (str): Title of the page
            content_snippet (str): Snippet of the page content
            relevance_score (float): Relevance score (0.0-1.0)
            depth (int): Crawl depth
            keywords_matched (list): List of keywords matched in the content
            
        Returns:
            bool: True if the page was updated, False if it doesn't exist
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Convert keywords_matched list to JSON string
            keywords_matched_json = json.dumps(keywords_matched)
            
            # Update existing page
            cursor.execute('''
            UPDATE crawled_pages 
            SET title = ?, content_snippet = ?, relevance_score = ?, 
                depth = ?, crawl_time = ?, keywords_matched = ? 
            WHERE url = ?
            ''', (title, content_snippet, relevance_score, depth, 
                  datetime.datetime.now().isoformat(), keywords_matched_json, url))
            
            conn.commit()
            
            # Check if any rows were affected
            return cursor.rowcount > 0
    
    def get_crawled_page(self, url):
        """
        Get a crawled page from the database.
        
        Args:
            url (str): URL of the page
            
        Returns:
            dict: Page data or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Query for the page
            cursor.execute('SELECT * FROM crawled_pages WHERE url = ?', (url,))
            
            row = cursor.fetchone()
            
            if row:
                # Convert row to dictionary
                page = dict(row)
                
                # Parse JSON fields
                if 'keywords_matched' in page and page['keywords_matched']:
                    page['keywords_matched'] = json.loads(page['keywords_matched'])
                
                return page
            
            return None
    
    def is_url_crawled(self, url):
        """
        Check if a URL has already been crawled.
        
        Args:
            url (str): URL to check
            
        Returns:
            bool: True if the URL has been crawled, False otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Query for the URL
            cursor.execute('SELECT 1 FROM crawled_pages WHERE url = ? LIMIT 1', (url,))
            
            return cursor.fetchone() is not None
    
    def get_relevant_pages(self, limit=100, offset=0, min_score=0.0):
        """
        Get relevant pages from the database.
        
        Args:
            limit (int): Maximum number of pages to return
            offset (int): Offset for pagination
            min_score (float): Minimum relevance score
            
        Returns:
            list: List of relevant pages
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Query for relevant pages
            cursor.execute('''
            SELECT * FROM crawled_pages 
            WHERE relevance_score >= ? 
            ORDER BY relevance_score DESC 
            LIMIT ? OFFSET ?
            ''', (min_score, limit, offset))
            
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            pages = []
            for row in rows:
                page = dict(row)
                
                # Parse JSON fields
                if 'keywords_matched' in page and page['keywords_matched']:
                    page['keywords_matched'] = json.loads(page['keywords_matched'])
                
                pages.append(page)
            
            return pages
    
    def get_recent_pages(self, limit=100, offset=0):
        """
        Get recently crawled pages from the database.
        
        Args:
            limit (int): Maximum number of pages to return
            offset (int): Offset for pagination
            
        Returns:
            list: List of recently crawled pages
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Query for recent pages
            cursor.execute('''
            SELECT * FROM crawled_pages 
            ORDER BY crawl_time DESC 
            LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            pages = []
            for row in rows:
                page = dict(row)
                
                # Parse JSON fields
                if 'keywords_matched' in page and page['keywords_matched']:
                    page['keywords_matched'] = json.loads(page['keywords_matched'])
                
                pages.append(page)
            
            return pages
    
    def get_crawl_sessions(self, limit=10, offset=0):
        """
        Get crawl sessions from the database.
        
        Args:
            limit (int): Maximum number of sessions to return
            offset (int): Offset for pagination
            
        Returns:
            list: List of crawl sessions
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Query for crawl sessions
            cursor.execute('''
            SELECT * FROM crawl_metadata 
            ORDER BY start_time DESC 
            LIMIT ? OFFSET ?
            ''', (limit, offset))
            
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            sessions = []
            for row in rows:
                session = dict(row)
                
                # Parse JSON fields
                if 'keywords' in session and session['keywords']:
                    session['keywords'] = json.loads(session['keywords'])
                
                sessions.append(session)
            
            return sessions
    
    def get_crawl_statistics(self):
        """
        Get statistics about the crawled data.
        
        Returns:
            dict: Statistics about the crawled data
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get total number of pages
            cursor.execute('SELECT COUNT(*) FROM crawled_pages')
            total_pages = cursor.fetchone()[0]
            
            # Get average relevance score
            cursor.execute('SELECT AVG(relevance_score) FROM crawled_pages')
            avg_relevance = cursor.fetchone()[0] or 0.0
            
            # Get total number of crawl sessions
            cursor.execute('SELECT COUNT(*) FROM crawl_metadata')
            total_sessions = cursor.fetchone()[0]
            
            # Get total crawl time
            cursor.execute('''
            SELECT SUM(
                CASE 
                    WHEN end_time IS NOT NULL 
                    THEN julianday(end_time) - julianday(start_time) 
                    ELSE 0 
                END
            ) * 24 * 60 * 60 FROM crawl_metadata
            ''')
            total_time = cursor.fetchone()[0] or 0.0
            
            return {
                'total_pages': total_pages,
                'avg_relevance': avg_relevance,
                'total_sessions': total_sessions,
                'total_time_seconds': total_time
            }
    
    def export_to_json(self, output_file, limit=1000):
        """
        Export crawled pages to a JSON file.
        
        Args:
            output_file (str): Path to the output file
            limit (int): Maximum number of pages to export
            
        Returns:
            int: Number of pages exported
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Query for pages
            cursor.execute('''
            SELECT * FROM crawled_pages 
            ORDER BY relevance_score DESC 
            LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            pages = []
            for row in rows:
                page = dict(row)
                
                # Parse JSON fields
                if 'keywords_matched' in page and page['keywords_matched']:
                    page['keywords_matched'] = json.loads(page['keywords_matched'])
                
                pages.append(page)
            
            # Write to file
            with open(output_file, 'w') as f:
                json.dump(pages, f, indent=2)
            
            return len(pages)
    
    def export_to_csv(self, output_file, limit=1000):
        """
        Export crawled pages to a CSV file.
        
        Args:
            output_file (str): Path to the output file
            limit (int): Maximum number of pages to export
            
        Returns:
            int: Number of pages exported
        """
        import csv
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Query for pages
            cursor.execute('''
            SELECT url, title, content_snippet, relevance_score, depth, crawl_time 
            FROM crawled_pages 
            ORDER BY relevance_score DESC 
            LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            
            # Write to file
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow(['URL', 'Title', 'Content Snippet', 'Relevance Score', 'Depth', 'Crawl Time'])
                
                # Write rows
                for row in rows:
                    writer.writerow(row)
            
            return len(rows)
    
    def vacuum_database(self):
        """
        Vacuum the database to reclaim space.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                conn.execute('VACUUM')
                return True
        except Exception:
            return False 