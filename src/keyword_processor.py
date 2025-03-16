#!/usr/bin/env python3
"""
Keyword Processor Module
This module handles the processing of keywords for the web crawler.
"""

import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import re

def download_nltk_data():
    """Download required NLTK data packages."""
    print("Downloading NLTK data packages...")
    nltk.download('punkt')
    nltk.download('wordnet')
    nltk.download('stopwords')
    print("NLTK data packages downloaded successfully.")

class KeywordProcessor:
    def __init__(self, use_stemming=False, use_lemmatization=False, remove_stopwords=False):
        """
        Initialize the keyword processor.
        
        Args:
            use_stemming (bool): Whether to use stemming for keyword processing
            use_lemmatization (bool): Whether to use lemmatization for keyword processing
            remove_stopwords (bool): Whether to remove stopwords during keyword processing
        """
        self.use_stemming = use_stemming
        self.use_lemmatization = use_lemmatization
        self.remove_stopwords = remove_stopwords
        
        # Initialize stemmer and lemmatizer if needed
        if self.use_stemming:
            self.stemmer = PorterStemmer()
        
        if self.use_lemmatization:
            self.lemmatizer = WordNetLemmatizer()
        
        if self.remove_stopwords:
            try:
                self.stop_words = set(stopwords.words('english'))
            except LookupError:
                print("NLTK stopwords not found. Downloading...")
                nltk.download('stopwords')
                self.stop_words = set(stopwords.words('english'))
    
    def process_input(self, keywords_input):
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
    
    def process_text(self, text):
        """
        Process text by tokenizing, stemming/lemmatizing, and removing stopwords.
        
        Args:
            text (str): Text to process
            
        Returns:
            list: Processed tokens
        """
        # Convert to lowercase
        text = text.lower()
        
        # Tokenize
        try:
            tokens = word_tokenize(text)
        except LookupError:
            print("NLTK punkt not found. Downloading...")
            nltk.download('punkt')
            tokens = word_tokenize(text)
        
        # Remove stopwords if enabled
        if self.remove_stopwords:
            tokens = [token for token in tokens if token not in self.stop_words]
        
        # Apply stemming if enabled
        if self.use_stemming:
            tokens = [self.stemmer.stem(token) for token in tokens]
        
        # Apply lemmatization if enabled
        if self.use_lemmatization:
            try:
                tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
            except LookupError:
                print("NLTK WordNet not found. Downloading...")
                nltk.download('wordnet')
                tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        
        return tokens
    
    def is_relevant(self, text, keywords, regex_pattern=None):
        """
        Check if the text is relevant to the keywords.
        Only requires ONE of the keywords to match instead of ALL.
        
        Args:
            text (str): Text to check
            keywords (list): List of keywords to search for
            regex_pattern (str): Regular expression pattern to use for matching
            
        Returns:
            bool: True if the text is relevant, False otherwise
        """
        # If a regex pattern is provided, use it for matching
        if regex_pattern:
            try:
                pattern = re.compile(regex_pattern, re.IGNORECASE)
                return bool(pattern.search(text))
            except re.error as e:
                print(f"Error in regular expression pattern: {e}")
                # Fall back to normal keyword matching
        
        # Process the text into tokens
        text_tokens = set(self.process_text(text))
        
        # Check if ANY of the keywords are present in the text tokens
        for keyword in keywords:
            # Process the keyword to get its tokens
            keyword_tokens = set(self.process_text(keyword))
            
            # If keyword processing yielded no tokens, use the original keyword
            if not keyword_tokens:
                keyword_tokens = {keyword.lower()}
            
            # Check if any of the keyword tokens are in the text tokens
            if keyword_tokens.intersection(text_tokens):
                return True
        
        return False
    
    def match_with_regex(self, text, pattern):
        """
        Match text using a regular expression pattern.
        
        Args:
            text (str): Text to match
            pattern (str): Regular expression pattern
            
        Returns:
            list: List of matches found
        """
        try:
            compiled_pattern = re.compile(pattern, re.IGNORECASE)
            matches = compiled_pattern.findall(text)
            return matches
        except re.error as e:
            print(f"Error in regular expression pattern: {e}")
            return []
    
    def extract_keywords_from_text(self, text, top_n=10):
        """
        Extract potential keywords from text based on frequency.
        
        Args:
            text (str): Text to extract keywords from
            top_n (int): Number of top keywords to return
            
        Returns:
            list: List of potential keywords
        """
        # Process the text
        tokens = self.process_text(text)
        
        # Count token frequencies
        token_freq = {}
        for token in tokens:
            if token in token_freq:
                token_freq[token] += 1
            else:
                token_freq[token] = 1
        
        # Sort tokens by frequency
        sorted_tokens = sorted(token_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Return top N tokens
        return [token for token, freq in sorted_tokens[:top_n]]
    
    def find_keyword_context(self, text, keyword, context_size=50):
        """
        Find the context around a keyword in text.
        
        Args:
            text (str): Text to search in
            keyword (str): Keyword to find
            context_size (int): Number of characters to include before and after the keyword
            
        Returns:
            list: List of context snippets
        """
        text_lower = text.lower()
        keyword_lower = keyword.lower()
        
        # Find all occurrences of the keyword
        contexts = []
        start_pos = 0
        
        while True:
            pos = text_lower.find(keyword_lower, start_pos)
            if pos == -1:
                break
            
            # Calculate context boundaries
            context_start = max(0, pos - context_size)
            context_end = min(len(text), pos + len(keyword) + context_size)
            
            # Extract context
            context = text[context_start:context_end]
            
            # Add ellipsis if context is truncated
            if context_start > 0:
                context = "..." + context
            if context_end < len(text):
                context = context + "..."
            
            contexts.append(context)
            
            # Move to next position
            start_pos = pos + len(keyword)
        
        return contexts