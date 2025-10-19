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
        token_storage_path: str = "./tokens.json",
        has_machine_credentials: bool = True
    ):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_mode = auth_mode
        self.client_scopes = client_scopes
        self.user_scopes = user_scopes
        self.has_machine_credentials = has_machine_credentials

        # Initialize components
        self.token_manager = TokenManager(token_storage_path)
        # Only initialize OAuth client if we have real credentials
        if has_machine_credentials:
            self.oauth_client = OAuth2Client(base_url, client_id, client_secret, user_redirect_port)
        else:
            self.oauth_client = None
        
        # Initialize auth status
        self.auth_status = AuthStatus(
            auth_mode=auth_mode,
            client_scopes=client_scopes,
            user_scopes=user_scopes
        )
    
    async def initialize(self) -> None:
        """Initialize the authentication manager."""
        await self.token_manager.load_tokens()

        # Check for injected tokens from credential management system
        await self._check_injected_tokens()

        await self._update_auth_status()
    
    async def _check_injected_tokens(self) -> None:
        """Check for tokens injected by credential management system."""
        import os

        # Check for client credentials tokens
        client_access_token = os.getenv("NINJARMM_CLIENT_ACCESS_TOKEN")
        client_refresh_token = os.getenv("NINJARMM_CLIENT_REFRESH_TOKEN")
        client_expires_in = os.getenv("NINJARMM_CLIENT_EXPIRES_IN")

        if client_access_token:
            expires_in = int(client_expires_in) if client_expires_in else 3600
            await self.inject_client_token(
                access_token=client_access_token,
                refresh_token=client_refresh_token,
                expires_in=expires_in,
                scope=self.client_scopes
            )
            logger.info("Injected client credentials token from environment")

        # Check for user authorization tokens
        user_access_token = os.getenv("NINJARMM_USER_ACCESS_TOKEN")
        user_refresh_token = os.getenv("NINJARMM_USER_REFRESH_TOKEN")
        user_expires_in = os.getenv("NINJARMM_USER_EXPIRES_IN")

        if user_access_token:
            expires_in = int(user_expires_in) if user_expires_in else 3600
            await self.inject_user_token(
                access_token=user_access_token,
                refresh_token=user_refresh_token,
                expires_in=expires_in,
                scope=self.user_scopes
            )
            logger.info("Injected user authorization token from environment")

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
        if not self.has_machine_credentials:
            # No machine credentials available - must use injected user tokens
            if not self.auth_status.tokens["user"].is_valid():
                raise Exception("No valid authentication available. Machine credentials not configured and no user tokens injected.")
            # Skip authentication flow since we rely on injected tokens
            return self.auth_status.tokens["user"].access_token
        elif self.auth_mode == "client" or (
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
        if not self.has_machine_credentials or not self.oauth_client:
            raise Exception("Client credentials authentication not available - no machine credentials configured")

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
        if not self.has_machine_credentials or not self.oauth_client:
            raise Exception("User authorization flow not available - no machine credentials configured for OAuth flow")

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
        if not self.has_machine_credentials or not self.oauth_client:
            raise Exception("Token refresh not available - no machine credentials configured for OAuth flow")

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

    async def inject_client_token(self, access_token: str, refresh_token: Optional[str] = None,
                                 expires_in: int = 3600, scope: Optional[str] = None) -> None:
        """
        Inject a client credentials token from external credential management system.

        Args:
            access_token: The access token
            refresh_token: Optional refresh token
            expires_in: Token expiration time in seconds
            scope: Token scope
        """
        await self.token_manager.set_token(
            token_type="client",
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
            scope=scope or self.client_scopes
        )
        logger.info("Injected client credentials token")

    async def inject_user_token(self, access_token: str, refresh_token: Optional[str] = None,
                               expires_in: int = 3600, scope: Optional[str] = None) -> None:
        """
        Inject a user authorization token from external credential management system.

        Args:
            access_token: The access token
            refresh_token: Optional refresh token
            expires_in: Token expiration time in seconds
            scope: Token scope
        """
        await self.token_manager.set_token(
            token_type="user",
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
            scope=scope or self.user_scopes
        )
        logger.info("Injected user authorization token")

    async def inject_tokens_from_dict(self, tokens_data: Dict[str, Dict[str, Any]]) -> None:
        """
        Inject tokens from a dictionary (useful for credential management systems).

        Args:
            tokens_data: Dictionary with token data in format:
                {
                    "client": {
                        "access_token": "...",
                        "refresh_token": "...",
                        "expires_in": 3600,
                        "scope": "..."
                    },
                    "user": {
                        "access_token": "...",
                        "refresh_token": "...",
                        "expires_in": 3600,
                        "scope": "..."
                    }
                }
        """
        if "client" in tokens_data:
            client_data = tokens_data["client"]
            await self.inject_client_token(
                access_token=client_data["access_token"],
                refresh_token=client_data.get("refresh_token"),
                expires_in=client_data.get("expires_in", 3600),
                scope=client_data.get("scope")
            )

        if "user" in tokens_data:
            user_data = tokens_data["user"]
            await self.inject_user_token(
                access_token=user_data["access_token"],
                refresh_token=user_data.get("refresh_token"),
                expires_in=user_data.get("expires_in", 3600),
                scope=user_data.get("scope")
            )

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
