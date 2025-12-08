import re
from urllib.parse import urlparse

# Suspicious URL shorteners
URL_SHORTENERS = {
    "bit.ly", "tinyurl.com", "goo.gl", "ow.ly", "t.co",
    "buff.ly", "adf.ly", "is.gd", "cli.gs", "yfrog.com",
    "shorte.st", "go2l.ink", "x.co", "prettylinkpro.com",
    "scrnch.me", "filoops.info", "vzturl.com", "qr.net",
    "1url.com", "tweez.me", "v.gd", "tr.im", "link.zip"
}

# Suspicious TLDs (top-level domains)
SUSPICIOUS_TLDS = {
    ".tk", ".ml", ".ga", ".cf", ".gq",  # Free domains often abused
    ".xyz", ".top", ".club", ".loan", ".work",
    ".click", ".link", ".download", ".racing", ".date",
    ".stream", ".review", ".country", ".science", ".party",
    ".win", ".bid", ".trade", ".webcam", ".faith"
}

# Known bad/phishing domains (example list - expand as needed)
KNOWN_BAD_DOMAINS = {
    "paypai.com",  # homoglyph of paypal
    "amaz0n.com",  # 0 instead of o
    "g00gle.com",
    "micros0ft.com",
    "facebo0k.com"
}

# Safe domains (whitelist for well-known sites)
SAFE_DOMAINS = {
    "google.com", "youtube.com", "facebook.com", "amazon.com",
    "wikipedia.org", "reddit.com", "twitter.com", "instagram.com",
    "linkedin.com", "github.com", "stackoverflow.com", "microsoft.com",
    "apple.com", "paypal.com", "ebay.com", "netflix.com"
}


def extract_urls(text: str) -> list:
    """
    Extract all URLs from text using regex.
    
    Returns:
        List of URL strings found in text
    """
    # Regex pattern for URLs
    url_pattern = r'https?://[^\s<>"{}\\|^`\[\]]+'
    return re.findall(url_pattern, text, re.IGNORECASE)


def check_homoglyphs(domain: str) -> bool:
    """
    Check if domain contains homoglyph characters (lookalike substitutions).
    
    Examples:
        - paypa1.com (1 instead of l)
        - g00gle.com (0 instead of o)
    """
    # Common homoglyph substitutions
    homoglyphs = {
        '0': 'o', '1': 'l', '1': 'i',
        'rn': 'm', 'vv': 'w', 'cl': 'd'
    }
    
    domain_lower = domain.lower()
    
    # Check for numeric substitutions in known brand names
    suspicious_patterns = [
        ('0', ['google', 'microsoft', 'paypal', 'amazon']),
        ('1', ['paypal', 'email', 'login']),
    ]
    
    for char, brands in suspicious_patterns:
        if char in domain_lower:
            for brand in brands:
                if brand.replace('o', '0') in domain_lower or brand.replace('l', '1') in domain_lower:
                    return True
    
    return False


def predict(text: str) -> dict:
    """
    Detect and score risk from URLs in text.
    
    Args:
        text: Plain text to analyze
    
    Returns:
        Dictionary with:
        - url_detected: bool
        - url_score: float [0.0-1.0] (0=safe, 1=high risk)
        - domains: list of domain names found
        - risk_factors: list of identified risk factors
    """
    if not text:
        return {
            "url_detected": False,
            "url_score": 0.0,
            "domains": [],
            "risk_factors": []
        }
    
    # Extract all URLs
    urls = extract_urls(text)
    
    if not urls:
        return {
            "url_detected": False,
            "url_score": 0.0,
            "domains": [],
            "risk_factors": []
        }
    
    # Analyze each URL
    domains = []
    risk_factors = []
    total_risk_score = 0.0
    
    for url in urls:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            if not domain:
                continue
                
            domains.append(domain)
            url_risk = 0.0
            
            # Check 1: Known bad domain
            if domain in KNOWN_BAD_DOMAINS:
                url_risk = 1.0
                risk_factors.append(f"Known malicious domain: {domain}")
            
            # Check 2: Safe domain (whitelist)
            elif any(safe_domain in domain for safe_domain in SAFE_DOMAINS):
                url_risk = 0.0  # Trusted domain
            
            # Check 3: URL shortener
            elif domain in URL_SHORTENERS:
                url_risk += 0.6
                risk_factors.append(f"URL shortener: {domain}")
            
            # Check 4: Suspicious TLD
            elif any(domain.endswith(tld) for tld in SUSPICIOUS_TLDS):
                url_risk += 0.7
                risk_factors.append(f"Suspicious TLD: {domain}")
            
            # Check 5: Homoglyph attack
            elif check_homoglyphs(domain):
                url_risk += 0.9
                risk_factors.append(f"Possible homoglyph attack: {domain}")
            
            # Check 6: IP address instead of domain
            elif re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
                url_risk += 0.5
                risk_factors.append(f"IP address used: {domain}")
            
            # Check 7: Excessive subdomains (e.g., secure.login.paypal.phishing.com)
            elif domain.count('.') > 3:
                url_risk += 0.4
                risk_factors.append(f"Excessive subdomains: {domain}")
            
            # Check 8: Suspicious keywords in domain
            suspicious_keywords = ['login', 'verify', 'secure', 'account', 'update', 'confirm']
            if any(keyword in domain for keyword in suspicious_keywords):
                url_risk += 0.3
                risk_factors.append(f"Suspicious keyword in domain: {domain}")
            
            total_risk_score += min(1.0, url_risk)
            
        except Exception:
            # If URL parsing fails, consider it suspicious
            total_risk_score += 0.5
            risk_factors.append(f"Malformed URL: {url}")
    
    # Average risk across all URLs
    avg_risk_score = min(1.0, total_risk_score / len(urls)) if urls else 0.0
    
    return {
        "url_detected": True,
        "url_score": float(avg_risk_score),
        "domains": list(set(domains)),  # Remove duplicates
        "risk_factors": risk_factors
    }
