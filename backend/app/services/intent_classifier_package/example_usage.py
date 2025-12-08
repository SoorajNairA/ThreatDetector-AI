#!/usr/bin/env python3
"""
Quick usage examples for the Intent Classifier.
Copy this file to your project and run: python example_usage.py
"""

from intent_classifier import classify_intent

def main():
    """Run usage examples."""
    
    print("=" * 100)
    print("INTENT CLASSIFIER - USAGE EXAMPLES")
    print("=" * 100)
    
    # Example 1: Direct threat
    print("\n1. DIRECT THREAT DETECTION")
    print("-" * 100)
    text = "I will kill you tomorrow"
    result = classify_intent(text)
    print(f"Text: '{text}'")
    print(f"Intent: {result['intent'].upper()}")
    print(f"Confidence: {result['probability']:.1%}")
    print(f"Explanation: {result['explanation']}")
    
    # Example 2: Safe with threat keyword
    print("\n2. SAFE CONTEXT - TECH")
    print("-" * 100)
    text = "Kill the background process"
    result = classify_intent(text)
    print(f"Text: '{text}'")
    print(f"Intent: {result['intent'].upper()}")
    print(f"Confidence: {result['probability']:.1%}")
    print(f"Explanation: {result['explanation']}")
    
    # Example 3: Figurative language
    print("\n3. SAFE CONTEXT - FIGURATIVE")
    print("-" * 100)
    text = "This workout is killing me"
    result = classify_intent(text)
    print(f"Text: '{text}'")
    print(f"Intent: {result['intent'].upper()}")
    print(f"Confidence: {result['probability']:.1%}")
    print(f"Explanation: {result['explanation']}")
    
    # Example 4: Sports context
    print("\n4. SAFE CONTEXT - SPORTS")
    print("-" * 100)
    text = "We're attacking their defense"
    result = classify_intent(text)
    print(f"Text: '{text}'")
    print(f"Intent: {result['intent'].upper()}")
    print(f"Confidence: {result['probability']:.1%}")
    print(f"Explanation: {result['explanation']}")
    
    # Example 5: Bombing threat
    print("\n5. SPECIFIC THREAT - BOMBING")
    print("-" * 100)
    text = "I will blow up the building tomorrow"
    result = classify_intent(text)
    print(f"Text: '{text}'")
    print(f"Intent: {result['intent'].upper()}")
    print(f"Confidence: {result['probability']:.1%}")
    print(f"ML Component: {result['ml_confidence']:.1%}")
    print(f"Rule Component: {result['rule_confidence']:.1%}")
    print(f"Processing Time: {result['latency_ms']:.2f}ms")
    
    # Example 6: Targeting threat
    print("\n6. SPECIFIC THREAT - TARGETING")
    print("-" * 100)
    text = "I know where you live and I'm coming for you"
    result = classify_intent(text)
    print(f"Text: '{text}'")
    print(f"Intent: {result['intent'].upper()}")
    print(f"Confidence: {result['probability']:.1%}")
    
    # Example 7: Entertainment context
    print("\n7. SAFE CONTEXT - ENTERTAINMENT")
    print("-" * 100)
    text = "This joke is killing me"
    result = classify_intent(text)
    print(f"Text: '{text}'")
    print(f"Intent: {result['intent'].upper()}")
    print(f"Confidence: {result['probability']:.1%}")
    
    # Example 8: Batch processing
    print("\n8. BATCH PROCESSING")
    print("-" * 100)
    texts = [
        "I will kill you",
        "Let's go to the movies",
        "plan to bomb tomorrow",
        "This movie is bomb",
    ]
    print(f"Processing {len(texts)} texts:")
    for text in texts:
        result = classify_intent(text)
        print(f"  '{text:40}' → {result['intent'].upper():6} ({result['probability']:.1%})")
    
    print("\n" + "=" * 100)
    print("For more information, see README.md")
    print("=" * 100)

if __name__ == "__main__":
    main()
