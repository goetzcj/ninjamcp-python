#!/usr/bin/env python3
"""
Example: NinjaRMM MCP Server with Credential Management System Integration

This example demonstrates how to integrate the NinjaRMM MCP Server with an
external credential management system that provides pre-obtained OAuth2 tokens.
"""

import asyncio
import os
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockCredentialManagementSystem:
    """
    Mock credential management system for demonstration.
    
    In a real implementation, this would be your actual credential management
    system (e.g., HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, etc.)
    """
    
    def __init__(self):
        # In a real system, these would come from secure storage
        self.stored_tokens = {
            "ninjarmm_client": {
                "access_token": "mock_client_access_token_here",
                "refresh_token": "mock_client_refresh_token_here",
                "expires_in": 3600,
                "scope": "monitoring management control"
            },
            "ninjarmm_user": {
                "access_token": "mock_user_access_token_here", 
                "refresh_token": "mock_user_refresh_token_here",
                "expires_in": 3600,
                "scope": "monitoring management control"
            }
        }
    
    async def get_ninjarmm_tokens(self) -> Dict[str, Dict[str, Any]]:
        """
        Retrieve NinjaRMM tokens from the credential management system.
        
        Returns:
            Dictionary with client and user tokens
        """
        logger.info("Retrieving NinjaRMM tokens from credential management system")
        
        # Simulate async credential retrieval
        await asyncio.sleep(0.1)
        
        return {
            "client": self.stored_tokens["ninjarmm_client"],
            "user": self.stored_tokens["ninjarmm_user"]
        }
    
    async def refresh_token(self, token_type: str, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh a token using the credential management system.
        
        Args:
            token_type: "client" or "user"
            refresh_token: The refresh token
            
        Returns:
            New token data
        """
        logger.info(f"Refreshing {token_type} token via credential management system")
        
        # In a real system, this would make an OAuth2 refresh request
        await asyncio.sleep(0.1)
        
        # Return mock refreshed token
        return {
            "access_token": f"refreshed_{token_type}_access_token",
            "refresh_token": f"refreshed_{token_type}_refresh_token", 
            "expires_in": 3600,
            "scope": "monitoring management control"
        }


async def run_with_credential_management():
    """Run the MCP server with credential management system integration."""
    
    # Initialize credential management system
    credential_system = MockCredentialManagementSystem()
    
    # Get tokens from credential management system
    tokens = await credential_system.get_ninjarmm_tokens()
    logger.info("Retrieved tokens from credential management system")
    
    # Import and initialize the MCP server
    try:
        from ninjarmm_mcp.server import NinjaRMMServer
        
        # Create and initialize server
        server = NinjaRMMServer()
        await server.initialize()
        
        # Inject tokens from credential management system
        await server.inject_tokens(tokens)
        logger.info("Tokens injected into MCP server")
        
        # Verify authentication status
        auth_status = await server.auth_manager.get_auth_status()
        logger.info(f"Authentication status: {auth_status.auth_mode}")
        logger.info(f"Client token valid: {auth_status.capabilities.can_use_client_credentials}")
        logger.info(f"User token valid: {auth_status.capabilities.can_use_user_auth}")
        
        # Run the server
        logger.info("Starting MCP server with injected credentials...")
        await server.run()
        
    except ImportError:
        logger.error("NinjaRMM MCP package not found. Please install it first.")
        logger.info("Run: pip install -e .")
    except Exception as e:
        logger.error(f"Error running server: {e}")
        raise


async def run_with_environment_variables():
    """Run the MCP server using environment variables for token injection."""
    
    # Set environment variables (normally these would be set by your deployment system)
    os.environ["NINJARMM_CLIENT_ACCESS_TOKEN"] = "env_client_access_token_here"
    os.environ["NINJARMM_CLIENT_REFRESH_TOKEN"] = "env_client_refresh_token_here"
    os.environ["NINJARMM_CLIENT_EXPIRES_IN"] = "3600"
    
    os.environ["NINJARMM_USER_ACCESS_TOKEN"] = "env_user_access_token_here"
    os.environ["NINJARMM_USER_REFRESH_TOKEN"] = "env_user_refresh_token_here"
    os.environ["NINJARMM_USER_EXPIRES_IN"] = "3600"
    
    logger.info("Set environment variables for token injection")
    
    try:
        from ninjarmm_mcp.server import NinjaRMMServer
        
        # Create and initialize server (will automatically detect env vars)
        server = NinjaRMMServer()
        await server.initialize()
        
        logger.info("Server initialized with environment variable tokens")
        
        # Verify authentication status
        auth_status = await server.auth_manager.get_auth_status()
        logger.info(f"Client token valid: {auth_status.capabilities.can_use_client_credentials}")
        logger.info(f"User token valid: {auth_status.capabilities.can_use_user_auth}")
        
        # Run the server
        logger.info("Starting MCP server with environment variable credentials...")
        await server.run()
        
    except ImportError:
        logger.error("NinjaRMM MCP package not found. Please install it first.")
        logger.info("Run: pip install -e .")
    except Exception as e:
        logger.error(f"Error running server: {e}")
        raise


async def main():
    """Main function to demonstrate different integration methods."""
    
    print("NinjaRMM MCP Server - Credential Management Integration Examples")
    print("=" * 70)
    print()
    print("Choose an integration method:")
    print("1. Programmatic token injection (recommended)")
    print("2. Environment variable injection")
    print("3. Exit")
    print()
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == "1":
        print("\nRunning with programmatic token injection...")
        await run_with_credential_management()
    elif choice == "2":
        print("\nRunning with environment variable injection...")
        await run_with_environment_variables()
    elif choice == "3":
        print("Exiting...")
        return
    else:
        print("Invalid choice. Please run again and select 1, 2, or 3.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise
