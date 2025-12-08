"""
Guard Security Platform - Python SDK
Official SDK for integrating Guard's threat analysis API.
"""

__version__ = "1.0.0"
__all__ = ["GuardClient", "GuardError", "AuthenticationError", "RateLimitError"]

from .client import GuardClient
from .exceptions import GuardError, AuthenticationError, RateLimitError
