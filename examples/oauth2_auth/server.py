"""
OAuth2 Authentication Example

Demonstrates OAuth2 Authorization Code Flow with Fennec Framework.
Includes authorization server and resource server.
"""

from fennec import Application, Router, JSONResponse, HTTPException, Request
from fennec.security import EnhancedJWTHandler, PasswordHasher
from typing import Dict, Optional
import secrets
import time
from urllib.parse import urlencode


# Configuration
SECRET_KEY = "your-secret-key-change-in-production"
AUTHORIZATION_CODE_EXPIRY = 600  # 10 minutes
ACCESS_TOKEN_EXPIRY = 3600  # 1 hour
REFRESH_TOKEN_EXPIRY = 604800  # 7 days


# In-memory storage (use database in production)
users_db = {
    "alice@example.com": {
        "id": 1,
        "email": "alice@example.com",
        "password": PasswordHasher.hash("password123"),
        "name": "Alice Johnson"
    },
    "bob@example.com": {
        "id": 2,
        "email": "bob@example.com",
        "password": PasswordHasher.hash("password456"),
        "name": "Bob Smith"
    }
}

# OAuth2 clients (applications that want to access user data)
clients_db = {
    "client123": {
        "client_id": "client123",
        "client_secret": "secret456",
        "redirect_uris": ["http://localhost:3000/callback"],
        "name": "My App"
    }
}

# Authorization codes (temporary codes exchanged for tokens)
auth_codes: Dict[str, dict] = {}

# JWT handler
jwt_handler = EnhancedJWTHandler(SECRET_KEY)


# Create application
app = Application(title="OAuth2 Server")
auth_router = Router(prefix="/oauth")
api_router = Router(prefix="/api")


# ============================================================================
# Authorization Endpoints
# ============================================================================

@auth_router.get("/authorize")
async def authorize(
    client_id: str,
    redirect_uri: str,
    response_type: str = "code",
    state: Optional[str] = None,
    scope: Optional[str] = None
):
    """
    OAuth2 Authorization Endpoint
    
    User is redirected here to grant access to the client application.
    """
    # Validate client
    if client_id not in clients_db:
        raise HTTPException(400, "Invalid client_id")
    
    client = clients_db[client_id]
    
    # Validate redirect_uri
    if redirect_uri not in client["redirect_uris"]:
        raise HTTPException(400, "Invalid redirect_uri")
    
    # Validate response_type
    if response_type != "code":
        raise HTTPException(400, "Unsupported response_type")
    
    # In a real app, show login/consent page
    # For this example, return HTML with login form
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OAuth2 Authorization</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 400px;
                margin: 50px auto;
                padding: 20px;
            }}
            .form-group {{
                margin-bottom: 15px;
            }}
            label {{
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }}
            input {{
                width: 100%;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }}
            button {{
                width: 100%;
                padding: 10px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }}
            button:hover {{
                background: #0056b3;
            }}
            .info {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 4px;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="info">
            <h2>Authorization Request</h2>
            <p><strong>{client["name"]}</strong> wants to access your account.</p>
            <p>Scopes: {scope or "basic profile"}</p>
        </div>
        
        <form id="loginForm">
            <div class="form-group">
                <label>Email:</label>
                <input type="email" name="email" required>
            </div>
            <div class="form-group">
                <label>Password:</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit">Authorize</button>
        </form>
        
        <script>
            document.getElementById('loginForm').onsubmit = async (e) => {{
                e.preventDefault();
                const formData = new FormData(e.target);
                const data = {{
                    email: formData.get('email'),
                    password: formData.get('password'),
                    client_id: '{client_id}',
                    redirect_uri: '{redirect_uri}',
                    state: '{state or ""}',
                    scope: '{scope or ""}'
                }};
                
                const response = await fetch('/oauth/authorize/consent', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(data)
                }});
                
                const result = await response.json();
                if (result.data && result.data.redirect_url) {{
                    window.location.href = result.data.redirect_url;
                }} else {{
                    alert('Login failed: ' + (result.message || 'Unknown error'));
                }}
            }};
        </script>
    </body>
    </html>
    """
    
    from fennec.request import Response
    return Response(html, status_code=200, headers={"content-type": "text/html"})


@auth_router.post("/authorize/consent")
async def authorize_consent(request: Request):
    """
    Process user consent and generate authorization code
    """
    body = await request.json()
    email = body.get("email")
    password = body.get("password")
    client_id = body.get("client_id")
    redirect_uri = body.get("redirect_uri")
    state = body.get("state")
    scope = body.get("scope", "")
    
    # Authenticate user
    if email not in users_db:
        raise HTTPException(401, "Invalid credentials")
    
    user = users_db[email]
    if not PasswordHasher.verify(password, user["password"]):
        raise HTTPException(401, "Invalid credentials")
    
    # Generate authorization code
    code = secrets.token_urlsafe(32)
    auth_codes[code] = {
        "user_id": user["id"],
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "expires_at": time.time() + AUTHORIZATION_CODE_EXPIRY
    }
    
    # Build redirect URL
    params = {"code": code}
    if state:
        params["state"] = state
    
    redirect_url = f"{redirect_uri}?{urlencode(params)}"
    
    return JSONResponse(data={"redirect_url": redirect_url})


@auth_router.post("/token")
async def token(
    grant_type: str,
    code: Optional[str] = None,
    refresh_token: Optional[str] = None,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    redirect_uri: Optional[str] = None
):
    """
    OAuth2 Token Endpoint
    
    Exchange authorization code for access token, or refresh access token.
    """
    # Validate client credentials
    if client_id not in clients_db:
        raise HTTPException(401, "Invalid client credentials")
    
    client = clients_db[client_id]
    if client["client_secret"] != client_secret:
        raise HTTPException(401, "Invalid client credentials")
    
    if grant_type == "authorization_code":
        # Exchange authorization code for tokens
        if not code:
            raise HTTPException(400, "Missing authorization code")
        
        if code not in auth_codes:
            raise HTTPException(400, "Invalid authorization code")
        
        auth_data = auth_codes[code]
        
        # Validate code hasn't expired
        if time.time() > auth_data["expires_at"]:
            del auth_codes[code]
            raise HTTPException(400, "Authorization code expired")
        
        # Validate client and redirect_uri match
        if auth_data["client_id"] != client_id:
            raise HTTPException(400, "Client mismatch")
        
        if auth_data["redirect_uri"] != redirect_uri:
            raise HTTPException(400, "Redirect URI mismatch")
        
        # Generate tokens
        user_id = auth_data["user_id"]
        scope = auth_data["scope"]
        
        access_token = jwt_handler.create_access_token(
            {"user_id": user_id, "scope": scope},
            expires_in=ACCESS_TOKEN_EXPIRY
        )
        
        refresh_token_str = jwt_handler.create_refresh_token(
            {"user_id": user_id, "scope": scope},
            expires_in=REFRESH_TOKEN_EXPIRY
        )
        
        # Delete used authorization code
        del auth_codes[code]
        
        return JSONResponse(data={
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": ACCESS_TOKEN_EXPIRY,
            "refresh_token": refresh_token_str,
            "scope": scope
        })
    
    elif grant_type == "refresh_token":
        # Refresh access token
        if not refresh_token:
            raise HTTPException(400, "Missing refresh token")
        
        try:
            # Verify and decode refresh token
            payload = jwt_handler.decode(refresh_token)
            
            if payload.get("type") != "refresh":
                raise HTTPException(400, "Invalid token type")
            
            # Generate new access token
            user_id = payload["user_id"]
            scope = payload.get("scope", "")
            
            new_access_token = jwt_handler.create_access_token(
                {"user_id": user_id, "scope": scope},
                expires_in=ACCESS_TOKEN_EXPIRY
            )
            
            return JSONResponse(data={
                "access_token": new_access_token,
                "token_type": "Bearer",
                "expires_in": ACCESS_TOKEN_EXPIRY,
                "scope": scope
            })
        
        except Exception as e:
            raise HTTPException(401, "Invalid refresh token")
    
    else:
        raise HTTPException(400, f"Unsupported grant_type: {grant_type}")


# ============================================================================
# Protected API Endpoints (Resource Server)
# ============================================================================

async def get_current_user(request: Request) -> dict:
    """Extract and validate access token"""
    auth_header = request.headers.get("authorization", "")
    
    if not auth_header.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid authorization header")
    
    token = auth_header[7:]  # Remove "Bearer " prefix
    
    try:
        payload = jwt_handler.decode(token)
        
        if payload.get("type") != "access":
            raise HTTPException(401, "Invalid token type")
        
        user_id = payload.get("user_id")
        
        # Find user
        for user in users_db.values():
            if user["id"] == user_id:
                return user
        
        raise HTTPException(401, "User not found")
    
    except Exception as e:
        raise HTTPException(401, f"Invalid access token: {str(e)}")


@api_router.get("/me")
async def get_profile(request: Request):
    """Get current user profile (protected endpoint)"""
    user = await get_current_user(request)
    
    return JSONResponse(data={
        "id": user["id"],
        "email": user["email"],
        "name": user["name"]
    })


@api_router.get("/data")
async def get_user_data(request: Request):
    """Get user data (protected endpoint)"""
    user = await get_current_user(request)
    
    return JSONResponse(data={
        "user_id": user["id"],
        "data": [
            {"id": 1, "title": "Item 1", "value": 100},
            {"id": 2, "title": "Item 2", "value": 200},
        ]
    })


# Include routers
app.include_router(auth_router)
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    print("🦊 Fennec OAuth2 Server")
    print("=" * 50)
    print("Authorization endpoint: http://localhost:8000/oauth/authorize")
    print("Token endpoint: http://localhost:8000/oauth/token")
    print("Protected API: http://localhost:8000/api/me")
    print("=" * 50)
    print("\nTest credentials:")
    print("  Email: alice@example.com")
    print("  Password: password123")
    print("\nClient credentials:")
    print("  Client ID: client123")
    print("  Client Secret: secret456")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
