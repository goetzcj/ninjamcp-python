"""OAuth2 client for NinjaRMM authentication."""

import asyncio
import hashlib
import secrets
import base64
import urllib.parse
from typing import Optional, Dict, Any
import logging
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import httpx

logger = logging.getLogger(__name__)


class OAuth2CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth2 callback."""
    
    def do_GET(self):
        """Handle GET request for OAuth2 callback."""
        # Parse the callback URL
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Store the authorization code
        if 'code' in query_params:
            self.server.auth_code = query_params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
            <html>
            <body>
            <h1>Authorization Successful!</h1>
            <p>You can close this window and return to your application.</p>
            <script>window.close();</script>
            </body>
            </html>
            """)
        else:
            error = query_params.get('error', ['Unknown error'])[0]
            self.server.auth_error = error
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"""
            <html>
            <body>
            <h1>Authorization Failed</h1>
            <p>Error: {error}</p>
            </body>
            </html>
            """.encode())
    
    def log_message(self, format, *args):
        """Suppress log messages."""
        pass


class OAuth2Client:
    """OAuth2 client for NinjaRMM authentication."""
    
    def __init__(self, base_url: str, client_id: str, client_secret: str, redirect_port: int = 8090):
        self.base_url = base_url.rstrip('/')
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_port = redirect_port
        self.redirect_uri = f"http://localhost:{redirect_port}/callback"
    
    def _generate_pkce_challenge(self) -> tuple[str, str]:
        """Generate PKCE code verifier and challenge."""
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        return code_verifier, code_challenge
    
    async def get_client_credentials_token(self, scope: str) -> Dict[str, Any]:
        """Get token using client credentials flow."""
        token_url = f"{self.base_url}/oauth/token"
        
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": scope
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def get_user_authorization_token(self, scope: str) -> Dict[str, Any]:
        """Get token using user authorization flow with PKCE."""
        # Generate PKCE parameters
        code_verifier, code_challenge = self._generate_pkce_challenge()
        state = secrets.token_urlsafe(32)
        
        # Build authorization URL
        auth_params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": scope,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }
        
        auth_url = f"{self.base_url}/oauth/authorize?" + urllib.parse.urlencode(auth_params)
        
        logger.info(f"Starting OAuth2 authorization flow on port {self.redirect_port}")
        logger.info(f"Authorization URL: {auth_url}")
        
        # Start local server for callback
        server = HTTPServer(('localhost', self.redirect_port), OAuth2CallbackHandler)
        server.auth_code = None
        server.auth_error = None
        
        # Start server in a separate thread
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        try:
            # Open browser for authorization
            webbrowser.open(auth_url)
            
            # Wait for callback
            timeout = 300  # 5 minutes
            for _ in range(timeout):
                if server.auth_code or server.auth_error:
                    break
                await asyncio.sleep(1)
            
            if server.auth_error:
                raise Exception(f"Authorization failed: {server.auth_error}")
            
            if not server.auth_code:
                raise Exception("Authorization timed out")
            
            # Exchange code for token
            return await self._exchange_code_for_token(server.auth_code, code_verifier)
            
        finally:
            server.shutdown()
            server_thread.join(timeout=1)
    
    async def _exchange_code_for_token(self, auth_code: str, code_verifier: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        token_url = f"{self.base_url}/oauth/token"
        
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": auth_code,
            "redirect_uri": self.redirect_uri,
            "code_verifier": code_verifier
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh an access token using refresh token."""
        token_url = f"{self.base_url}/oauth/token"
        
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data, headers=headers)
            response.raise_for_status()
            return response.json()
