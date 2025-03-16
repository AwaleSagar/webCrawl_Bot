#!/usr/bin/env python3
"""
Command Line Interface for Web Crawler Database
Provides a simple CLI for querying and managing the crawler database.
"""

import argparse
import sys
import os
from database_manager import DatabaseManager

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Web Crawler Database CLI')
    
    # Database options
    parser.add_argument('--db-path', type=str, default='crawler.db',
                       help='Path to the SQLite database file (default: crawler.db)')
    
    # Command options
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show database statistics')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query the database for pages')
    query_parser.add_argument('--min-score', type=float, default=0.0,
                             help='Minimum relevance score (0.0-1.0)')
    query_parser.add_argument('--limit', type=int, default=100,
                             help='Maximum number of results to return')
    query_parser.add_argument('--offset', type=int, default=0,
                             help='Offset for pagination')
    query_parser.add_argument('--sort', type=str, choices=['relevance', 'date'], default='relevance',
                             help='Sort order (default: relevance)')
    
    # Recent command
    recent_parser = subparsers.add_parser('recent', help='Show recently crawled pages')
    recent_parser.add_argument('--limit', type=int, default=100,
                              help='Maximum number of results to return')
    recent_parser.add_argument('--offset', type=int, default=0,
                              help='Offset for pagination')
    
    # Sessions command
    sessions_parser = subparsers.add_parser('sessions', help='Show crawl sessions')
    sessions_parser.add_argument('--limit', type=int, default=10,
                                help='Maximum number of sessions to return')
    sessions_parser.add_argument('--offset', type=int, default=0,
                                help='Offset for pagination')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export database to a file')
    export_parser.add_argument('output_file', type=str,
                              help='Path to the output file')
    export_parser.add_argument('--format', type=str, choices=['json', 'csv'], default='json',
                              help='Export format (default: json)')
    export_parser.add_argument('--limit', type=int, default=1000,
                              help='Maximum number of results to export')
    export_parser.add_argument('--min-score', type=float, default=0.0,
                              help='Minimum relevance score (0.0-1.0)')
    
    # Vacuum command
    vacuum_parser = subparsers.add_parser('vacuum', help='Vacuum the database to reclaim space')
    
    return parser.parse_args()

def show_stats(db_manager):
    """Show database statistics."""
    stats = db_manager.get_crawl_statistics()
    
    print("\nDatabase Statistics:")
    print("===================")
    print(f"Total pages: {stats['total_pages']}")
    print(f"Average relevance score: {stats['avg_relevance']:.4f}")
    print(f"Total crawl sessions: {stats['total_sessions']}")
    print(f"Total crawl time: {stats['total_time_seconds'] / 60:.2f} minutes")

def query_pages(db_manager, min_score, limit, offset, sort_by='relevance'):
    """Query the database for pages."""
    if sort_by == 'relevance':
        pages = db_manager.get_relevant_pages(limit, offset, min_score)
    else:  # sort_by == 'date'
        pages = db_manager.get_recent_pages(limit, offset)
    
    print("\nRelevant Pages:")
    print("==============")
    
    if not pages:
        print("No pages found matching the criteria.")
        return
    
    for i, page in enumerate(pages, 1):
        print(f"{i}. {page['title']}")
        print(f"   URL: {page['url']}")
        print(f"   Relevance Score: {page['relevance_score']:.4f}")
        print(f"   Depth: {page['depth']}")
        print(f"   Crawl Time: {page['crawl_time']}")
        if 'keywords_matched' in page and page['keywords_matched']:
            print(f"   Keywords Matched: {', '.join(page['keywords_matched'])}")
        print()

def show_recent_pages(db_manager, limit, offset):
    """Show recently crawled pages."""
    pages = db_manager.get_recent_pages(limit, offset)
    
    print("\nRecently Crawled Pages:")
    print("=====================")
    
    if not pages:
        print("No pages found in the database.")
        return
    
    for i, page in enumerate(pages, 1):
        print(f"{i}. {page['title']}")
        print(f"   URL: {page['url']}")
        print(f"   Relevance Score: {page['relevance_score']:.4f}")
        print(f"   Depth: {page['depth']}")
        print(f"   Crawl Time: {page['crawl_time']}")
        if 'keywords_matched' in page and page['keywords_matched']:
            print(f"   Keywords Matched: {', '.join(page['keywords_matched'])}")
        print()

def show_sessions(db_manager, limit, offset):
    """Show crawl sessions."""
    sessions = db_manager.get_crawl_sessions(limit, offset)
    
    print("\nCrawl Sessions:")
    print("==============")
    
    if not sessions:
        print("No crawl sessions found in the database.")
        return
    
    for i, session in enumerate(sessions, 1):
        print(f"{i}. Session ID: {session['id']}")
        print(f"   Start Time: {session['start_time']}")
        print(f"   End Time: {session['end_time'] or 'In progress'}")
        print(f"   Keywords: {', '.join(session['keywords'])}")
        print(f"   Pages Crawled: {session['pages_crawled']}")
        print(f"   Relevant Pages Found: {session['relevant_pages_found']}")
        print()

def export_database(db_manager, output_file, export_format, limit, min_score):
    """Export database to a file."""
    if export_format == 'json':
        count = db_manager.export_to_json(output_file, limit)
        print(f"Exported {count} pages to {output_file} in JSON format")
    elif export_format == 'csv':
        count = db_manager.export_to_csv(output_file, limit)
        print(f"Exported {count} pages to {output_file} in CSV format")

def vacuum_database(db_manager):
    """Vacuum the database to reclaim space."""
    if db_manager.vacuum_database():
        print("Database vacuumed successfully")
    else:
        print("Failed to vacuum database")

def main():
    """Main function."""
    args = parse_arguments()
    
    # Check if database file exists
    if not os.path.exists(args.db_path):
        print(f"Error: Database file '{args.db_path}' not found.")
        print("Please run the crawler with --use-database option first.")
        return 1
    
    # Initialize database manager
    db_manager = DatabaseManager(args.db_path)
    
    # Execute the requested command
    if args.command == 'stats':
        show_stats(db_manager)
    elif args.command == 'query':
        query_pages(db_manager, args.min_score, args.limit, args.offset, 
                   'relevance' if args.sort == 'relevance' else 'date')
    elif args.command == 'recent':
        show_recent_pages(db_manager, args.limit, args.offset)
    elif args.command == 'sessions':
        show_sessions(db_manager, args.limit, args.offset)
    elif args.command == 'export':
        export_database(db_manager, args.output_file, args.format, args.limit, args.min_score)
    elif args.command == 'vacuum':
        vacuum_database(db_manager)
    else:
        print("Error: No command specified.")
        print("Use --help to see available commands.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 