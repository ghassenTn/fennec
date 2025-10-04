# Security Improvements - Implementation Guide

## Quick Wins (Implement These First)

### 1. Add Security Headers Middleware

Create `framework/security/headers.py`:

```python
from fennec.middleware import Middleware

class SecurityHeadersMiddleware(Middleware):
    """
    Adds security headers to all responses
    """
    
    async def __call__(self, request, call_next):
        response = await call_next(request)
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        # HSTS (only if using HTTPS)
        if request.scope.get("scheme") == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
```

Usage:
```python
from fennec.security.headers import SecurityHeadersMiddleware

app.middleware_manager.add(SecurityHeadersMiddleware())
```

### 2. Add Password Hashing

Create `framework/security/password.py`:

```python
import bcrypt

class PasswordHasher:
    """
    Secure password hashing using bcrypt
    """
    
    @staticmethod
    def hash(password: str) -> str:
        """Hash a password"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()
    
    @staticmethod
    def verify(password: str, hashed: str) -> bool:
        """Verify a password against a hash"""
        try:
            return bcrypt.checkpw(password.encode(), hashed.encode())
        except Exception:
            return False
```

Install bcrypt:
```bash
pip install bcrypt
```

Usage:
```python
from fennec.security.password import PasswordHasher

# Hash password
hashed = PasswordHasher.hash("user_password")

# Verify password
is_valid = PasswordHasher.verify("user_password", hashed)
```

### 3. Add Request Size Limit Middleware

Create `framework/security/size_limit.py`:

```python
from fennec.middleware import Middleware
from fennec.exceptions import HTTPException

class RequestSizeLimitMiddleware(Middleware):
    """
    Limits request body size to prevent memory exhaustion
    """
    
    def __init__(self, max_size: int = 10 * 1024 * 1024):  # 10MB default
        self.max_size = max_size
    
    async def __call__(self, request, call_next):
        content_length = request.headers.get("content-length")
        
        if content_length:
            size = int(content_length)
            if size > self.max_size:
                raise HTTPException(
                    413,
                    f"Request too large. Maximum size: {self.max_size} bytes"
                )
        
        return await call_next(request)
```

Usage:
```python
from fennec.security.size_limit import RequestSizeLimitMiddleware

# Limit to 5MB
app.middleware_manager.add(RequestSizeLimitMiddleware(max_size=5 * 1024 * 1024))
```

### 4. Add Environment-based Configuration

Create `framework/config.py`:

```python
import os
from typing import List

class Config:
    """
    Application configuration from environment variables
    """
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE-ME-IN-PRODUCTION")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    # JWT
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION: int = int(os.getenv("JWT_EXPIRATION", "3600"))
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if cls.SECRET_KEY == "CHANGE-ME-IN-PRODUCTION":
            raise ValueError("SECRET_KEY must be set in production!")
        
        if cls.DEBUG and not cls.DATABASE_URL:
            print("WARNING: DATABASE_URL not set")
```

Usage:
```python
from fennec.config import Config

# Validate config on startup
Config.validate()

# Use config
app = Application(title="My API")
jwt = JWTHandler(secret_key=Config.SECRET_KEY)
```

Create `.env` file:
```bash
SECRET_KEY=your-super-secret-key-here
DEBUG=false
DATABASE_URL=postgresql://user:pass@localhost/db
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### 5. Improve JWT Security

Update `framework/security/auth.py`:

```python
class JWTHandler:
    """Enhanced JWT handler with refresh tokens"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.blacklist = set()  # In production, use Redis
    
    def encode(self, payload: Dict[str, Any], expires_in: int = 3600) -> str:
        """Create access token"""
        payload["exp"] = int(time.time()) + expires_in
        payload["type"] = "access"
        # ... rest of implementation
    
    def create_refresh_token(self, payload: Dict[str, Any]) -> str:
        """Create refresh token (longer expiration)"""
        payload["exp"] = int(time.time()) + (7 * 24 * 3600)  # 7 days
        payload["type"] = "refresh"
        # ... rest of implementation
    
    def revoke_token(self, token: str):
        """Revoke a token (add to blacklist)"""
        self.blacklist.add(token)
    
    def decode(self, token: str) -> Dict[str, Any]:
        """Decode and validate token"""
        if token in self.blacklist:
            raise UnauthorizedException("Token has been revoked")
        # ... rest of implementation
```

### 6. Add Input Sanitization

Create `framework/security/sanitize.py`:

```python
import html
import re

class InputSanitizer:
    """Sanitize user input"""
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """Escape HTML entities"""
        return html.escape(text)
    
    @staticmethod
    def sanitize_sql(text: str) -> str:
        """Remove SQL injection attempts"""
        # Remove common SQL keywords
        dangerous = ["DROP", "DELETE", "INSERT", "UPDATE", "SELECT", "--", ";"]
        for word in dangerous:
            text = text.replace(word, "")
        return text
    
    @staticmethod
    def sanitize_path(path: str) -> str:
        """Prevent path traversal"""
        # Remove ../ and similar
        path = path.replace("..", "")
        path = path.replace("~", "")
        return path
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """Validate and sanitize email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError("Invalid email format")
        return email.lower().strip()
```

## Production Deployment Checklist

### Before Deployment

```bash
# 1. Set environment variables
export SECRET_KEY=$(openssl rand -hex 32)
export DEBUG=false
export DATABASE_URL=postgresql://...
export ALLOWED_ORIGINS=https://yourdomain.com

# 2. Install production dependencies
pip install bcrypt python-dotenv gunicorn

# 3. Run with production server
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Nginx Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Docker Configuration

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Run application
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

## Testing Security

### 1. Test Security Headers

```bash
curl -I https://yourdomain.com/api/users
```

Should see:
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
```

### 2. Test Rate Limiting

```bash
for i in {1..150}; do
  curl https://yourdomain.com/api/users
done
```

Should get 429 after limit.

### 3. Test CORS

```bash
curl -H "Origin: https://evil.com" https://yourdomain.com/api/users
```

Should be blocked if not in ALLOWED_ORIGINS.

### 4. Test SQL Injection

```bash
curl -X POST https://yourdomain.com/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "test'; DROP TABLE users;--"}'
```

Should be sanitized or rejected.

## Monitoring

### Log Security Events

```python
import logging

security_logger = logging.getLogger("security")

# Log failed login attempts
security_logger.warning(f"Failed login attempt from {ip_address}")

# Log rate limit violations
security_logger.warning(f"Rate limit exceeded for {ip_address}")

# Log suspicious activity
security_logger.error(f"SQL injection attempt detected: {payload}")
```

### Set Up Alerts

Use tools like:
- Sentry for error tracking
- Datadog for monitoring
- CloudWatch for AWS
- Prometheus + Grafana

## Summary

Implement these improvements in order:

1. ✅ Security Headers Middleware (5 minutes)
2. ✅ Password Hashing (10 minutes)
3. ✅ Request Size Limits (5 minutes)
4. ✅ Environment Configuration (15 minutes)
5. ✅ JWT Improvements (30 minutes)
6. ✅ Input Sanitization (20 minutes)

Total time: ~1.5 hours for basic security hardening.

After these improvements, your framework will be **much more secure** for production use.
