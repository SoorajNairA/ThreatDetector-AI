"""URL detection and analysis utilities"""
import re
from typing import List


# Simple regex pattern for detecting URLs
URL_PATTERN = re.compile(
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
)


def extract_urls(text: str) -> List[str]:
    """
    Extract URLs from text using regex.
    
    Args:
        text: Input text to search for URLs
        
    Returns:
        List of URLs found in text
    """
    return URL_PATTERN.findall(text)


def has_urls(text: str) -> bool:
    """
    Check if text contains any URLs.
    
    Args:
        text: Input text to check
        
    Returns:
        True if URLs are present, False otherwise
    """
    return bool(URL_PATTERN.search(text))
