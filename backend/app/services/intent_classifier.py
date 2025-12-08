"""
Intent Classifier wrapper for the trained ML model.
Uses the hybrid classifier from intent_classifier_package.
"""

from .intent_classifier_package.intent_classifier.classifier import IntentClassifier

# Singleton instance
_classifier = None


def get_classifier():
    """Get or create the singleton classifier instance."""
    global _classifier
    if _classifier is None:
        _classifier = IntentClassifier()
    return _classifier


def predict(text: str) -> dict:
    """
    Predict intent using the trained hybrid classifier.
    
    Args:
        text: Input text to classify
        
    Returns:
        dict with keys:
            - intent: Detected intent (phishing/scam/spam/legitimate)
            - intent_confidence: Confidence score (0-1)
    """
    classifier = get_classifier()
    result = classifier.classify_intent(text)
    
    # Map threat classifier output to Guardian's intent categories
    # The hybrid classifier returns 'threat' or 'safe'
    intent_mapping = {
        "threat": _map_threat_to_specific_intent(text, result.probability),
        "safe": "legitimate"
    }
    
    mapped_intent = intent_mapping.get(result.intent, "unknown")
    
    return {
        "intent": mapped_intent,
        "intent_confidence": float(result.probability)
    }


def _map_threat_to_specific_intent(text: str, confidence: float) -> str:
    """
    Map threat detection to specific intent categories.
    Uses simple keyword heuristics for now.
    """
    text_lower = text.lower()
    
    # High confidence phishing indicators
    phishing_keywords = ["verify", "login", "password", "click here", "confirm", 
                         "account", "suspended", "update", "secure", "credentials"]
    if any(word in text_lower for word in phishing_keywords):
        return "phishing"
    
    # Scam indicators
    scam_keywords = ["winner", "claim", "prize", "congratulations", "won", 
                    "lottery", "inheritance", "million", "dollars", "transfer"]
    if any(word in text_lower for word in scam_keywords):
        return "scam"
    
    # Spam indicators
    spam_keywords = ["unsubscribe", "offer", "limited time", "buy now", 
                    "discount", "free", "click", "subscribe"]
    if any(word in text_lower for word in spam_keywords):
        return "spam"
    
    # Default to phishing for high-confidence threats
    if confidence >= 0.7:
        return "phishing"
    
    return "spam"
