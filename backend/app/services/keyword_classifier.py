# Keyword families for risk detection
KEYWORD_FAMILIES = {
    "urgency": [
        "urgent", "immediately", "quickly", "now", "asap", "right away",
        "act now", "limited time", "deadline", "expire", "expiring"
    ],
    "financial": [
        "bank", "account", "payment", "credit", "debit", "card",
        "transfer", "money", "wire", "refund", "invoice", "billing"
    ],
    "credentials": [
        "password", "login", "username", "verify", "confirm",
        "authenticate", "credentials", "sign in", "access", "account"
    ],
    "action_verbs": [
        "click", "click here", "tap", "download", "install",
        "update", "upgrade", "activate", "enable", "disable"
    ],
    "identity_theft": [
        "social security", "ssn", "date of birth", "drivers license",
        "passport", "identity", "personal information", "pii"
    ],
    "urgency_money": [
        "winning", "winner", "prize", "jackpot", "congratulations",
        "claim", "reward", "bonus", "free money", "unclaimed"
    ]
}

def predict(text: str):
    """
    Detect patterns of urgency, money, identity theft, and risk markers.
    
    Returns:
        keywords: list of matched keywords
        keyword_score: float [0, 1]
    """
    if not text:
        return {
            "keywords": [],
            "keyword_score": 0.0
        }
    
    text_lower = text.lower()
    keywords_found = []
    total_hits = 0
    high_risk_hits = 0
    
    # High-risk families (credentials, identity, financial urgency)
    high_risk_families = {"credentials", "identity_theft", "urgency_money"}
    
    for family, keywords in KEYWORD_FAMILIES.items():
        for keyword in keywords:
            if keyword in text_lower:
                keywords_found.append(keyword)
                total_hits += 1
                if family in high_risk_families:
                    high_risk_hits += 1
    
    # Score calculation
    # High-risk families weighted more heavily
    keyword_score = min(1.0, (high_risk_hits * 0.25) + (total_hits * 0.05))
    
    # Classify into categories based on keyword patterns
    category = "safe"
    confidence = 0.6
    
    # Check for specific threat categories
    has_credentials = any(k in text_lower for k in KEYWORD_FAMILIES["credentials"])
    has_urgency = any(k in text_lower for k in KEYWORD_FAMILIES["urgency"])
    has_financial = any(k in text_lower for k in KEYWORD_FAMILIES["financial"])
    has_action = any(k in text_lower for k in KEYWORD_FAMILIES["action_verbs"])
    has_identity = any(k in text_lower for k in KEYWORD_FAMILIES["identity_theft"])
    has_money = any(k in text_lower for k in KEYWORD_FAMILIES["urgency_money"])
    
    # Check for specific scam/spam indicators
    scam_keywords = ['congratulations', 'winner', 'won', 'prize', 'claim', 'jackpot', 'million', 'thousand']
    spam_keywords = ['buy now', 'limited time', 'offer', 'act now', 'exclusive', 'deal']
    
    has_scam = any(kw in text_lower for kw in scam_keywords)
    has_spam = any(kw in text_lower for kw in spam_keywords)
    
    # Phishing: credentials + urgency + action verbs
    if has_credentials and (has_urgency or has_action):
        category = "phishing"
        confidence = min(0.95, 0.7 + (keyword_score * 0.25))
    
    # Scam: money/prizes + urgency or winning language
    elif has_scam and (has_money or has_urgency):
        category = "scam"
        confidence = min(0.95, 0.70 + (keyword_score * 0.25))
    
    # Scam: Just strong scam keywords alone
    elif has_scam:
        category = "scam"
        confidence = min(0.90, 0.65 + (keyword_score * 0.25))
    
    # Identity theft: identity + financial
    elif has_identity and has_financial:
        category = "phishing"
        confidence = min(0.95, 0.75 + (keyword_score * 0.2))
    
    # Spam: urgency + action + spam keywords
    elif has_spam and has_urgency:
        category = "spam"
        confidence = min(0.90, 0.65 + (keyword_score * 0.25))
    
    # Spam: Just spam keywords with action verbs
    elif has_spam and has_action:
        category = "spam"
        confidence = min(0.85, 0.60 + (keyword_score * 0.25))
    
    # Propaganda check (for misinformation keywords)
    propaganda_keywords = ['fake news', 'hoax', 'conspiracy', 'coverup', 'wake up', 
                          'sheeple', 'mainstream media', 'they dont want you', 'propaganda']
    if any(kw in text_lower for kw in propaganda_keywords):
        category = "propaganda"
        confidence = 0.75
    
    # Safe if low keyword score
    elif keyword_score < 0.15:
        category = "safe"
        confidence = min(0.90, 0.6 + ((1.0 - keyword_score) * 0.3))
    
    return {
        "category": category,
        "confidence": float(confidence),
        "keywords": keywords_found,
        "keyword_score": float(keyword_score)
    }
