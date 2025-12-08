"""
Guard API Client
"""

import time
from typing import Dict, Optional, List
import requests

from .exceptions import GuardError, AuthenticationError, RateLimitError


class GuardClient:
    """
    Client for Guard Security Platform API.
    
    Example:
        >>> from guard_sdk import GuardClient
        >>> client = GuardClient(api_key="your_api_key")
        >>> result = client.analyze("Click here to verify your account")
        >>> print(result.risk_level)
        'high'
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000",
        timeout: int = 30
    ):
        """
        Initialize Guard client.
        
        Args:
            api_key: Your Guard API key
            base_url: Base URL of Guard API (default: http://localhost:8000)
            timeout: Request timeout in seconds (default: 30)
        """
        if not api_key:
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "X-API-Key": api_key,
            "Content-Type": "application/json",
            "User-Agent": f"guard-python-sdk/1.0.0"
        })
    
    def analyze(
        self,
        text: str,
        sandbox: bool = False,
        metadata: Optional[Dict] = None
    ) -> "AnalysisResult":
        """
        Analyze text for threats.
        
        Args:
            text: Text to analyze
            sandbox: Use sandbox mode (faster, mock data)
            metadata: Optional metadata to attach
            
        Returns:
            AnalysisResult object with risk_level, risk_score, and detailed analysis
            
        Raises:
            AuthenticationError: Invalid API key
            RateLimitError: Rate limit exceeded
            GuardianError: Other API errors
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        payload = {
            "text": text,
            "sandbox": sandbox
        }
        
        if metadata:
            payload["metadata"] = metadata
        
        try:
            response = self._session.post(
                f"{self.base_url}/analyze",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded. Please try again later.")
            elif response.status_code != 200:
                error_msg = response.json().get("detail", "Unknown error")
                raise GuardianError(f"API error: {error_msg}")
            
            data = response.json()
            return AnalysisResult(data)
            
        except requests.exceptions.Timeout:
            raise GuardError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise GuardError(f"Could not connect to Guard API at {self.base_url}")
        except requests.exceptions.RequestException as e:
            raise GuardError(f"Request failed: {str(e)}")
    
    def batch_analyze(
        self,
        texts: List[str],
        sandbox: bool = False,
        delay: float = 0.1
    ) -> List["AnalysisResult"]:
        """
        Analyze multiple texts (with rate limiting).
        
        Args:
            texts: List of texts to analyze
            sandbox: Use sandbox mode
            delay: Delay between requests in seconds (default: 0.1)
            
        Returns:
            List of AnalysisResult objects
        """
        results = []
        for text in texts:
            result = self.analyze(text, sandbox=sandbox)
            results.append(result)
            if delay > 0:
                time.sleep(delay)
        return results
    
    def create_api_key(self, name: str) -> Dict:
        """
        Create a new API key.
        
        Args:
            name: Name for the API key
            
        Returns:
            Dict with 'key' and 'key_id'
        """
        response = self._session.post(
            f"{self.base_url}/accounts/api-keys",
            json={"name": name},
            timeout=self.timeout
        )
        
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        elif response.status_code != 200:
            raise GuardError(f"Failed to create API key: {response.text}")
        
        return response.json()
    
    def list_api_keys(self) -> List[Dict]:
        """
        List all API keys for your account.
        
        Returns:
            List of API key objects
        """
        response = self._session.get(
            f"{self.base_url}/accounts/api-keys",
            timeout=self.timeout
        )
        
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        elif response.status_code != 200:
            raise GuardError(f"Failed to list API keys: {response.text}")
        
        return response.json()
    
    def revoke_api_key(self, key_id: str) -> None:
        """
        Revoke an API key.
        
        Args:
            key_id: ID of the key to revoke
        """
        response = self._session.delete(
            f"{self.base_url}/accounts/api-keys/{key_id}",
            timeout=self.timeout
        )
        
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        elif response.status_code != 200:
            raise GuardError(f"Failed to revoke API key: {response.text}")
    
    def health_check(self) -> Dict:
        """
        Check API health status.
        
        Returns:
            Dict with status information
        """
        try:
            response = self._session.get(
                f"{self.base_url}/health",
                timeout=5
            )
            return response.json()
        except Exception as e:
            raise GuardError(f"Health check failed: {str(e)}")
    
    def close(self):
        """Close the HTTP session."""
        self._session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class AnalysisResult:
    """
    Result from threat analysis.
    """
    
    def __init__(self, data: Dict):
        """Initialize from API response data."""
        self._data = data
        self.risk_level = data.get("risk_level", "unknown")
        self.risk_score = data.get("risk_score", 0.0)
        self.timestamp = data.get("timestamp")
        self.message = data.get("message", "")
        
        # Analysis details
        analysis = data.get("analysis", {})
        self.ai_generated = analysis.get("ai_generated", False)
        self.ai_confidence = analysis.get("ai_confidence", 0.0)
        self.human_confidence = analysis.get("human_confidence", 0.0)
        self.intent = analysis.get("intent", "unknown")
        self.intent_confidence = analysis.get("intent_confidence", 0.0)
        self.style_score = analysis.get("style_score", 0.0)
        self.url_detected = analysis.get("url_detected", False)
        self.url_score = analysis.get("url_score", 0.0)
        self.domains = analysis.get("domains", [])
        self.keywords = analysis.get("keywords", [])
        self.keyword_score = analysis.get("keyword_score", 0.0)
    
    def is_high_risk(self) -> bool:
        """Check if result is high risk."""
        return self.risk_level == "high"
    
    def is_medium_risk(self) -> bool:
        """Check if result is medium risk."""
        return self.risk_level == "medium"
    
    def is_low_risk(self) -> bool:
        """Check if result is low risk."""
        return self.risk_level == "low"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return self._data
    
    def __repr__(self):
        return f"<AnalysisResult risk_level='{self.risk_level}' risk_score={self.risk_score:.3f}>"
    
    def __str__(self):
        return f"Risk: {self.risk_level.upper()} ({self.risk_score:.1%}), Intent: {self.intent}"
