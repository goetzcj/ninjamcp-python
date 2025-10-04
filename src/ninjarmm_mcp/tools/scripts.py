"""Script execution tools for NinjaRMM MCP Server."""

from typing import Dict, Any, List
from mcp.types import TextContent

from .base import BaseTool


class GetAutomationScriptsTool(BaseTool):
    """Tool to get available automation scripts."""
    
    @property
    def name(self) -> str:
        return "get_automation_scripts"
    
    @property
    def description(self) -> str:
        return "Get available automation scripts with optional filtering"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "organization_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Filter by organization IDs"
                },
                "script_type": {
                    "type": "string",
                    "description": "Filter by script type (e.g., 'POWERSHELL', 'BATCH', 'BASH')"
                },
                "category": {
                    "type": "string",
                    "description": "Filter by script category"
                },
                "cursor": {
                    "type": "string",
                    "description": "Pagination cursor for next page"
                },
                "page_size": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 1000,
                    "default": 1000,
                    "description": "Number of scripts to return (max 1000)"
                }
            },
            "required": []
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute get automation scripts."""
        try:
            # Build query parameters
            params = {}
            
            if arguments.get("organization_ids"):
                params["organizationIds"] = ",".join(map(str, arguments["organization_ids"]))
            
            if arguments.get("script_type"):
                params["scriptType"] = arguments["script_type"]
            
            if arguments.get("category"):
                params["category"] = arguments["category"]
            
            if arguments.get("cursor"):
                params["cursor"] = arguments["cursor"]
            
            if arguments.get("page_size"):
                params["pageSize"] = arguments["page_size"]
            
            result = await self.client.get("/automation/scripts", "get_automation_scripts", params=params)
            
            return [TextContent(
                type="text",
                text=self.client._safe_json_stringify(result)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error getting automation scripts: {str(e)}"
            )]


class RunScriptTool(BaseTool):
    """Tool to execute automation scripts on devices."""
    
    @property
    def name(self) -> str:
        return "run_script"
    
    @property
    def description(self) -> str:
        return "Execute automation scripts on specified devices"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "script_id": {
                    "type": "integer",
                    "description": "The ID of the script to execute"
                },
                "device_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Device IDs to run the script on"
                },
                "parameters": {
                    "type": "object",
                    "description": "Script parameters as key-value pairs"
                },
                "run_as": {
                    "type": "string",
                    "description": "User context to run the script as (optional)"
                },
                "timeout": {
                    "type": "integer",
                    "minimum": 60,
                    "maximum": 3600,
                    "default": 300,
                    "description": "Script execution timeout in seconds (60-3600)"
                }
            },
            "required": ["script_id", "device_ids"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute run script."""
        try:
            script_id = arguments["script_id"]
            device_ids = arguments["device_ids"]
            parameters = arguments.get("parameters", {})
            run_as = arguments.get("run_as")
            timeout = arguments.get("timeout", 300)
            
            # Prepare request data
            data = {
                "scriptId": script_id,
                "deviceIds": device_ids,
                "timeout": timeout
            }
            
            if parameters:
                data["parameters"] = parameters
            
            if run_as:
                data["runAs"] = run_as
            
            result = await self.client.post("/automation/scripts/run", "run_script", data=data)
            
            return [TextContent(
                type="text",
                text=self.client._safe_json_stringify(result)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error running script: {str(e)}"
            )]


class ScriptTools:
    """Collection of script execution tools."""
    
    @staticmethod
    def get_tools(client) -> List[BaseTool]:
        """Get all script execution tools."""
        return [
            GetAutomationScriptsTool(client),
            RunScriptTool(client)
        ]
