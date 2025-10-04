"""Authentication data models."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class TokenInfo(BaseModel):
    """Information about an authentication token."""
    
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    scope: Optional[str] = None
    token_type: str = "Bearer"
    valid: bool = False
    
    def is_expired(self) -> bool:
        """Check if the token is expired."""
        if not self.expires_at:
            return True
        return datetime.now() >= self.expires_at
    
    def is_valid(self) -> bool:
        """Check if the token is valid and not expired."""
        return self.valid and self.access_token and not self.is_expired()


class AuthCapabilities(BaseModel):
    """Authentication capabilities and features."""
    
    can_use_client_credentials: bool = False
    can_use_user_auth: bool = False
    supports_refresh: bool = False


class AuthStatus(BaseModel):
    """Current authentication status."""
    
    auth_mode: str = "hybrid"
    client_scopes: str = "monitoring management control"
    user_scopes: str = "monitoring management control"
    
    tokens: Dict[str, TokenInfo] = Field(default_factory=lambda: {
        "client": TokenInfo(),
        "user": TokenInfo()
    })
    
    capabilities: AuthCapabilities = Field(default_factory=AuthCapabilities)
    
    def update_capabilities(self) -> None:
        """Update capabilities based on current token status."""
        self.capabilities.can_use_client_credentials = self.tokens["client"].is_valid()
        self.capabilities.can_use_user_auth = self.tokens["user"].is_valid()
        self.capabilities.supports_refresh = bool(self.tokens["user"].refresh_token)
    
    def get_best_token(self, operation: Optional[str] = None) -> Optional[TokenInfo]:
        """Get the best available token for an operation."""
        # For ticket operations, prefer user token
        if operation and "ticket" in operation.lower():
            if self.tokens["user"].is_valid():
                return self.tokens["user"]
            return None
        
        # For other operations, prefer client token, fallback to user
        if self.tokens["client"].is_valid():
            return self.tokens["client"]
        elif self.tokens["user"].is_valid():
            return self.tokens["user"]
        
        return None
