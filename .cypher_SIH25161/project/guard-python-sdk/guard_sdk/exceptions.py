"""
Guard SDK Exceptions
"""


class GuardError(Exception):
    """Base exception for Guard SDK errors."""
    pass


class AuthenticationError(GuardError):
    """Raised when API key authentication fails."""
    pass


class RateLimitError(GuardError):
    """Raised when rate limit is exceeded."""
    pass


class ValidationError(GuardError):
    """Raised when input validation fails."""
    pass
