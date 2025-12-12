"""Text feature extraction utilities"""
from typing import List


def calculate_average_sentence_length(text: str) -> float:
    """
    Calculate average sentence length in words.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Average sentence length (words per sentence)
    """
    # Simple sentence splitting by common delimiters
    sentences = [s.strip() for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
    
    if not sentences:
        return 0.0
    
    total_words = sum(len(sentence.split()) for sentence in sentences)
    return total_words / len(sentences)


def calculate_uppercase_ratio(text: str) -> float:
    """
    Calculate ratio of uppercase letters to total letters.
    
    Args:
        text: Input text to analyze
        
    Returns:
        Ratio of uppercase letters (0.0 to 1.0)
    """
    if not text:
        return 0.0
    
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    
    uppercase_count = sum(1 for c in letters if c.isupper())
    return uppercase_count / len(letters)


def extract_keywords(text: str, keyword_list: List[str]) -> List[str]:
    """
    Extract keywords from text.
    
    Args:
        text: Input text to analyze
        keyword_list: List of keywords to search for
        
    Returns:
        List of found keywords
    """
    text_lower = text.lower()
    found_keywords = []
    
    for keyword in keyword_list:
        if keyword.lower() in text_lower:
            found_keywords.append(keyword)
    
    return found_keywords
