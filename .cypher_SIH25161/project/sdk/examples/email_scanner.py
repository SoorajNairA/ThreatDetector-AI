#!/usr/bin/env python3
"""
Email scanner example using Guard SDK
"""

from guard_sdk import GuardClient, GuardError

# Initialize client
client = GuardClient(
    api_key="your_api_key_here",
    base_url="http://localhost:8000"
)


def scan_email(sender, subject, body):
    """
    Scan email for threats.
    
    Args:
        sender: Email sender address
        subject: Email subject line
        body: Email body content
        
    Returns:
        dict with action, risk_level, and details
    """
    # Combine email parts
    full_text = f"From: {sender}\nSubject: {subject}\n\n{body}"
    
    try:
        # Analyze with Guardian
        result = client.analyze(full_text)
        
        # Determine action
        if result.is_high_risk():
            action = "BLOCK"
            reason = f"High risk {result.intent} detected"
        elif result.is_medium_risk():
            action = "QUARANTINE"
            reason = f"Suspicious {result.intent} content"
        else:
            action = "DELIVER"
            reason = "Safe"
        
        return {
            "action": action,
            "risk_level": result.risk_level,
            "risk_score": result.risk_score,
            "intent": result.intent,
            "reason": reason,
            "details": {
                "ai_generated": result.ai_generated,
                "urls_detected": result.url_detected,
                "domains": result.domains,
                "keywords": result.keywords
            }
        }
    
    except GuardError as e:
        print(f"Error scanning email: {e}")
        return {
            "action": "ERROR",
            "reason": str(e)
        }


# Example emails
test_emails = [
    {
        "sender": "security@paypal-verify.com",
        "subject": "URGENT: Account Verification Required",
        "body": "Your PayPal account has been limited. Click here immediately to verify your identity and restore access: http://bit.ly/paypal-verify"
    },
    {
        "sender": "boss@company.com",
        "subject": "Re: Project Update",
        "body": "Thanks for the update. Let's schedule a meeting tomorrow at 2pm to discuss the next steps."
    },
    {
        "sender": "winner@lottery-intl.com",
        "subject": "Congratulations! You Won $5,000,000",
        "body": "You have been selected as a winner of our international lottery. Send your bank details to claim your prize immediately!"
    },
    {
        "sender": "marketing@store.com",
        "subject": "50% Off Sale This Weekend",
        "body": "Shop our weekend sale with 50% off selected items. Visit our store or shop online. Unsubscribe anytime."
    }
]

print("=" * 80)
print("EMAIL SCANNER - Guard Security Platform")
print("=" * 80)
print()

for i, email in enumerate(test_emails, 1):
    print(f"Email #{i}")
    print("-" * 80)
    print(f"From: {email['sender']}")
    print(f"Subject: {email['subject']}")
    print(f"Body: {email['body'][:100]}...")
    print()
    
    # Scan email
    result = scan_email(email['sender'], email['subject'], email['body'])
    
    # Display result
    action_emoji = {
        "BLOCK": "🔴",
        "QUARANTINE": "🟡",
        "DELIVER": "🟢",
        "ERROR": "⚠️"
    }
    
    print(f"Action: {action_emoji.get(result['action'], '❓')} {result['action']}")
    print(f"Reason: {result['reason']}")
    
    if result['action'] != "ERROR":
        print(f"Risk Level: {result['risk_level'].upper()} ({result['risk_score']:.1%})")
        print(f"Intent: {result['intent']}")
        
        if result['details']['urls_detected']:
            print(f"⚠️ URLs detected: {', '.join(result['details']['domains'])}")
        
        if result['details']['keywords']:
            print(f"Keywords: {', '.join(result['details']['keywords'][:5])}")
    
    print()

client.close()

print("=" * 80)
print("Scan Complete")
print("=" * 80)
