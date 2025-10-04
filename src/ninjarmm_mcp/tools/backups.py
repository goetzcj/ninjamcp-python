"""Backup management tools for NinjaRMM MCP Server."""

from typing import Dict, Any, List
from mcp.types import TextContent

from .base import BaseTool


class GetBackupJobsTool(BaseTool):
    """Tool to get backup job information."""
    
    @property
    def name(self) -> str:
        return "get_backup_jobs"
    
    @property
    def description(self) -> str:
        return "Retrieve backup job information with optional filtering by device and organization"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "device_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Filter by device IDs"
                },
                "organization_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Filter by organization IDs"
                },
                "status": {
                    "type": "string",
                    "description": "Filter by backup status (e.g., 'SUCCESS', 'FAILED', 'RUNNING')"
                },
                "since": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Get backup jobs since this timestamp (ISO format)"
                },
                "until": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Get backup jobs until this timestamp (ISO format)"
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
                    "description": "Number of backup jobs to return (max 1000)"
                }
            },
            "required": []
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute get backup jobs."""
        try:
            # Build query parameters
            params = {}
            
            if arguments.get("device_ids"):
                params["deviceIds"] = ",".join(map(str, arguments["device_ids"]))
            
            if arguments.get("organization_ids"):
                params["organizationIds"] = ",".join(map(str, arguments["organization_ids"]))
            
            if arguments.get("status"):
                params["status"] = arguments["status"]
            
            if arguments.get("since"):
                params["since"] = arguments["since"]
            
            if arguments.get("until"):
                params["until"] = arguments["until"]
            
            if arguments.get("cursor"):
                params["cursor"] = arguments["cursor"]
            
            if arguments.get("page_size"):
                params["pageSize"] = arguments["page_size"]
            
            result = await self.client.get("/backup-jobs", "get_backup_jobs", params=params)
            
            return [TextContent(
                type="text",
                text=self.client._safe_json_stringify(result)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error getting backup jobs: {str(e)}"
            )]


class BackupTools:
    """Collection of backup management tools."""
    
    @staticmethod
    def get_tools(client) -> List[BaseTool]:
        """Get all backup management tools."""
        return [
            GetBackupJobsTool(client)
        ]
