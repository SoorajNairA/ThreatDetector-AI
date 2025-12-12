#!/usr/bin/env python3
"""
Basic usage examples for Guard SDK
"""

from guard_sdk import GuardClient

# Initialize client
client = GuardClient(
    api_key="your_api_key_here",
    base_url="http://localhost:8000"
)

# Example 1: Simple analysis
print("=" * 60)
print("Example 1: Basic Analysis")
print("=" * 60)

text = "URGENT! Your account has been suspended. Click here to verify your identity immediately."
result = client.analyze(text)

print(f"Text: {text}")
print(f"\nResults:")
print(f"  Risk Level: {result.risk_level.upper()}")
print(f"  Risk Score: {result.risk_score:.1%}")
print(f"  Intent: {result.intent}")
print(f"  Intent Confidence: {result.intent_confidence:.1%}")
print(f"  AI Generated: {result.ai_generated}")
print()

# Example 2: Check risk level
print("=" * 60)
print("Example 2: Risk Level Checks")
print("=" * 60)

texts = [
    "Click here to win $1,000,000!",
    "Meeting at 3pm tomorrow",
    "Verify your password now"
]

for text in texts:
    result = client.analyze(text)
    
    if result.is_high_risk():
        status = "🔴 HIGH RISK"
    elif result.is_medium_risk():
        status = "🟡 MEDIUM RISK"
    else:
        status = "🟢 LOW RISK"
    
    print(f"{status}: {text[:50]}")
    print(f"  Intent: {result.intent}, Score: {result.risk_score:.2f}")
    print()

# Example 3: Detailed analysis
print("=" * 60)
print("Example 3: Detailed Analysis")
print("=" * 60)

result = client.analyze("Click this suspicious link: http://bit.ly/fake-verify")

print(f"Risk Assessment:")
print(f"  Overall: {result.risk_level} ({result.risk_score:.1%})")
print()
print(f"AI Detection:")
print(f"  AI Generated: {result.ai_generated}")
print(f"  AI Confidence: {result.ai_confidence:.1%}")
print(f"  Human Confidence: {result.human_confidence:.1%}")
print()
print(f"Intent Classification:")
print(f"  Intent: {result.intent}")
print(f"  Confidence: {result.intent_confidence:.1%}")
print()
print(f"URL Detection:")
print(f"  URLs Found: {result.url_detected}")
if result.domains:
    print(f"  Domains: {', '.join(result.domains)}")
print(f"  URL Risk: {result.url_score:.1%}")
print()
print(f"Keyword Analysis:")
print(f"  Keywords: {', '.join(result.keywords[:5])}")
print(f"  Keyword Risk: {result.keyword_score:.1%}")
print()

# Example 4: Batch analysis
print("=" * 60)
print("Example 4: Batch Analysis")
print("=" * 60)

messages = [
    "Congratulations! You won a prize",
    "Let's meet for coffee tomorrow",
    "Your account needs verification",
    "Happy birthday! Hope you have a great day",
    "Click here to claim your refund"
]

results = client.batch_analyze(messages, delay=0.1)

high_risk_count = sum(1 for r in results if r.is_high_risk())
print(f"Analyzed {len(messages)} messages")
print(f"High risk detected: {high_risk_count}")
print()

for msg, result in zip(messages, results):
    print(f"[{result.risk_level.upper()}] {msg}")
print()

# Close client
client.close()

print("=" * 60)
print("Examples Complete")
print("=" * 60)
