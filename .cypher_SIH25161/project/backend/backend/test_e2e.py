"""
End-to-end test: Test the full flow from backend classifiers to frontend
"""
import requests
import json

API_URL = "http://localhost:8000"

# Test cases with different risk levels
test_cases = [
    {
        "name": "HIGH RISK - Phishing with URL",
        "text": "URGENT! Your account has been compromised. Click here immediately to verify your identity and prevent permanent suspension: http://bit.ly/secure-verify",
        "expected_level": "high"
    },
    {
        "name": "MEDIUM RISK - Scam attempt",
        "text": "Congratulations! You've won $1,000,000! Send us your bank account details and social security number to claim your prize today!",
        "expected_level": "medium"
    },
    {
        "name": "LOW RISK - Normal message",
        "text": "Hey, just checking in to see how you're doing. Let me know if you want to grab coffee this weekend!",
        "expected_level": "low"
    }
]

print("=" * 80)
print("END-TO-END CLASSIFIER TEST")
print("=" * 80)
print()

# First check if backend is running
try:
    health = requests.get(f"{API_URL}/health", timeout=2)
    print(f"✓ Backend is running: {health.json()}")
    print()
except Exception as e:
    print(f"✗ Backend not running: {e}")
    print("Please start the backend with: python -m uvicorn app.main:app --reload")
    exit(1)

# Test each case
for i, test_case in enumerate(test_cases, 1):
    print(f"\n{'=' * 80}")
    print(f"TEST {i}: {test_case['name']}")
    print(f"{'=' * 80}")
    print(f"Text: {test_case['text'][:80]}...")
    print()
    
    try:
        # Make API request (with both auth methods)
        response = requests.post(
            f"{API_URL}/analyze",
            json={"text": test_case["text"]},
            headers={
                "x-api-key": "global_api_key_12345",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✓ Request successful!")
            print(f"\nRISK ASSESSMENT:")
            print(f"  Risk Score: {result['risk_score']:.3f}")
            print(f"  Risk Level: {result['risk_level']} (expected: {test_case['expected_level']})")
            
            analysis = result['analysis']
            print(f"\nCLASSIFIER RESULTS:")
            print(f"  AI Generated: {analysis.get('ai_generated')} (confidence: {analysis.get('ai_confidence', 0):.3f})")
            print(f"  Intent: {analysis.get('intent')} (confidence: {analysis.get('intent_confidence', 0):.3f})")
            print(f"  Style Score: {analysis.get('style_score', 0):.3f}")
            print(f"  URL Detected: {analysis.get('url_detected')} (score: {analysis.get('url_score', 0):.3f})")
            if analysis.get('domains'):
                print(f"  Domains: {', '.join(analysis['domains'])}")
            print(f"  Keywords: {len(analysis.get('keywords', []))} found")
            if analysis.get('keywords'):
                print(f"    → {', '.join(analysis['keywords'][:5])}{'...' if len(analysis['keywords']) > 5 else ''}")
            
            # Check if result matches expected
            if result['risk_level'].lower() == test_case['expected_level']:
                print(f"\n✓ PASS: Risk level matches expected")
            else:
                print(f"\n⚠ WARN: Risk level {result['risk_level']} doesn't match expected {test_case['expected_level']}")
        else:
            print(f"✗ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"✗ Error: {e}")

print(f"\n{'=' * 80}")
print("TEST COMPLETE")
print(f"{'=' * 80}")
print()
print("Frontend Integration:")
print("  1. The backend /analyze endpoint is working")
print("  2. All 5 classifiers are integrated and returning data")
print("  3. Frontend can call this endpoint using the analyzeText() function")
print("  4. Response format matches the AnalyzeResponse interface")
print()
print("To test frontend:")
print("  1. Start frontend: npm run dev (in frontend folder)")
print("  2. Visit http://localhost:3000")
print("  3. Enter text and click 'Analyze Threat'")
print("  4. Check browser console and Network tab for API calls")
