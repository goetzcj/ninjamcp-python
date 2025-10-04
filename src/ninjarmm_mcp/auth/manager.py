"""Authentication manager for NinjaRMM MCP Server."""

import logging
from typing import Optional, Dict, Any
from ..models.auth import AuthStatus, TokenInfo
from .tokens import TokenManager
from .oauth import OAuth2Client

logger = logging.getLogger(__name__)


class AuthenticationManager:
    """Manages authentication for NinjaRMM API with hybrid OAuth2 flows."""
    
    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
        auth_mode: str = "hybrid",
        client_scopes: str = "monitoring management control",
        user_scopes: str = "monitoring management control",
        user_redirect_port: int = 8090,
        token_storage_path: str = "./tokens.json"
    ):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_mode = auth_mode
        self.client_scopes = client_scopes
        self.user_scopes = user_scopes
        
        # Initialize components
        self.token_manager = TokenManager(token_storage_path)
        self.oauth_client = OAuth2Client(base_url, client_id, client_secret, user_redirect_port)
        
        # Initialize auth status
        self.auth_status = AuthStatus(
            auth_mode=auth_mode,
            client_scopes=client_scopes,
            user_scopes=user_scopes
        )
    
    async def initialize(self) -> None:
        """Initialize the authentication manager."""
        await self.token_manager.load_tokens()
        await self._update_auth_status()
    
    async def _update_auth_status(self) -> None:
        """Update authentication status with current tokens."""
        tokens = self.token_manager.get_all_tokens()
        self.auth_status.tokens = tokens
        self.auth_status.update_capabilities()
    
    async def authenticate(self, operation: Optional[str] = None) -> str:
        """
        Authenticate and return access token for operation.
        
        Args:
            operation: Optional operation name for context-aware authentication
            
        Returns:
            Access token string
            
        Raises:
            Exception: If authentication fails
        """
        await self._update_auth_status()
        
        # Check if we have a valid token for this operation
        token = self.auth_status.get_best_token(operation)
        if token and token.is_valid():
            return token.access_token
        
        # Try to refresh user token if available
        user_token = self.auth_status.tokens["user"]
        if user_token.refresh_token and not user_token.is_valid():
            try:
                await self._refresh_user_token()
                await self._update_auth_status()
                token = self.auth_status.get_best_token(operation)
                if token and token.is_valid():
                    return token.access_token
            except Exception as e:
                logger.warning(f"Failed to refresh user token: {e}")
        
        # Determine which authentication flow to use
        if self.auth_mode == "client" or (
            self.auth_mode == "hybrid" and 
            operation and "ticket" not in operation.lower()
        ):
            # Use client credentials for non-ticket operations
            await self._authenticate_client_credentials()
        elif self.auth_mode == "user" or (
            self.auth_mode == "hybrid" and 
            operation and "ticket" in operation.lower()
        ):
            # Use user authorization for ticket operations
            await self._authenticate_user_authorization()
        else:
            # Default to client credentials
            await self._authenticate_client_credentials()
        
        await self._update_auth_status()
        token = self.auth_status.get_best_token(operation)
        if not token or not token.is_valid():
            raise Exception("Authentication failed - no valid token available")
        
        return token.access_token

    async def _authenticate_client_credentials(self) -> None:
        """Authenticate using client credentials flow."""
        try:
            logger.info("Authenticating with client credentials")
            token_data = await self.oauth_client.get_client_credentials_token(self.client_scopes)

            await self.token_manager.set_token(
                "client",
                token_data["access_token"],
                token_data["expires_in"],
                scope=token_data.get("scope")
            )

            logger.info("Client credentials authentication successful")

        except Exception as e:
            logger.error(f"Client credentials authentication failed: {e}")
            raise Exception(f"Client credentials authentication failed: {e}")

    async def _authenticate_user_authorization(self) -> None:
        """Authenticate using user authorization flow."""
        try:
            logger.info("Starting user authorization flow")
            token_data = await self.oauth_client.get_user_authorization_token(self.user_scopes)

            await self.token_manager.set_token(
                "user",
                token_data["access_token"],
                token_data["expires_in"],
                refresh_token=token_data.get("refresh_token"),
                scope=token_data.get("scope")
            )

            logger.info("User authorization authentication successful")

        except Exception as e:
            logger.error(f"User authorization authentication failed: {e}")
            raise Exception(f"User authorization authentication failed: {e}")

    async def _refresh_user_token(self) -> None:
        """Refresh user token using refresh token."""
        user_token = self.token_manager.get_token("user")
        if not user_token.refresh_token:
            raise Exception("No refresh token available")

        try:
            logger.info("Refreshing user token")
            token_data = await self.oauth_client.refresh_token(user_token.refresh_token)

            await self.token_manager.set_token(
                "user",
                token_data["access_token"],
                token_data["expires_in"],
                refresh_token=token_data.get("refresh_token", user_token.refresh_token),
                scope=token_data.get("scope")
            )

            logger.info("User token refresh successful")

        except Exception as e:
            logger.error(f"User token refresh failed: {e}")
            raise Exception(f"User token refresh failed: {e}")

    async def get_auth_status(self) -> AuthStatus:
        """Get current authentication status."""
        await self._update_auth_status()
        return self.auth_status

    async def reauthorize_user(self) -> None:
        """Force user re-authorization."""
        await self.token_manager.clear_token("user")
        await self._authenticate_user_authorization()

    async def clear_tokens(self, token_type: str = "all") -> None:
        """Clear stored tokens."""
        if token_type == "all":
            await self.token_manager.clear_all_tokens()
        else:
            await self.token_manager.clear_token(token_type)

        await self._update_auth_status()
