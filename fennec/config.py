"""
Environment-based configuration management
"""

import os
from typing import List, Optional


class Config:
    """
    Configuration from environment variables
    """

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE-IN-PRODUCTION")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # CORS
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # JWT
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE", "3600"))
    JWT_REFRESH_TOKEN_EXPIRE: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE", "604800"))

    # Request limits
    MAX_REQUEST_SIZE: int = int(os.getenv("MAX_REQUEST_SIZE", str(10 * 1024 * 1024)))

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

    @classmethod
    def validate(cls) -> None:
        """
        Validate configuration

        Raises:
            ValueError: If configuration is invalid
        """
        errors = []

        # Check SECRET_KEY in production
        if not cls.DEBUG and cls.SECRET_KEY == "CHANGE-IN-PRODUCTION":
            errors.append("SECRET_KEY must be set in production!")

        # Validate PORT
        if not (1 <= cls.PORT <= 65535):
            errors.append(f"Invalid PORT: {cls.PORT}. Must be between 1 and 65535")

        # Validate token expiration times
        if cls.JWT_ACCESS_TOKEN_EXPIRE <= 0:
            errors.append("JWT_ACCESS_TOKEN_EXPIRE must be positive")

        if cls.JWT_REFRESH_TOKEN_EXPIRE <= 0:
            errors.append("JWT_REFRESH_TOKEN_EXPIRE must be positive")

        # Validate request size
        if cls.MAX_REQUEST_SIZE <= 0:
            errors.append("MAX_REQUEST_SIZE must be positive")

        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

    @classmethod
    def load_from_file(cls, filepath: str) -> None:
        """
        Load configuration from .env file

        Args:
            filepath: Path to .env file
        """
        if not os.path.exists(filepath):
            return

        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value

    @classmethod
    def get(cls, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get configuration value

        Args:
            key: Configuration key
            default: Default value if not found

        Returns:
            Configuration value or default
        """
        return os.getenv(key, default)

    @classmethod
    def set(cls, key: str, value: str) -> None:
        """
        Set configuration value

        Args:
            key: Configuration key
            value: Configuration value
        """
        os.environ[key] = value

    @classmethod
    def to_dict(cls) -> dict:
        """
        Convert configuration to dictionary

        Returns:
            Dictionary of configuration values
        """
        return {
            "SECRET_KEY": "***" if cls.SECRET_KEY != "CHANGE-IN-PRODUCTION" else cls.SECRET_KEY,
            "DEBUG": cls.DEBUG,
            "DATABASE_URL": "***" if cls.DATABASE_URL else "",
            "ALLOWED_ORIGINS": cls.ALLOWED_ORIGINS,
            "HOST": cls.HOST,
            "PORT": cls.PORT,
            "JWT_ALGORITHM": cls.JWT_ALGORITHM,
            "JWT_ACCESS_TOKEN_EXPIRE": cls.JWT_ACCESS_TOKEN_EXPIRE,
            "JWT_REFRESH_TOKEN_EXPIRE": cls.JWT_REFRESH_TOKEN_EXPIRE,
            "MAX_REQUEST_SIZE": cls.MAX_REQUEST_SIZE,
            "RATE_LIMIT_ENABLED": cls.RATE_LIMIT_ENABLED,
            "RATE_LIMIT_REQUESTS": cls.RATE_LIMIT_REQUESTS,
            "RATE_LIMIT_WINDOW": cls.RATE_LIMIT_WINDOW,
        }
