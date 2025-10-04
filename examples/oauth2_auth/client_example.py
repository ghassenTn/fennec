"""
OAuth2 Client Example

Demonstrates how a client application would interact with the OAuth2 server.
"""

import httpx
from urllib.parse import urlencode, parse_qs, urlparse


class OAuth2Client:
    """Simple OAuth2 client"""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        authorization_url: str,
        token_url: str,
        redirect_uri: str
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorization_url = authorization_url
        self.token_url = token_url
        self.redirect_uri = redirect_uri
        self.access_token = None
        self.refresh_token = None
    
    def get_authorization_url(self, state: str = None, scope: str = None) -> str:
        """
        Generate authorization URL to redirect user to
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code"
        }
        
        if state:
            params["state"] = state
        
        if scope:
            params["scope"] = scope
        
        return f"{self.authorization_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> dict:
        """
        Exchange authorization code for access token
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Token exchange failed: {response.text}")
            
            token_data = response.json()["data"]
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data.get("refresh_token")
            
            return token_data
    
    async def refresh_access_token(self) -> dict:
        """
        Refresh access token using refresh token
        """
        if not self.refresh_token:
            raise Exception("No refresh token available")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Token refresh failed: {response.text}")
            
            token_data = response.json()["data"]
            self.access_token = token_data["access_token"]
            
            return token_data
    
    async def make_api_request(self, url: str) -> dict:
        """
        Make authenticated API request
        """
        if not self.access_token:
            raise Exception("No access token available")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            
            if response.status_code == 401:
                # Try to refresh token
                await self.refresh_access_token()
                
                # Retry request
                response = await client.get(
                    url,
                    headers={"Authorization": f"Bearer {self.access_token}"}
                )
            
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.text}")
            
            return response.json()


async def main():
    """Example OAuth2 flow"""
    
    # Initialize OAuth2 client
    client = OAuth2Client(
        client_id="client123",
        client_secret="secret456",
        authorization_url="http://localhost:8000/oauth/authorize",
        token_url="http://localhost:8000/oauth/token",
        redirect_uri="http://localhost:3000/callback"
    )
    
    # Step 1: Get authorization URL
    auth_url = client.get_authorization_url(state="random_state", scope="profile")
    print("Step 1: Authorization URL")
    print(f"Redirect user to: {auth_url}")
    print()
    
    # Step 2: User authorizes and is redirected back with code
    # In a real app, this would be handled by your callback endpoint
    print("Step 2: User authorizes")
    print("After user authorizes, they are redirected to:")
    print("http://localhost:3000/callback?code=AUTHORIZATION_CODE&state=random_state")
    print()
    
    # For testing, you can manually get the code from the redirect
    authorization_code = input("Enter authorization code from redirect: ")
    
    # Step 3: Exchange code for access token
    print("\nStep 3: Exchange code for token")
    try:
        token_data = await client.exchange_code_for_token(authorization_code)
        print(f"✓ Access token: {token_data['access_token'][:20]}...")
        print(f"✓ Refresh token: {token_data['refresh_token'][:20]}...")
        print(f"✓ Expires in: {token_data['expires_in']} seconds")
        print()
    except Exception as e:
        print(f"✗ Error: {e}")
        return
    
    # Step 4: Make authenticated API requests
    print("Step 4: Make API requests")
    try:
        # Get user profile
        profile = await client.make_api_request("http://localhost:8000/api/me")
        print(f"✓ User profile: {profile['data']}")
        
        # Get user data
        data = await client.make_api_request("http://localhost:8000/api/data")
        print(f"✓ User data: {data['data']}")
        print()
    except Exception as e:
        print(f"✗ Error: {e}")
        return
    
    # Step 5: Refresh token (optional)
    print("Step 5: Refresh access token")
    try:
        new_token_data = await client.refresh_access_token()
        print(f"✓ New access token: {new_token_data['access_token'][:20]}...")
        print()
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    import asyncio
    print("🦊 OAuth2 Client Example")
    print("=" * 50)
    print("Make sure the OAuth2 server is running on port 8000")
    print("=" * 50)
    print()
    
    asyncio.run(main())
