"""
Intent Classifier Package - Hybrid threat detection system.
"""

from .classifier import classify_intent, get_classifier, ClassificationResult


def predict(text: str, context=None):
    """
    Wrapper function for backward compatibility.
    
    Args:
        text: Input text to classify
        context: Optional context for enhanced analysis
        
    Returns:
        Dictionary with classification results including intent_confidence
    """
    result = classify_intent(text, context)
    
    # Add intent_confidence for compatibility (same as probability)
    result["intent_confidence"] = result.get("probability", 0.0)
    
    return result


__all__ = ["classify_intent", "get_classifier", "ClassificationResult", "predict"]
