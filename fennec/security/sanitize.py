"""
Input sanitization utilities
"""

import html
import re
from typing import Optional
from urllib.parse import urlparse


class InputSanitizer:
    """
    Utilities for sanitizing and validating user input
    """

    @staticmethod
    def sanitize_html(text: str) -> str:
        """
        Escape HTML entities to prevent XSS attacks

        Args:
            text: Input text

        Returns:
            HTML-escaped text
        """
        return html.escape(text)

    @staticmethod
    def sanitize_sql(text: str) -> str:
        """
        Remove common SQL injection patterns

        Note: This is NOT a replacement for parameterized queries!
        Always use parameterized queries for database operations.

        Args:
            text: Input text

        Returns:
            Sanitized text
        """
        # Remove common SQL injection patterns
        dangerous_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
            r"(--|;|\/\*|\*\/)",
            r"(\bOR\b.*=.*)",
            r"(\bAND\b.*=.*)",
            r"('|\")",
        ]

        sanitized = text
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)

        return sanitized.strip()

    @staticmethod
    def validate_email(email: str) -> str:
        """
        Validate and sanitize email address

        Args:
            email: Email address

        Returns:
            Sanitized email address

        Raises:
            ValueError: If email format is invalid
        """
        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        email = email.strip().lower()

        if not re.match(pattern, email):
            raise ValueError("Invalid email format")

        # Additional length check
        if len(email) > 254:  # RFC 5321
            raise ValueError("Email address too long")

        return email

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal attacks

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove path separators and dangerous characters
        sanitized = re.sub(r'[/\\:*?"<>|]', '', filename)

        # Remove leading dots to prevent hidden files
        sanitized = sanitized.lstrip('.')

        # Limit length
        if len(sanitized) > 255:
            sanitized = sanitized[:255]

        # Ensure we have a valid filename
        if not sanitized:
            sanitized = "unnamed"

        return sanitized

    @staticmethod
    def validate_url(url: str, allowed_schemes: Optional[list] = None) -> str:
        """
        Validate and sanitize URL

        Args:
            url: URL to validate
            allowed_schemes: List of allowed URL schemes (default: ['http', 'https'])

        Returns:
            Validated URL

        Raises:
            ValueError: If URL is invalid or uses disallowed scheme
        """
        if allowed_schemes is None:
            allowed_schemes = ['http', 'https']

        try:
            parsed = urlparse(url)

            if not parsed.scheme:
                raise ValueError("URL must include a scheme (http/https)")

            if parsed.scheme not in allowed_schemes:
                raise ValueError(f"URL scheme must be one of: {', '.join(allowed_schemes)}")

            if not parsed.netloc:
                raise ValueError("URL must include a domain")

            return url

        except Exception as e:
            raise ValueError(f"Invalid URL: {str(e)}")

    @staticmethod
    def sanitize_path(path: str) -> str:
        """
        Sanitize file path to prevent directory traversal

        Args:
            path: File path

        Returns:
            Sanitized path

        Raises:
            ValueError: If path contains traversal attempts
        """
        # Check for path traversal attempts
        if '..' in path or path.startswith('/'):
            raise ValueError("Path traversal detected")

        # Remove dangerous characters
        sanitized = re.sub(r'[^\w\s\-./]', '', path)

        return sanitized

    @staticmethod
    def sanitize_alphanumeric(text: str, allow_spaces: bool = False) -> str:
        """
        Keep only alphanumeric characters

        Args:
            text: Input text
            allow_spaces: Whether to allow spaces

        Returns:
            Sanitized text with only alphanumeric characters
        """
        if allow_spaces:
            return re.sub(r'[^\w\s]', '', text)
        else:
            return re.sub(r'[^\w]', '', text)

    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = "...") -> str:
        """
        Truncate text to maximum length

        Args:
            text: Input text
            max_length: Maximum length
            suffix: Suffix to add if truncated

        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text

        return text[:max_length - len(suffix)] + suffix
