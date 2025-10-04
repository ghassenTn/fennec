# OAuth2 Authentication Example 🦊

A complete OAuth2 Authorization Code Flow implementation using Fennec Framework.

## Features

- ✅ OAuth2 Authorization Code Flow
- ✅ Access tokens and refresh tokens
- ✅ Client authentication
- ✅ Protected API endpoints
- ✅ Token expiration and refresh
- ✅ User consent flow
- ✅ Secure password hashing

## Project Structure

```
oauth2_auth/
├── server.py           # OAuth2 authorization and resource server
├── client_example.py   # Example OAuth2 client
└── README.md           # This file
```

## OAuth2 Flow

```
┌────────┐                                  ┌─────────────┐
│        │                                  │             │
│ Client │                                  │    User     │
│  App   │                                  │             │
└───┬────┘                                  └──────┬──────┘
    │                                              │
    │ 1. Redirect to authorization URL            │
    ├─────────────────────────────────────────────>
    │                                              │
    │                    2. Login & Authorize     │
    │                    <─────────────────────────┤
    │                                              │
    │ 3. Redirect with authorization code         │
    <──────────────────────────────────────────────┤
    │                                              │
    │ 4. Exchange code for tokens                 │
    ├──────────────────────────>┌──────────────┐  │
    │                            │   OAuth2     │  │
    │ 5. Return access token     │   Server     │  │
    <────────────────────────────┤              │  │
    │                            └──────────────┘  │
    │ 6. Access protected API                      │
    ├──────────────────────────>                   │
    │                                              │
    │ 7. Return user data                          │
    <────────────────────────────                  │
    │                                              │
```

## Installation

```bash
pip install fennec uvicorn httpx
```

## Running the Server

```bash
python server.py
```

The server will start on `http://localhost:8000`

## Endpoints

### Authorization Endpoints

#### 1. Authorization Endpoint
```
GET /oauth/authorize
```

**Parameters:**
- `client_id` (required): Client application ID
- `redirect_uri` (required): Callback URL
- `response_type` (required): Must be "code"
- `state` (optional): Random string for CSRF protection
- `scope` (optional): Requested permissions

**Example:**
```
http://localhost:8000/oauth/authorize?client_id=client123&redirect_uri=http://localhost:3000/callback&response_type=code&state=xyz
```

#### 2. Token Endpoint
```
POST /oauth/token
```

**Parameters (Authorization Code Grant):**
- `grant_type`: "authorization_code"
- `code`: Authorization code from redirect
- `redirect_uri`: Same redirect URI used in authorization
- `client_id`: Client ID
- `client_secret`: Client secret

**Parameters (Refresh Token Grant):**
- `grant_type`: "refresh_token"
- `refresh_token`: Refresh token
- `client_id`: Client ID
- `client_secret`: Client secret

**Example:**
```bash
curl -X POST http://localhost:8000/oauth/token \
  -d "grant_type=authorization_code" \
  -d "code=AUTHORIZATION_CODE" \
  -d "redirect_uri=http://localhost:3000/callback" \
  -d "client_id=client123" \
  -d "client_secret=secret456"
```

**Response:**
```json
{
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "scope": "profile"
  }
}
```

### Protected API Endpoints

#### Get User Profile
```
GET /api/me
Authorization: Bearer ACCESS_TOKEN
```

**Example:**
```bash
curl http://localhost:8000/api/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "data": {
    "id": 1,
    "email": "alice@example.com",
    "name": "Alice Johnson"
  }
}
```

#### Get User Data
```
GET /api/data
Authorization: Bearer ACCESS_TOKEN
```

## Using the Client Example

The `client_example.py` demonstrates how to implement an OAuth2 client:

```bash
python client_example.py
```

Follow the interactive prompts:

1. Copy the authorization URL and open it in your browser
2. Login with test credentials:
   - Email: `alice@example.com`
   - Password: `password123`
3. After authorization, copy the code from the redirect URL
4. Paste the code into the terminal
5. The client will exchange the code for tokens and make API requests

## Test Credentials

### Users
- **Email:** alice@example.com  
  **Password:** password123

- **Email:** bob@example.com  
  **Password:** password456

### OAuth2 Client
- **Client ID:** client123
- **Client Secret:** secret456
- **Redirect URI:** http://localhost:3000/callback

## Implementation Details

### Authorization Code Flow

1. **Authorization Request**: Client redirects user to authorization endpoint
2. **User Authentication**: User logs in and grants permission
3. **Authorization Code**: Server redirects back with temporary code
4. **Token Exchange**: Client exchanges code for access token
5. **API Access**: Client uses access token to access protected resources
6. **Token Refresh**: Client uses refresh token to get new access token

### Security Features

1. **Password Hashing**: Passwords hashed with bcrypt
2. **JWT Tokens**: Signed tokens with expiration
3. **Client Authentication**: Client secret validation
4. **Code Expiration**: Authorization codes expire after 10 minutes
5. **Token Expiration**: Access tokens expire after 1 hour
6. **Refresh Tokens**: Long-lived tokens for getting new access tokens
7. **State Parameter**: CSRF protection

### Token Structure

**Access Token Payload:**
```json
{
  "user_id": 1,
  "scope": "profile",
  "type": "access",
  "exp": 1234567890
}
```

**Refresh Token Payload:**
```json
{
  "user_id": 1,
  "scope": "profile",
  "type": "refresh",
  "exp": 1234567890
}
```

## Integrating with Your Application

### Step 1: Register Your Client

Add your client to `clients_db`:

```python
clients_db["your_client_id"] = {
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "redirect_uris": ["https://yourapp.com/callback"],
    "name": "Your App Name"
}
```

### Step 2: Implement Authorization Flow

```python
from oauth2_client import OAuth2Client

client = OAuth2Client(
    client_id="your_client_id",
    client_secret="your_client_secret",
    authorization_url="http://localhost:8000/oauth/authorize",
    token_url="http://localhost:8000/oauth/token",
    redirect_uri="https://yourapp.com/callback"
)

# Redirect user to authorization URL
auth_url = client.get_authorization_url(state="random_state")
# redirect_to(auth_url)
```

### Step 3: Handle Callback

```python
# In your callback endpoint
@app.get("/callback")
async def callback(code: str, state: str):
    # Exchange code for token
    token_data = await client.exchange_code_for_token(code)
    
    # Store tokens securely
    # session["access_token"] = token_data["access_token"]
    # session["refresh_token"] = token_data["refresh_token"]
    
    return "Authorization successful!"
```

### Step 4: Make API Requests

```python
# Use access token to make API requests
profile = await client.make_api_request("http://localhost:8000/api/me")
```

## Advanced Features

### Scopes

Add scope-based permissions:

```python
SCOPES = {
    "profile": "Access basic profile information",
    "email": "Access email address",
    "data": "Access user data"
}

# Check scope in protected endpoints
def require_scope(required_scope: str):
    def decorator(func):
        async def wrapper(request: Request):
            user = await get_current_user(request)
            token_scope = user.get("scope", "")
            
            if required_scope not in token_scope:
                raise HTTPException(403, f"Missing required scope: {required_scope}")
            
            return await func(request)
        return wrapper
    return decorator

@api_router.get("/email")
@require_scope("email")
async def get_email(request: Request):
    user = await get_current_user(request)
    return JSONResponse(data={"email": user["email"]})
```

### PKCE (Proof Key for Code Exchange)

For public clients (mobile apps, SPAs):

```python
import hashlib
import base64

# Client generates code verifier
code_verifier = secrets.token_urlsafe(32)

# Client generates code challenge
code_challenge = base64.urlsafe_b64encode(
    hashlib.sha256(code_verifier.encode()).digest()
).decode().rstrip('=')

# Include in authorization request
auth_url = f"{auth_url}&code_challenge={code_challenge}&code_challenge_method=S256"

# Include verifier in token request
token_data = await client.post(token_url, data={
    "code": code,
    "code_verifier": code_verifier,
    ...
})
```

### Token Revocation

```python
@auth_router.post("/revoke")
async def revoke_token(token: str, token_type_hint: str = "access_token"):
    """Revoke access or refresh token"""
    jwt_handler.revoke_token(token)
    return JSONResponse(data={"message": "Token revoked"})
```

## Production Considerations

1. **Use HTTPS**: Always use HTTPS in production
2. **Secure Storage**: Store tokens securely (encrypted database, not localStorage)
3. **Rate Limiting**: Limit token endpoint requests
4. **Audit Logging**: Log all authorization and token requests
5. **Token Rotation**: Rotate refresh tokens on use
6. **Scope Validation**: Validate scopes on every request
7. **Client Registration**: Implement dynamic client registration
8. **Multi-Factor Auth**: Add MFA to authorization flow
9. **Session Management**: Implement proper session handling
10. **Database**: Use database instead of in-memory storage

## Testing

### Manual Testing

1. Start the server
2. Open authorization URL in browser
3. Login and authorize
4. Copy authorization code from redirect
5. Exchange code for token using curl
6. Use token to access protected endpoints

### Automated Testing

```python
import pytest
from fennec.testing import TestClient

@pytest.mark.asyncio
async def test_oauth_flow():
    client = TestClient(app)
    
    # Test authorization endpoint
    response = client.get("/oauth/authorize", params={
        "client_id": "client123",
        "redirect_uri": "http://localhost:3000/callback",
        "response_type": "code"
    })
    assert response.status_code == 200
    
    # Test token exchange
    response = client.post("/oauth/token", data={
        "grant_type": "authorization_code",
        "code": "test_code",
        "client_id": "client123",
        "client_secret": "secret456"
    })
    assert response.status_code == 200
```

## Learn More

- [OAuth 2.0 Specification](https://oauth.net/2/)
- [RFC 6749 - OAuth 2.0](https://tools.ietf.org/html/rfc6749)
- [OAuth 2.0 Security Best Practices](https://tools.ietf.org/html/draft-ietf-oauth-security-topics)
- [PKCE Extension](https://tools.ietf.org/html/rfc7636)
- [Fennec Documentation](https://github.com/your-repo/fennec)
