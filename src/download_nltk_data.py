#!/usr/bin/env python3
"""
Script to download required NLTK data packages.
"""

import nltk

def download_nltk_data():
    """Download required NLTK data packages."""
    print("Downloading NLTK data packages...")
    
    # Download punkt tokenizer
    print("Downloading punkt tokenizer...")
    nltk.download('punkt')
    
    # Download WordNet for lemmatization
    print("Downloading WordNet...")
    nltk.download('wordnet')
    
    # Download stopwords
    print("Downloading stopwords...")
    nltk.download('stopwords')
    
    print("All NLTK data packages downloaded successfully.")

if __name__ == "__main__":
    download_nltk_data() 