"""Activity monitoring tools for NinjaRMM MCP Server."""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from mcp.types import TextContent

from .base import BaseTool


class GetActivitiesTool(BaseTool):
    """Tool to get activities/events."""
    
    @property
    def name(self) -> str:
        return "get_activities"
    
    @property
    def description(self) -> str:
        return "Retrieve activities/events with optional filtering by device, organization, type, and time range"
    
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
                "activity_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by activity types (e.g., 'SCRIPT_RUN', 'ALERT', 'MAINTENANCE')"
                },
                "status": {
                    "type": "string",
                    "description": "Filter by status (e.g., 'SUCCESS', 'FAILED', 'RUNNING')"
                },
                "since": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Get activities since this timestamp (ISO format)"
                },
                "until": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Get activities until this timestamp (ISO format)"
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
                    "description": "Number of activities to return (max 1000)"
                }
            },
            "required": []
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute get activities."""
        try:
            # Build query parameters
            params = {}
            
            if arguments.get("device_ids"):
                params["deviceIds"] = ",".join(map(str, arguments["device_ids"]))
            
            if arguments.get("organization_ids"):
                params["organizationIds"] = ",".join(map(str, arguments["organization_ids"]))
            
            if arguments.get("activity_types"):
                params["activityTypes"] = ",".join(arguments["activity_types"])
            
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
            
            result = await self.client.get("/activities", "get_activities", params=params)
            
            return [TextContent(
                type="text",
                text=self.client._safe_json_stringify(result)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error getting activities: {str(e)}"
            )]


class MonitorDeviceActivitiesTool(BaseTool):
    """Tool to monitor activities for specific devices with real-time capabilities."""
    
    @property
    def name(self) -> str:
        return "monitor_device_activities"
    
    @property
    def description(self) -> str:
        return "Monitor activities for specific devices with real-time polling capabilities"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "device_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Device IDs to monitor"
                },
                "activity_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Activity types to monitor (optional)"
                },
                "poll_interval": {
                    "type": "integer",
                    "minimum": 5,
                    "maximum": 300,
                    "default": 30,
                    "description": "Polling interval in seconds (5-300)"
                },
                "duration": {
                    "type": "integer",
                    "minimum": 30,
                    "maximum": 3600,
                    "default": 300,
                    "description": "Monitoring duration in seconds (30-3600)"
                }
            },
            "required": ["device_ids"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute monitor device activities."""
        try:
            device_ids = arguments["device_ids"]
            activity_types = arguments.get("activity_types")
            poll_interval = arguments.get("poll_interval", 30)
            duration = arguments.get("duration", 300)
            
            activities = []
            start_time = datetime.now()
            end_time = start_time + timedelta(seconds=duration)
            last_check = start_time
            
            while datetime.now() < end_time:
                # Build query parameters
                params = {
                    "deviceIds": ",".join(map(str, device_ids)),
                    "since": last_check.isoformat(),
                    "pageSize": 1000
                }
                
                if activity_types:
                    params["activityTypes"] = ",".join(activity_types)
                
                try:
                    result = await self.client.get("/activities", "monitor_device_activities", params=params)
                    
                    # Extract activities from result
                    new_activities = []
                    if isinstance(result, list):
                        new_activities = result
                    elif isinstance(result, dict):
                        new_activities = result.get("data", result.get("activities", []))
                    
                    if new_activities:
                        activities.extend(new_activities)
                    
                    last_check = datetime.now()
                    
                except Exception as e:
                    # Log error but continue monitoring
                    activities.append({
                        "error": f"Polling error at {datetime.now().isoformat()}: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Wait for next poll
                await asyncio.sleep(poll_interval)
            
            result = {
                "monitoring_summary": {
                    "device_ids": device_ids,
                    "start_time": start_time.isoformat(),
                    "end_time": datetime.now().isoformat(),
                    "duration_seconds": (datetime.now() - start_time).total_seconds(),
                    "poll_interval": poll_interval,
                    "total_activities": len(activities)
                },
                "activities": activities
            }
            
            return [TextContent(
                type="text",
                text=self.client._safe_json_stringify(result)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error monitoring device activities: {str(e)}"
            )]


class TrackScriptExecutionTool(BaseTool):
    """Tool to track script execution outcomes with detailed monitoring."""
    
    @property
    def name(self) -> str:
        return "track_script_execution"
    
    @property
    def description(self) -> str:
        return "Track script execution outcomes with detailed monitoring and status updates"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "execution_id": {
                    "type": "string",
                    "description": "Script execution ID to track"
                },
                "device_id": {
                    "type": "integer",
                    "description": "Device ID where script is running (optional, for additional context)"
                },
                "poll_interval": {
                    "type": "integer",
                    "minimum": 5,
                    "maximum": 60,
                    "default": 10,
                    "description": "Polling interval in seconds (5-60)"
                },
                "timeout": {
                    "type": "integer",
                    "minimum": 60,
                    "maximum": 3600,
                    "default": 600,
                    "description": "Maximum time to wait for completion in seconds (60-3600)"
                }
            },
            "required": ["execution_id"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute track script execution."""
        try:
            execution_id = arguments["execution_id"]
            device_id = arguments.get("device_id")
            poll_interval = arguments.get("poll_interval", 10)
            timeout = arguments.get("timeout", 600)
            
            start_time = datetime.now()
            end_time = start_time + timedelta(seconds=timeout)
            execution_history = []
            
            while datetime.now() < end_time:
                try:
                    # Check script execution status
                    params = {"executionId": execution_id}
                    if device_id:
                        params["deviceId"] = device_id
                    
                    result = await self.client.get("/script-executions", "track_script_execution", params=params)
                    
                    # Record the status check
                    status_check = {
                        "timestamp": datetime.now().isoformat(),
                        "status": result
                    }
                    execution_history.append(status_check)
                    
                    # Check if execution is complete
                    if isinstance(result, dict):
                        status = result.get("status", "").upper()
                        if status in ["COMPLETED", "SUCCESS", "FAILED", "ERROR", "CANCELLED"]:
                            break
                    elif isinstance(result, list) and result:
                        # If result is a list, check the first item
                        first_result = result[0]
                        if isinstance(first_result, dict):
                            status = first_result.get("status", "").upper()
                            if status in ["COMPLETED", "SUCCESS", "FAILED", "ERROR", "CANCELLED"]:
                                break
                    
                except Exception as e:
                    execution_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "error": f"Polling error: {str(e)}"
                    })
                
                await asyncio.sleep(poll_interval)
            
            final_result = {
                "tracking_summary": {
                    "execution_id": execution_id,
                    "device_id": device_id,
                    "start_time": start_time.isoformat(),
                    "end_time": datetime.now().isoformat(),
                    "duration_seconds": (datetime.now() - start_time).total_seconds(),
                    "poll_interval": poll_interval,
                    "timeout": timeout,
                    "status_checks": len(execution_history)
                },
                "execution_history": execution_history
            }
            
            return [TextContent(
                type="text",
                text=self.client._safe_json_stringify(final_result)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error tracking script execution: {str(e)}"
            )]


class WaitForActivityOutcomeTool(BaseTool):
    """Tool to wait for and monitor action outcomes with polling."""

    @property
    def name(self) -> str:
        return "wait_for_activity_outcome"

    @property
    def description(self) -> str:
        return "Wait for and monitor action outcomes with polling until completion or timeout"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "activity_id": {
                    "type": "string",
                    "description": "Activity ID to monitor"
                },
                "device_id": {
                    "type": "integer",
                    "description": "Device ID for the activity (optional)"
                },
                "expected_status": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["COMPLETED", "SUCCESS", "FAILED", "ERROR"],
                    "description": "Expected completion statuses to wait for"
                },
                "poll_interval": {
                    "type": "integer",
                    "minimum": 5,
                    "maximum": 60,
                    "default": 15,
                    "description": "Polling interval in seconds (5-60)"
                },
                "timeout": {
                    "type": "integer",
                    "minimum": 60,
                    "maximum": 3600,
                    "default": 900,
                    "description": "Maximum time to wait in seconds (60-3600)"
                }
            },
            "required": ["activity_id"]
        }

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute wait for activity outcome."""
        try:
            activity_id = arguments["activity_id"]
            device_id = arguments.get("device_id")
            expected_status = arguments.get("expected_status", ["COMPLETED", "SUCCESS", "FAILED", "ERROR"])
            poll_interval = arguments.get("poll_interval", 15)
            timeout = arguments.get("timeout", 900)

            start_time = datetime.now()
            end_time = start_time + timedelta(seconds=timeout)
            status_history = []

            while datetime.now() < end_time:
                try:
                    # Check activity status
                    params = {"activityId": activity_id}
                    if device_id:
                        params["deviceId"] = device_id

                    result = await self.client.get("/activities", "wait_for_activity_outcome", params=params)

                    # Record the status check
                    status_check = {
                        "timestamp": datetime.now().isoformat(),
                        "result": result
                    }
                    status_history.append(status_check)

                    # Check if activity has reached expected status
                    current_status = None
                    if isinstance(result, dict):
                        current_status = result.get("status", "").upper()
                    elif isinstance(result, list) and result:
                        first_result = result[0]
                        if isinstance(first_result, dict):
                            current_status = first_result.get("status", "").upper()

                    if current_status and current_status in [s.upper() for s in expected_status]:
                        break

                except Exception as e:
                    status_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "error": f"Polling error: {str(e)}"
                    })

                await asyncio.sleep(poll_interval)

            final_result = {
                "outcome_summary": {
                    "activity_id": activity_id,
                    "device_id": device_id,
                    "expected_status": expected_status,
                    "start_time": start_time.isoformat(),
                    "end_time": datetime.now().isoformat(),
                    "duration_seconds": (datetime.now() - start_time).total_seconds(),
                    "poll_interval": poll_interval,
                    "timeout": timeout,
                    "status_checks": len(status_history),
                    "completed": len(status_history) > 0 and datetime.now() < end_time
                },
                "status_history": status_history
            }

            return [TextContent(
                type="text",
                text=self.client._safe_json_stringify(final_result)
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error waiting for activity outcome: {str(e)}"
            )]


class ActivityTools:
    """Collection of activity monitoring tools."""

    @staticmethod
    def get_tools(client) -> List[BaseTool]:
        """Get all activity monitoring tools."""
        return [
            GetActivitiesTool(client),
            MonitorDeviceActivitiesTool(client),
            TrackScriptExecutionTool(client),
            WaitForActivityOutcomeTool(client)
        ]
