"""Base tool classes and registry for NinjaRMM MCP Server."""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, Awaitable
from mcp.types import Tool, TextContent

from ..client import NinjaRMMClient

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """Base class for all NinjaRMM MCP tools."""
    
    def __init__(self, client: NinjaRMMClient):
        self.client = client
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass
    
    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """JSON schema for tool input parameters."""
        pass
    
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute the tool with given arguments."""
        pass
    
    def to_tool(self) -> Tool:
        """Convert to MCP Tool object."""
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema=self.input_schema
        )


class ToolRegistry:
    """Registry for managing MCP tools."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._handlers: Dict[str, Callable[[Dict[str, Any]], Awaitable[List[TextContent]]]] = {}
    
    def register(self, tool: BaseTool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool
        self._handlers[tool.name] = tool.execute
        logger.info(f"Registered tool: {tool.name}")
    
    def register_multiple(self, tools: List[BaseTool]) -> None:
        """Register multiple tools."""
        for tool in tools:
            self.register(tool)
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def get_handler(self, name: str) -> Optional[Callable[[Dict[str, Any]], Awaitable[List[TextContent]]]]:
        """Get a tool handler by name."""
        return self._handlers.get(name)
    
    def list_tools(self) -> List[Tool]:
        """Get list of all registered tools."""
        return [tool.to_tool() for tool in self._tools.values()]
    
    def get_tool_names(self) -> List[str]:
        """Get list of all tool names."""
        return list(self._tools.keys())
    
    def has_tool(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools
    
    def unregister(self, name: str) -> bool:
        """Unregister a tool."""
        if name in self._tools:
            del self._tools[name]
            del self._handlers[name]
            logger.info(f"Unregistered tool: {name}")
            return True
        return False
    
    def clear(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()
        self._handlers.clear()
        logger.info("Cleared all tools from registry")
