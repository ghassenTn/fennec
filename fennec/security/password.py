"""
Password hashing and verification using bcrypt
"""

import bcrypt


class PasswordHasher:
    """
    Secure password hashing using bcrypt
    """

    @staticmethod
    def hash(password: str, rounds: int = 12) -> str:
        """
        Hash password with bcrypt

        Args:
            password: Plain text password
            rounds: Cost factor (default: 12)

        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt(rounds=rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify(password: str, hashed: str) -> bool:
        """
        Verify password against hash

        Args:
            password: Plain text password
            hashed: Hashed password

        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
