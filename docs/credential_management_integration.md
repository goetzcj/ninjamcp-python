# Credential Management System Integration

This guide explains how to integrate the NinjaRMM MCP Server with external credential management systems that handle OAuth2 authentication.

## Overview

Instead of the MCP server performing its own OAuth2 authentication flow (which opens a browser for user login), you can use an external credential management system to:

1. Handle the OAuth2 authentication with NinjaRMM
2. Obtain access and refresh tokens
3. Pass those tokens to the MCP server
4. Let the MCP server use the pre-obtained tokens

## Integration Methods

### Method 1: Environment Variables

Set the following environment variables with tokens from your credential management system:

```bash
# Client Credentials Flow tokens
export NINJARMM_CLIENT_ACCESS_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
export NINJARMM_CLIENT_REFRESH_TOKEN="def50200..."  # optional
export NINJARMM_CLIENT_EXPIRES_IN="3600"  # optional, defaults to 3600

# User Authorization Flow tokens  
export NINJARMM_USER_ACCESS_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9..."
export NINJARMM_USER_REFRESH_TOKEN="def50200..."  # optional
export NINJARMM_USER_EXPIRES_IN="3600"  # optional, defaults to 3600
```

The server will automatically detect and use these tokens during initialization.

### Method 2: Programmatic Injection

```python
import asyncio
from ninjarmm_mcp.server import NinjaRMMServer

async def main():
    # Initialize the server
    server = NinjaRMMServer()
    await server.initialize()
    
    # Get tokens from your credential management system
    tokens_from_credential_system = {
        "client": {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
            "refresh_token": "def50200...",  # optional
            "expires_in": 3600,  # optional
            "scope": "monitoring management control"  # optional
        },
        "user": {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
            "refresh_token": "def50200...",  # optional
            "expires_in": 3600,  # optional
            "scope": "monitoring management control"  # optional
        }
    }
    
    # Inject the tokens
    await server.inject_tokens(tokens_from_credential_system)
    
    # Run the server
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### Method 3: Direct Token Manager Access

For more granular control:

```python
import asyncio
from ninjarmm_mcp.server import NinjaRMMServer

async def main():
    server = NinjaRMMServer()
    await server.initialize()
    
    # Inject client credentials token
    await server.auth_manager.inject_client_token(
        access_token="client_access_token_here",
        refresh_token="client_refresh_token_here",  # optional
        expires_in=3600,
        scope="monitoring management control"
    )
    
    # Inject user authorization token
    await server.auth_manager.inject_user_token(
        access_token="user_access_token_here", 
        refresh_token="user_refresh_token_here",  # optional
        expires_in=3600,
        scope="monitoring management control"
    )
    
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
```

## Token Storage Format

Tokens are stored in `tokens.json` with this structure:

```json
{
  "client": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
    "refresh_token": "def50200...",
    "expires_at": "2025-10-04T15:30:00.123456",
    "scope": "monitoring management control",
    "token_type": "Bearer",
    "valid": true
  },
  "user": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
    "refresh_token": "def50200...",
    "expires_at": "2025-10-04T15:30:00.123456",
    "scope": "monitoring management control", 
    "token_type": "Bearer",
    "valid": true
  }
}
```

## Token Types

### Client Credentials Token
- Used for most operations (devices, activities, alerts, etc.)
- Obtained via OAuth2 Client Credentials flow
- Requires `client_id` and `client_secret`

### User Authorization Token  
- Required for ticket operations
- Obtained via OAuth2 Authorization Code flow with PKCE
- Requires user consent and login

## Credential Management System Requirements

Your credential management system should:

1. **Handle OAuth2 flows** with NinjaRMM's endpoints:
   - Authorization: `https://app.ninjarmm.com/oauth/authorize`
   - Token: `https://app.ninjarmm.com/oauth/token`

2. **Support both flows**:
   - Client Credentials for general operations
   - Authorization Code + PKCE for user operations

3. **Provide token refresh** capability using refresh tokens

4. **Securely store** and manage tokens

## Benefits

- **Centralized Authentication**: All OAuth2 flows handled by your credential management system
- **Security**: No browser-based authentication in production environments
- **Scalability**: Easier to manage credentials across multiple instances
- **Compliance**: Better audit trails and credential rotation policies
- **Flexibility**: Works with any credential management system

## Backward Compatibility

This integration is fully backward compatible. If no tokens are injected:
- The server will perform its own OAuth2 authentication flows
- Browser-based user authentication will be used when needed
- All existing functionality remains unchanged

## Error Handling

The server will:
- Validate injected tokens before use
- Attempt token refresh if tokens are expired and refresh tokens are available
- Fall back to OAuth2 flows if injected tokens are invalid and no refresh is possible
- Log all authentication events for debugging

## Security Considerations

- **Never log access tokens** - they are sensitive credentials
- **Use HTTPS** for all token transmission
- **Implement token rotation** in your credential management system
- **Monitor token usage** for suspicious activity
- **Use least privilege scopes** for each token type
