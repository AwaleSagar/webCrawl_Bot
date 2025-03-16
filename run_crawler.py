#!/usr/bin/env python
"""
Wrapper script to run the web crawler.
This script imports and calls the main function from src/main.py.
"""

import os
import sys
import argparse

def run_crawler():
    """Run the web crawler by importing and calling the main function."""
    try:
        # Add the src directory to the Python path
        src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
        sys.path.insert(0, src_dir)
        
        # Import the main module
        try:
            from main import main
        except ImportError as e:
            print(f"Error importing main module: {e}")
            print("Make sure the src directory contains main.py")
            sys.exit(1)
        
        # Call the main function with all command line arguments
        # This passes through all arguments to main.py
        sys.exit(main())
        
    except Exception as e:
        print(f"Error running crawler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_crawler() 