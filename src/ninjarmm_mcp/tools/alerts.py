"""Alert management tools for NinjaRMM MCP Server."""

from typing import Dict, Any, List
from mcp.types import TextContent

from .base import BaseTool


class GetAlertsTool(BaseTool):
    """Tool to get alerts with optional filtering."""
    
    @property
    def name(self) -> str:
        return "get_alerts"
    
    @property
    def description(self) -> str:
        return "Retrieve alerts with optional filtering by device, organization, type, status, and severity"
    
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
                "alert_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by alert types"
                },
                "status": {
                    "type": "string",
                    "description": "Filter by status (e.g., 'OPEN', 'ACKNOWLEDGED', 'RESOLVED')"
                },
                "severity": {
                    "type": "string",
                    "description": "Filter by severity (e.g., 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL')"
                },
                "since": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Get alerts since this timestamp (ISO format)"
                },
                "until": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Get alerts until this timestamp (ISO format)"
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
                    "description": "Number of alerts to return (max 1000)"
                }
            },
            "required": []
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute get alerts."""
        try:
            # Build query parameters
            params = {}
            
            if arguments.get("device_ids"):
                params["deviceIds"] = ",".join(map(str, arguments["device_ids"]))
            
            if arguments.get("organization_ids"):
                params["organizationIds"] = ",".join(map(str, arguments["organization_ids"]))
            
            if arguments.get("alert_types"):
                params["alertTypes"] = ",".join(arguments["alert_types"])
            
            if arguments.get("status"):
                params["status"] = arguments["status"]
            
            if arguments.get("severity"):
                params["severity"] = arguments["severity"]
            
            if arguments.get("since"):
                params["since"] = arguments["since"]
            
            if arguments.get("until"):
                params["until"] = arguments["until"]
            
            if arguments.get("cursor"):
                params["cursor"] = arguments["cursor"]
            
            if arguments.get("page_size"):
                params["pageSize"] = arguments["page_size"]
            
            result = await self.client.get("/alerts", "get_alerts", params=params)
            
            return [TextContent(
                type="text",
                text=self.client._safe_json_stringify(result)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error getting alerts: {str(e)}"
            )]


class ResetAlertTool(BaseTool):
    """Tool to reset/acknowledge specific alerts."""
    
    @property
    def name(self) -> str:
        return "reset_alert"
    
    @property
    def description(self) -> str:
        return "Reset or acknowledge a specific alert by ID"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "alert_id": {
                    "type": "integer",
                    "description": "The ID of the alert to reset/acknowledge"
                },
                "action": {
                    "type": "string",
                    "enum": ["acknowledge", "reset", "resolve"],
                    "default": "acknowledge",
                    "description": "Action to perform on the alert"
                },
                "note": {
                    "type": "string",
                    "description": "Optional note to add when resetting the alert"
                }
            },
            "required": ["alert_id"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute reset alert."""
        try:
            alert_id = arguments["alert_id"]
            action = arguments.get("action", "acknowledge")
            note = arguments.get("note")
            
            # Prepare request data
            data = {"action": action}
            if note:
                data["note"] = note
            
            result = await self.client.post(f"/alerts/{alert_id}/reset", "reset_alert", data=data)
            
            return [TextContent(
                type="text",
                text=self.client._safe_json_stringify(result)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error resetting alert: {str(e)}"
            )]


class GetDeviceAlertsTool(BaseTool):
    """Tool to get alerts for a specific device."""

    @property
    def name(self) -> str:
        return "get_device_alerts"

    @property
    def description(self) -> str:
        return "Retrieve active alerts (triggered conditions) for a specific device"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "integer",
                    "description": "Device identifier"
                },
                "lang": {
                    "type": "string",
                    "description": "Language tag (optional)"
                },
                "tz": {
                    "type": "string",
                    "description": "Time Zone (optional)"
                }
            },
            "required": ["device_id"]
        }

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute get device alerts."""
        try:
            device_id = arguments["device_id"]

            # Build query parameters
            params = {}
            if arguments.get("lang"):
                params["lang"] = arguments["lang"]
            if arguments.get("tz"):
                params["tz"] = arguments["tz"]

            result = await self.client.get(f"/device/{device_id}/alerts", "get_device_alerts", params=params)

            return [TextContent(
                type="text",
                text=self.client._safe_json_stringify(result)
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error getting device alerts: {str(e)}"
            )]


class AlertTools:
    """Collection of alert management tools."""

    @staticmethod
    def get_tools(client) -> List[BaseTool]:
        """Get all alert management tools."""
        return [
            GetAlertsTool(client),
            ResetAlertTool(client),
            GetDeviceAlertsTool(client)
        ]
