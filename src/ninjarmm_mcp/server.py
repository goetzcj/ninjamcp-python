"""Main MCP server implementation for NinjaRMM."""

import asyncio
import logging
import os
from typing import Any, Sequence
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    JSONRPCError,
    INTERNAL_ERROR,
    METHOD_NOT_FOUND,
)

from .auth import AuthenticationManager
from .client import NinjaRMMClient
from .tools import (
    ToolRegistry,
    DeviceTools,
    ActivityTools,
    AlertTools,
    BackupTools,
    ScriptTools,
    TicketTools,
    CountTools,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NinjaRMMServer:
    """Main NinjaRMM MCP Server implementation."""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Configuration from environment
        self.base_url = os.getenv("NINJARMM_BASE_URL", "https://app.ninjarmm.com")
        self.client_id = os.getenv("NINJARMM_CLIENT_ID")
        self.client_secret = os.getenv("NINJARMM_CLIENT_SECRET")
        self.auth_mode = os.getenv("NINJARMM_AUTH_MODE", "hybrid")
        self.client_scopes = os.getenv("NINJARMM_CLIENT_SCOPES", "monitoring management control")
        self.user_scopes = os.getenv("NINJARMM_USER_SCOPES", "monitoring management control")
        self.user_redirect_port = int(os.getenv("NINJARMM_USER_REDIRECT_PORT", "8090"))
        self.token_storage_path = os.getenv("NINJARMM_TOKEN_STORAGE_PATH", "./tokens.json")
        
        # Validate required configuration
        if not self.client_id or not self.client_secret:
            raise ValueError("NINJARMM_CLIENT_ID and NINJARMM_CLIENT_SECRET must be set")
        
        # Initialize components
        self.auth_manager = AuthenticationManager(
            base_url=self.base_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
            auth_mode=self.auth_mode,
            client_scopes=self.client_scopes,
            user_scopes=self.user_scopes,
            user_redirect_port=self.user_redirect_port,
            token_storage_path=self.token_storage_path
        )
        
        self.client = NinjaRMMClient(self.auth_manager)
        self.tool_registry = ToolRegistry()
        self.server = Server("ninjarmm-mcp-server")
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self) -> None:
        """Register MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """Handle list tools request."""
            return self.tool_registry.list_tools()
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
            """Handle call tool request."""
            if not arguments:
                arguments = {}
            
            handler = self.tool_registry.get_handler(name)
            if not handler:
                raise JSONRPCError(METHOD_NOT_FOUND, f"Tool '{name}' not found")

            try:
                return await handler(arguments)
            except Exception as e:
                logger.error(f"Error executing tool '{name}': {e}")
                raise JSONRPCError(INTERNAL_ERROR, f"Tool execution failed: {e}")
    
    async def _register_tools(self) -> None:
        """Register all available tools."""
        try:
            # Register device management tools
            device_tools = DeviceTools.get_tools(self.client)
            self.tool_registry.register_multiple(device_tools)
            
            # Register activity monitoring tools
            activity_tools = ActivityTools.get_tools(self.client)
            self.tool_registry.register_multiple(activity_tools)
            
            # Register alert management tools
            alert_tools = AlertTools.get_tools(self.client)
            self.tool_registry.register_multiple(alert_tools)
            
            # Register backup tools
            backup_tools = BackupTools.get_tools(self.client)
            self.tool_registry.register_multiple(backup_tools)
            
            # Register script tools
            script_tools = ScriptTools.get_tools(self.client)
            self.tool_registry.register_multiple(script_tools)
            
            # Register ticket tools
            ticket_tools = TicketTools.get_tools(self.client)
            self.tool_registry.register_multiple(ticket_tools)

            # Register counting tools
            count_tools = CountTools.get_tools(self.client)
            self.tool_registry.register_multiple(count_tools)

            # Register authentication management tools
            await self._register_auth_tools()
            
            logger.info(f"Registered {len(self.tool_registry.get_tool_names())} tools")
            
        except Exception as e:
            logger.error(f"Failed to register tools: {e}")
            raise
    
    async def _register_auth_tools(self) -> None:
        """Register authentication management tools."""
        from .tools.base import BaseTool
        from mcp.types import TextContent
        
        class GetAuthStatusTool(BaseTool):
            def __init__(self, auth_manager):
                self.auth_manager = auth_manager
            
            @property
            def name(self) -> str:
                return "get_auth_status"
            
            @property
            def description(self) -> str:
                return "Check current authentication status and capabilities"
            
            @property
            def input_schema(self) -> dict[str, Any]:
                return {"type": "object", "properties": {}, "required": []}
            
            async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
                try:
                    status = await self.auth_manager.get_auth_status()
                    return [TextContent(
                        type="text",
                        text=status.model_dump_json(indent=2)
                    )]
                except Exception as e:
                    return [TextContent(
                        type="text",
                        text=f"Error getting auth status: {str(e)}"
                    )]
        
        class ReauthorizeUserTool(BaseTool):
            def __init__(self, auth_manager):
                self.auth_manager = auth_manager
            
            @property
            def name(self) -> str:
                return "reauthorize_user"
            
            @property
            def description(self) -> str:
                return "Re-authenticate user for ticket operations"
            
            @property
            def input_schema(self) -> dict[str, Any]:
                return {"type": "object", "properties": {}, "required": []}
            
            async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
                try:
                    await self.auth_manager.reauthorize_user()
                    return [TextContent(
                        type="text",
                        text="User re-authorization completed successfully"
                    )]
                except Exception as e:
                    return [TextContent(
                        type="text",
                        text=f"Error re-authorizing user: {str(e)}"
                    )]
        
        class ClearTokensTool(BaseTool):
            def __init__(self, auth_manager):
                self.auth_manager = auth_manager
            
            @property
            def name(self) -> str:
                return "clear_tokens"
            
            @property
            def description(self) -> str:
                return "Clear stored authentication tokens"
            
            @property
            def input_schema(self) -> dict[str, Any]:
                return {
                    "type": "object",
                    "properties": {
                        "token_type": {
                            "type": "string",
                            "enum": ["all", "client", "user"],
                            "default": "all",
                            "description": "Type of tokens to clear"
                        }
                    },
                    "required": []
                }
            
            async def execute(self, arguments: dict[str, Any]) -> list[TextContent]:
                try:
                    token_type = arguments.get("token_type", "all")
                    await self.auth_manager.clear_tokens(token_type)
                    return [TextContent(
                        type="text",
                        text=f"Cleared {token_type} tokens successfully"
                    )]
                except Exception as e:
                    return [TextContent(
                        type="text",
                        text=f"Error clearing tokens: {str(e)}"
                    )]
        
        # Register auth tools
        auth_tools = [
            GetAuthStatusTool(self.auth_manager),
            ReauthorizeUserTool(self.auth_manager),
            ClearTokensTool(self.auth_manager)
        ]
        
        self.tool_registry.register_multiple(auth_tools)
    
    async def initialize(self) -> None:
        """Initialize the server."""
        try:
            logger.info("Initializing NinjaRMM MCP Server...")
            
            # Initialize authentication
            await self.auth_manager.initialize()
            
            # Register all tools
            await self._register_tools()
            
            logger.info("NinjaRMM MCP Server initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize server: {e}")
            raise
    
    async def run(self) -> None:
        """Run the MCP server."""
        try:
            await self.initialize()
            
            # Run the server
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="ninjarmm-mcp-server",
                        server_version="1.3.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=None,
                            experimental_capabilities=None,
                        ),
                    ),
                )
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise


async def main() -> None:
    """Main entry point."""
    server = NinjaRMMServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
