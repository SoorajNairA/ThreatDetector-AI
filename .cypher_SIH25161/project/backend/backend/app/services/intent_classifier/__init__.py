"""
Intent Classifier Package - Hybrid threat detection system.
"""

from .classifier import classify_intent, get_classifier, ClassificationResult


def _categorize_threat(text: str, probability: float, ml_conf: float, semantic_conf: float, rule_conf: float) -> str:
    """
    Categorize threat into specific types based on keywords and patterns.
    
    Returns: 'phishing', 'scam', 'propaganda', 'spam', 'unknown', or 'safe'
    """
    text_lower = text.lower()
    
    # High confidence threat patterns
    phishing_keywords = ['password', 'login', 'verify', 'account', 'credentials', 
                         'authenticate', 'confirm', 'suspended', 'unusual activity',
                         'verify your identity', 'click here', 'update payment',
                         'compromised', 'verify your account', 'confirm your identity']
    
    scam_keywords = ['won', 'winner', 'prize', 'congratulations', 'claim', 'million',
                    'lottery', 'inheritance', 'free money', 'unclaimed', 'jackpot',
                    'send money', 'wire transfer', 'bank account number', 'thousand']
    
    propaganda_keywords = ['fake news', 'conspiracy', 'coverup', 'wake up', 'sheeple',
                          'they dont want', 'mainstream media', 'hoax', 'propaganda',
                          'censorship', 'hidden truth']
    
    spam_keywords = ['buy now', 'limited time', 'act now', 'exclusive deal', 
                    'special offer', 'discount', 'click below', 'unsubscribe',
                    'limited offer']
    
    # Check for urgency indicators (amplifies threat categorization)
    urgency_indicators = ['urgent', 'immediately', 'asap', 'right away', 'now', 
                         'final notice', 'within 24 hours', 'expires']
    has_urgency = any(ind in text_lower for ind in urgency_indicators)
    
    # Count keyword matches with urgency boost
    phishing_score = sum(1 for kw in phishing_keywords if kw in text_lower)
    scam_score = sum(1 for kw in scam_keywords if kw in text_lower)
    propaganda_score = sum(1 for kw in propaganda_keywords if kw in text_lower)
    spam_score = sum(1 for kw in spam_keywords if kw in text_lower)
    
    # Apply urgency multiplier
    if has_urgency:
        phishing_score = phishing_score * 1.5
        scam_score = scam_score * 1.2
        spam_score = spam_score * 1.3
    
    # Determine category based on highest score
    scores = {
        'phishing': phishing_score,
        'scam': scam_score,
        'propaganda': propaganda_score,
        'spam': spam_score
    }
    
    max_category = max(scores, key=scores.get)
    max_score = scores[max_category]
    
    # Return category based on score threshold (lowered for better detection)
    # Even if ML thinks it's safe, if we have strong keyword matches, classify as threat
    if max_score >= 2.0:
        return max_category
    elif max_score >= 1.0:
        # If ML or semantic shows some threat signal, trust the keywords
        if probability > 0.15 or ml_conf > 0.2 or semantic_conf > 0.2:
            return max_category
        else:
            return 'unknown'
    elif max_score >= 0.5:
        # Need higher confidence to classify with weak keyword match
        if probability > 0.3 or ml_conf > 0.4:
            return max_category
        else:
            return 'safe'
    else:
        return 'safe'


def predict(text: str, context=None):
    """
    Wrapper function for backward compatibility.
    
    Args:
        text: Input text to classify
        context: Optional context for enhanced analysis
        
    Returns:
        Dictionary with classification results including intent and intent_confidence
    """
    result = classify_intent(text, context)
    
    # Get the base intent (threat or safe/legitimate) and confidence scores
    base_intent = result.get("intent", "safe")
    probability = result.get("probability", 0.0)
    ml_conf = result.get("ml_confidence", 0.0)
    semantic_conf = result.get("semantic_confidence", 0.0)
    rule_conf = result.get("rule_confidence", 0.0)
    
    # Categorize based on keywords and ML signals
    specific_intent = _categorize_threat(text, probability, ml_conf, semantic_conf, rule_conf)
    
    # Update result with specific intent
    result["intent"] = specific_intent
    result["intent_confidence"] = probability
    
    return result


__all__ = ["classify_intent", "get_classifier", "ClassificationResult", "predict"]
