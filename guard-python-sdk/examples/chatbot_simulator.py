#!/usr/bin/env python3
"""
Chatbot Simulator - Mimics suspicious conversations for testing Guard API
Sends various threat patterns to test intent classifier accuracy
"""

import time
import random
import subprocess
import sys
import os

try:
    from guard_sdk import GuardClient, GuardError
except ImportError:
    print("=" * 80)
    print("ERROR: guard_sdk module not found!")
    print("=" * 80)
    print("\nAttempting to install guard_sdk...")
    print("Running: pip install -e ../../guard-python-sdk")
    print()
    
    try:
        sdk_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", sdk_path])
        print("\n✓ Installation successful! Please run the script again.")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Installation failed: {e}")
        print("\nPlease manually install the SDK:")
        print("  cd guard-python-sdk")
        print("  pip install -e .")
    
    sys.exit(1)

# Initialize client
client = GuardClient(
    api_key="gsp_Jq-mJQFKbCpeWPt7fKcd9oFpmsO9_-8xOQKgFotpD_M",
    base_url="http://localhost:8000"
)

# Conversation scenarios with expected threat patterns
THREAT_CONVERSATIONS = [
    {
        "category": "PHISHING ATTACK",
        "messages": [
            "Hi! This is your bank security team.",
            "We've detected unusual activity on your account.",
            "Please verify your identity immediately to prevent account suspension.",
            "Click here to confirm your details: http://bit.ly/bank-verify",
            "You must provide your password and social security number.",
            "This is urgent! Your account will be locked in 24 hours."
        ]
    },
    {
        "category": "PRIZE SCAM",
        "messages": [
            "Congratulations! You've been selected as a winner!",
            "You won $1,000,000 in our international lottery!",
            "To claim your prize, send us your bank account details.",
            "We need your full name, address, and date of birth.",
            "Act fast! This offer expires in 48 hours.",
            "Send payment of $500 for processing fees to receive your prize."
        ]
    },
    {
        "category": "ACCOUNT TAKEOVER",
        "messages": [
            "Your Amazon account has been compromised!",
            "Someone tried to login from Russia.",
            "Verify your account now to prevent unauthorized purchases.",
            "Enter your password here: secure-amazon-login.com",
            "If you don't respond in 1 hour, your account will be permanently disabled.",
            "We need your credit card information to verify ownership."
        ]
    },
    {
        "category": "TECH SUPPORT SCAM",
        "messages": [
            "WARNING: Your computer is infected with a virus!",
            "Microsoft Security Alert: Critical threat detected.",
            "Call this number immediately: 1-800-FAKE-NUM",
            "Do not turn off your computer or you will lose all data.",
            "Our technicians need remote access to fix the issue.",
            "Pay $299.99 for lifetime virus protection."
        ]
    },
    {
        "category": "ROMANCE SCAM",
        "messages": [
            "I feel such a strong connection with you already.",
            "I know we just met online, but I think I'm falling for you.",
            "I'm stuck in another country and need help.",
            "Can you send me $2000? I'll pay you back I promise.",
            "I want to visit you but need money for the plane ticket.",
            "Please wire the money to this account urgently."
        ]
    },
    {
        "category": "CRYPTOCURRENCY SCAM",
        "messages": [
            "Amazing investment opportunity! Double your money in 7 days!",
            "Send Bitcoin to this wallet: 1FakeWalletAddress123",
            "Our trading bot has 99% success rate guaranteed!",
            "Limited spots available! Invest now or miss out forever!",
            "Everyone is getting rich, don't be left behind!",
            "Send minimum $1000 in crypto to start earning."
        ]
    },
    {
        "category": "JOB SCAM",
        "messages": [
            "Congratulations! You've been selected for a high-paying job!",
            "Work from home and earn $5000 per week!",
            "No experience needed! Just send us $200 for training materials.",
            "You need to provide your social security number for payroll.",
            "First, cash this check and send us back half the amount.",
            "This is a limited time opportunity, act now!"
        ]
    },
    {
        "category": "FAKE SHIPPING NOTIFICATION",
        "messages": [
            "Your package delivery has failed.",
            "Click here to reschedule: fake-fedex-tracking.com",
            "We need to verify your address details.",
            "Pay $3.99 redelivery fee to receive your package.",
            "Enter your credit card information to confirm.",
            "Package will be returned if not claimed within 24 hours."
        ]
    }
]

# Normal, safe conversations for comparison
SAFE_CONVERSATIONS = [
    {
        "category": "CASUAL CHAT",
        "messages": [
            "Hey! How are you doing today?",
            "Did you catch the game last night?",
            "Want to grab coffee this weekend?",
            "That movie was really good, you should watch it.",
            "Let me know what time works for you.",
            "See you later!"
        ]
    },
    {
        "category": "WORK DISCUSSION",
        "messages": [
            "Good morning team!",
            "The project deadline is next Friday.",
            "Can everyone submit their reports by end of day?",
            "Great work on the presentation!",
            "Let's schedule a meeting to discuss next steps.",
            "Thanks for your hard work everyone."
        ]
    },
    {
        "category": "CUSTOMER SERVICE",
        "messages": [
            "Thank you for contacting our support team.",
            "We've received your inquiry and will respond within 24 hours.",
            "Your order #12345 has been shipped.",
            "Please let us know if you have any questions.",
            "We appreciate your business.",
            "Have a great day!"
        ]
    }
]


def simulate_conversation(conversation, delay=1.5):
    """
    Simulate a conversation by sending messages one by one
    
    Args:
        conversation: Dict with category and messages
        delay: Seconds to wait between messages
    """
    print("\n" + "=" * 80)
    print(f"CONVERSATION: {conversation['category']}")
    print("=" * 80)
    
    results = []
    high_risk_count = 0
    
    for i, message in enumerate(conversation['messages'], 1):
        print(f"\n[Message {i}/{len(conversation['messages'])}]")
        print(f"User: {message}")
        
        try:
            # Analyze message
            result = client.analyze(message, sandbox=False)
            
            # Display result
            risk_emoji = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🟢"
            }
            
            emoji = risk_emoji.get(result.risk_level, "⚪")
            print(f"{emoji} Risk: {result.risk_level.upper()} ({result.risk_score:.1%})")
            print(f"   Intent: {result.intent} (confidence: {result.intent_confidence:.1%})")
            
            if result.keywords:
                print(f"   Keywords: {', '.join(result.keywords[:5])}")
            
            if result.url_detected:
                print(f"   ⚠️ URLs detected: {', '.join(result.domains)}")
            
            # Track high risk messages
            if result.is_high_risk():
                high_risk_count += 1
            
            results.append({
                "message": message,
                "risk_level": result.risk_level,
                "risk_score": result.risk_score,
                "intent": result.intent
            })
            
            # Wait before next message
            if i < len(conversation['messages']):
                time.sleep(delay)
        
        except GuardError as e:
            print(f"❌ Error: {e}")
            continue
    
    # Conversation summary
    print("\n" + "-" * 80)
    print("CONVERSATION SUMMARY")
    print("-" * 80)
    
    avg_score = sum(r['risk_score'] for r in results) / len(results) if results else 0
    print(f"Total Messages: {len(results)}")
    print(f"High Risk Detected: {high_risk_count}/{len(results)}")
    print(f"Average Risk Score: {avg_score:.1%}")
    
    # Determine if conversation should be flagged
    if high_risk_count >= len(results) * 0.5:
        print("⚠️ ALERT: Suspicious conversation detected!")
    elif avg_score >= 0.6:
        print("⚠️ WARNING: Potentially suspicious conversation")
    else:
        print("✓ Conversation appears safe")
    
    return results


def run_test_suite(include_safe=True, message_delay=1.5):
    """
    Run full test suite with all conversation scenarios
    
    Args:
        include_safe: Include safe conversations for comparison
        message_delay: Seconds between messages
    """
    print("=" * 80)
    print("CHATBOT SIMULATOR - Testing Intent Classifier")
    print("=" * 80)
    print(f"\nTesting {len(THREAT_CONVERSATIONS)} threat scenarios")
    if include_safe:
        print(f"Testing {len(SAFE_CONVERSATIONS)} safe scenarios")
    print()
    
    all_results = {
        "threats": [],
        "safe": []
    }
    
    # Test threat conversations
    print("\n" + "█" * 80)
    print("THREAT SCENARIOS")
    print("█" * 80)
    
    for conversation in THREAT_CONVERSATIONS:
        results = simulate_conversation(conversation, delay=message_delay)
        all_results["threats"].append({
            "category": conversation["category"],
            "results": results
        })
        time.sleep(2)  # Pause between conversations
    
    # Test safe conversations
    if include_safe:
        print("\n" + "█" * 80)
        print("SAFE SCENARIOS (for comparison)")
        print("█" * 80)
        
        for conversation in SAFE_CONVERSATIONS:
            results = simulate_conversation(conversation, delay=message_delay)
            all_results["safe"].append({
                "category": conversation["category"],
                "results": results
            })
            time.sleep(2)
    
    # Overall summary
    print("\n" + "=" * 80)
    print("OVERALL TEST SUMMARY")
    print("=" * 80)
    
    # Threat detection accuracy
    threat_messages = [msg for conv in all_results["threats"] for msg in conv["results"]]
    threat_high_risk = sum(1 for msg in threat_messages if msg["risk_level"] == "high")
    
    print(f"\nThreat Scenarios:")
    print(f"  Total Messages: {len(threat_messages)}")
    print(f"  Detected as High Risk: {threat_high_risk} ({threat_high_risk/len(threat_messages)*100:.1f}%)")
    
    # False positive rate (safe messages flagged as threats)
    if include_safe:
        safe_messages = [msg for conv in all_results["safe"] for msg in conv["results"]]
        safe_high_risk = sum(1 for msg in safe_messages if msg["risk_level"] == "high")
        
        print(f"\nSafe Scenarios:")
        print(f"  Total Messages: {len(safe_messages)}")
        print(f"  False Positives (flagged as high risk): {safe_high_risk} ({safe_high_risk/len(safe_messages)*100:.1f}%)")
    
    # Intent distribution
    print(f"\nIntent Distribution (Threat Messages):")
    intents = {}
    for msg in threat_messages:
        intent = msg["intent"]
        intents[intent] = intents.get(intent, 0) + 1
    
    for intent, count in sorted(intents.items(), key=lambda x: x[1], reverse=True):
        print(f"  {intent}: {count} ({count/len(threat_messages)*100:.1f}%)")
    
    print("\n" + "=" * 80)
    print("Test Complete!")
    print("=" * 80)


def interactive_mode():
    """Interactive mode - type messages and see real-time analysis"""
    print("=" * 80)
    print("INTERACTIVE CHATBOT MODE")
    print("=" * 80)
    print("\nType messages to analyze (or 'quit' to exit)")
    print("Commands: 'threat' = run threat test, 'safe' = run safe test, 'all' = run all tests")
    print()
    
    while True:
        try:
            message = input("\nYou: ").strip()
            
            if not message:
                continue
            
            if message.lower() == 'quit':
                print("Goodbye!")
                break
            
            if message.lower() == 'threat':
                run_test_suite(include_safe=False, message_delay=1.0)
                continue
            
            if message.lower() == 'safe':
                for conv in SAFE_CONVERSATIONS:
                    simulate_conversation(conv, delay=1.0)
                continue
            
            if message.lower() == 'all':
                run_test_suite(include_safe=True, message_delay=1.0)
                continue
            
            # Analyze message
            result = client.analyze(message)
            
            risk_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
            emoji = risk_emoji.get(result.risk_level, "⚪")
            
            print(f"\n{emoji} Risk: {result.risk_level.upper()} ({result.risk_score:.1%})")
            print(f"Intent: {result.intent} (confidence: {result.intent_confidence:.1%})")
            
            if result.ai_generated:
                print(f"AI Generated: Yes ({result.ai_confidence:.1%})")
            
            if result.url_detected:
                print(f"URLs: {', '.join(result.domains)}")
            
            if result.keywords:
                print(f"Keywords: {', '.join(result.keywords[:5])}")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except GuardError as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    import sys
    
    print("\n" + "█" * 80)
    print("GUARD CHATBOT SIMULATOR")
    print("█" * 80)
    print("\nSelect mode:")
    print("1. Run full test suite (all scenarios)")
    print("2. Run only threat scenarios")
    print("3. Interactive mode (type your own messages)")
    print()
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        run_test_suite(include_safe=True, message_delay=1.5)
    elif choice == "2":
        run_test_suite(include_safe=False, message_delay=1.0)
    elif choice == "3":
        interactive_mode()
    else:
        print("Invalid choice. Running full test suite...")
        run_test_suite(include_safe=True, message_delay=1.5)
    
    client.close()
