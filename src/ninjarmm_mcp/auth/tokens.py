"""Token management for NinjaRMM authentication."""

import json
import aiofiles
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
import logging

from ..models.auth import TokenInfo

logger = logging.getLogger(__name__)


class TokenManager:
    """Manages OAuth2 tokens with persistent storage."""
    
    def __init__(self, storage_path: str = "./tokens.json"):
        self.storage_path = Path(storage_path)
        self._tokens: Dict[str, TokenInfo] = {
            "client": TokenInfo(),
            "user": TokenInfo()
        }
    
    async def load_tokens(self) -> None:
        """Load tokens from storage."""
        if not self.storage_path.exists():
            logger.info("No token storage file found, starting with empty tokens")
            return
        
        try:
            async with aiofiles.open(self.storage_path, 'r') as f:
                content = await f.read()
                data = json.loads(content)
            
            for token_type, token_data in data.items():
                if token_type in self._tokens:
                    # Convert expires_at string back to datetime
                    if token_data.get("expires_at"):
                        token_data["expires_at"] = datetime.fromisoformat(token_data["expires_at"])
                    
                    self._tokens[token_type] = TokenInfo(**token_data)
            
            logger.info("Loaded tokens from storage")
            
        except Exception as e:
            logger.error(f"Failed to load tokens: {e}")
    
    async def save_tokens(self) -> None:
        """Save tokens to storage."""
        try:
            # Prepare data for JSON serialization
            data = {}
            for token_type, token_info in self._tokens.items():
                token_dict = token_info.model_dump()
                # Convert datetime to string for JSON serialization
                if token_dict.get("expires_at"):
                    token_dict["expires_at"] = token_dict["expires_at"].isoformat()
                data[token_type] = token_dict
            
            # Ensure directory exists
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(self.storage_path, 'w') as f:
                await f.write(json.dumps(data, indent=2))
            
            logger.info("Saved tokens to storage")
            
        except Exception as e:
            logger.error(f"Failed to save tokens: {e}")
    
    def get_token(self, token_type: str) -> TokenInfo:
        """Get a token by type."""
        return self._tokens.get(token_type, TokenInfo())
    
    async def set_token(self, token_type: str, access_token: str, expires_in: int, 
                       refresh_token: Optional[str] = None, scope: Optional[str] = None) -> None:
        """Set a token with expiration."""
        expires_at = datetime.now() + timedelta(seconds=int(expires_in * 0.9))  # 90% of actual expiry
        
        self._tokens[token_type] = TokenInfo(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            scope=scope,
            valid=True
        )
        
        await self.save_tokens()
        logger.info(f"Set {token_type} token, expires at {expires_at}")
    
    async def clear_token(self, token_type: str) -> None:
        """Clear a specific token."""
        self._tokens[token_type] = TokenInfo()
        await self.save_tokens()
        logger.info(f"Cleared {token_type} token")
    
    async def clear_all_tokens(self) -> None:
        """Clear all tokens."""
        self._tokens = {
            "client": TokenInfo(),
            "user": TokenInfo()
        }
        await self.save_tokens()
        logger.info("Cleared all tokens")
    
    def get_all_tokens(self) -> Dict[str, TokenInfo]:
        """Get all tokens."""
        return self._tokens.copy()
    
    def is_token_valid(self, token_type: str) -> bool:
        """Check if a token is valid and not expired."""
        token = self.get_token(token_type)
        return token.is_valid()
