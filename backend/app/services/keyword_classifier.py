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
    
    return {
        "keywords": keywords_found,
        "keyword_score": float(keyword_score)
    }
