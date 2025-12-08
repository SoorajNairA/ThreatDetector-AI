import re
import math
from collections import Counter

def entropy(s):
    """Calculate Shannon entropy of a string."""
    if not s:
        return 0.0
    counts = Counter(s)
    total = len(s)
    return -sum((c/total) * math.log2(c/total) for c in counts.values())

def predict(text: str):
    """
    Measure writing style patterns that correlate with AI or human content.
    
    Returns:
        style_score: float [0, 1] where higher is more human-like
    """
    if not text:
        return {"style_score": 0.5}
    
    # ===== Feature extraction =====
    tokens = text.split()
    num_tokens = len(tokens)
    
    if num_tokens == 0:
        return {"style_score": 0.5}
    
    # 1. Average token length (longer tokens → human-like)
    avg_token_len = sum(len(t) for t in tokens) / num_tokens
    
    # 2. Token variance (higher variance → human-like)
    token_lens = [len(t) for t in tokens]
    mean_len = sum(token_lens) / len(token_lens)
    variance = sum((x - mean_len) ** 2 for x in token_lens) / len(token_lens)
    token_variance = min(1.0, math.sqrt(variance) / 10)  # normalize
    
    # 3. Sentence count and average sentence length
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    num_sentences = max(1, len(sentences))
    avg_sentence_len = num_tokens / num_sentences
    
    # 4. Character-level entropy (higher → more diverse, human-like)
    char_entropy = entropy(text)
    
    # 5. Punctuation patterns (reasonable punctuation → human-like)
    punctuation_chars = re.findall(r'[.!?,;:\"-]', text)
    punct_ratio = len(punctuation_chars) / max(1, len(text))
    
    # 6. Repetition score (lower repetition → more human-like)
    # Count consecutive repeated tokens
    repetition_count = 0
    for i in range(len(tokens) - 1):
        if tokens[i].lower() == tokens[i+1].lower():
            repetition_count += 1
    repetition_ratio = repetition_count / max(1, num_tokens - 1)
    
    # ===== Score combination =====
    # Normalize features to [0, 1]
    token_len_score = min(1.0, avg_token_len / 8)  # typical avg token ~4-8 chars
    sentence_len_score = min(1.0, avg_sentence_len / 25)  # typical ~15-25 words/sentence
    entropy_score = min(1.0, char_entropy / 5)  # typical entropy 3-5
    punctuation_score = min(1.0, punct_ratio * 10)  # typical ~5-15% punctuation
    repetition_score = max(0.0, 1.0 - repetition_ratio * 5)  # penalize repetition
    
    # Weighted average (prefer entropy and repetition as strong signals)
    style_score = (
        token_len_score * 0.15 +
        token_variance * 0.15 +
        sentence_len_score * 0.15 +
        entropy_score * 0.25 +
        punctuation_score * 0.15 +
        repetition_score * 0.15
    )
    
    # Determine formality level based on multiple indicators
    formal_indicators = 0
    informal_indicators = 0
    
    # Check for informal markers
    informal_patterns = [
        r'\blol\b', r'\bomg\b', r'\bwtf\b', r'\blmao\b', r'\brofl\b',
        r'\bya\b', r'\byeah\b', r'\bnah\b', r'\bgonna\b', r'\bwanna\b',
        r'\bdude\b', r'\bguys\b', r'\bkinda\b', r'\bsorta\b',
        r'😂', r'😊', r'👍', r'❤️', r'🤣'  # emojis
    ]
    
    for pattern in informal_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            informal_indicators += 1
    
    # Check for formal markers
    formal_patterns = [
        r'\bdear\s+(?:sir|madam)\b', r'\bsincerely\b', r'\bregards\b',
        r'\bpursuant\b', r'\btherefore\b', r'\bfurthermore\b',
        r'\bnevertheless\b', r'\bhowever\b', r'\bmoreover\b',
        r'\bplease find attached\b', r'\bi am writing to\b',
        r'\bwith respect to\b', r'\bin accordance with\b'
    ]
    
    for pattern in formal_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            formal_indicators += 1
    
    # Check capitalization and punctuation
    if text and text[0].isupper() and text.rstrip().endswith(('.', '!', '?')):
        formal_indicators += 0.5
    
    # Check for contractions (informal)
    contractions = ["n't", "'s", "'re", "'ve", "'ll", "'d", "'m"]
    contraction_count = sum(1 for c in contractions if c in text.lower())
    if contraction_count > 2:
        informal_indicators += 1
    
    # Check average sentence length (longer = more formal)
    if avg_sentence_len > 20:
        formal_indicators += 1
    elif avg_sentence_len < 10:
        informal_indicators += 1
    
    # Check average word length (longer = more formal)
    if avg_token_len > 5.5:
        formal_indicators += 1
    elif avg_token_len < 4:
        informal_indicators += 1
    
    # Make final decision
    if informal_indicators > formal_indicators + 1:
        style = "informal"
        confidence = min(0.95, 0.6 + (informal_indicators * 0.1))
    elif formal_indicators > informal_indicators + 1:
        style = "formal"
        confidence = min(0.95, 0.6 + (formal_indicators * 0.1))
    else:
        # Neutral - use sentence/word length as tiebreaker
        if avg_sentence_len > 15 or avg_token_len > 5:
            style = "formal"
            confidence = 0.55
        else:
            style = "informal"
            confidence = 0.55
    
    return {
        "style": style,
        "confidence": float(confidence),
        "style_score": float(min(1.0, max(0.0, style_score))),
        "avg_token_len": float(avg_token_len),
        "avg_sentence_len": float(avg_sentence_len),
        "formal_indicators": formal_indicators,
        "informal_indicators": informal_indicators
    }
