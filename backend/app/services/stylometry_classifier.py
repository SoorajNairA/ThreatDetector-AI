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
    
    return {
        "style_score": float(min(1.0, max(0.0, style_score))),
        "avg_token_len": float(avg_token_len),
        "token_variance": float(token_variance),
        "avg_sentence_len": float(avg_sentence_len),
        "char_entropy": float(char_entropy),
        "punct_ratio": float(punct_ratio),
        "repetition_ratio": float(repetition_ratio)
    }
