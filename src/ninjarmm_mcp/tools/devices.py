"""Device management tools for NinjaRMM MCP Server."""

import json
from typing import Dict, Any, List, Optional
from mcp.types import TextContent

from .base import BaseTool
from ..models.device import Device, DeviceFilter
from ..utils.device_filter import DeviceFilterBuilder


class GetOrganizationsTool(BaseTool):
    """Tool to get all organizations."""
    
    @property
    def name(self) -> str:
        return "get_organizations"
    
    @property
    def description(self) -> str:
        return "Get all organizations with their IDs and names"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute get organizations."""
        try:
            result = await self.client.get("/organizations", "get_organizations")
            
            # Format the response
            if isinstance(result, list):
                organizations = result
            else:
                organizations = result.get("data", result)
            
            formatted_result = {
                "organizations": organizations,
                "count": len(organizations) if isinstance(organizations, list) else 0
            }
            
            return [TextContent(
                type="text",
                text=self.client._safe_json_stringify(formatted_result)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text", 
                text=f"Error getting organizations: {str(e)}"
            )]


class GetDevicesTool(BaseTool):
    """Tool to get basic device information."""
    
    @property
    def name(self) -> str:
        return "get_devices"
    
    @property
    def description(self) -> str:
        return """Get basic device information with advanced filtering capabilities.

        Supports comprehensive filtering including:
        - Organization, location, and role filtering (with inclusion/exclusion)
        - Device class filtering (WINDOWS_SERVER, MAC, LINUX_WORKSTATION, etc.)
        - Online/offline status filtering
        - Device approval status filtering
        - Creation date range filtering
        - Group membership filtering
        - Specific device ID filtering

        Examples:
        - Get all online Windows servers: online_status="online", device_classes=["WINDOWS_SERVER"]
        - Get devices created in 2024: created_after="2024-01-01", created_before="2024-12-31"
        - Get devices excluding specific orgs: exclude_organizations=[123, 456]
        """

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                # Legacy parameters (maintained for backward compatibility)
                "organization_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Filter by organization IDs (legacy parameter, use for backward compatibility)"
                },
                "device_filter": {
                    "type": "string",
                    "description": "Raw device filter string (advanced users). If provided, other filter parameters are ignored."
                },
                "node_class_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Filter by node class IDs (legacy parameter)"
                },
                "node_role_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Filter by node role IDs (legacy parameter)"
                },

                # Enhanced filtering parameters
                "online_status": {
                    "type": "string",
                    "enum": ["online", "offline"],
                    "description": "Filter by device online/offline status"
                },
                "approval_status": {
                    "type": "string",
                    "enum": ["PENDING", "APPROVED"],
                    "description": "Filter by device approval status"
                },
                "device_classes": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "WINDOWS_SERVER", "WINDOWS_WORKSTATION", "LINUX_WORKSTATION", "MAC",
                            "VMWARE_VM_HOST", "VMWARE_VM_GUEST", "LINUX_SERVER", "MAC_SERVER",
                            "CLOUD_MONITOR_TARGET", "NMS_SWITCH", "NMS_ROUTER", "NMS_FIREWALL",
                            "NMS_PRIVATE_NETWORK_GATEWAY", "NMS_PRINTER", "NMS_SCANNER",
                            "NMS_DIAL_MANAGER", "NMS_WAP", "NMS_IPSLA", "NMS_COMPUTER",
                            "NMS_VM_HOST", "NMS_APPLIANCE", "NMS_OTHER", "NMS_SERVER",
                            "NMS_PHONE", "NMS_VIRTUAL_MACHINE", "NMS_NETWORK_MANAGEMENT_AGENT"
                        ]
                    },
                    "description": "Filter by device classes (e.g., ['WINDOWS_SERVER', 'LINUX_SERVER'])"
                },
                "device_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Filter by specific device IDs"
                },
                "location_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Filter by location IDs"
                },
                "role_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Filter by device role IDs"
                },
                "group_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Filter by group membership (devices in these groups)"
                },
                "created_after": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "description": "Filter devices created after this date (YYYY-MM-DD format)"
                },
                "created_before": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "description": "Filter devices created before this date (YYYY-MM-DD format)"
                },

                # Exclusion filters
                "exclude_organizations": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Exclude devices from these organization IDs"
                },
                "exclude_locations": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Exclude devices from these location IDs"
                },
                "exclude_roles": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Exclude devices with these role IDs"
                },

                # Pagination
                "cursor": {
                    "type": "string",
                    "description": "Pagination cursor for next page"
                },
                "page_size": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 1000,
                    "default": 1000,
                    "description": "Number of devices to return (max 1000)"
                }
            },
            "required": []
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute get devices with enhanced filtering."""
        try:
            # Build query parameters
            params = {}

            # Handle pagination parameters
            if arguments.get("cursor"):
                params["cursor"] = arguments["cursor"]
            if arguments.get("page_size"):
                params["pageSize"] = arguments["page_size"]

            # Handle device filter - if raw device_filter is provided, use it directly
            if arguments.get("device_filter"):
                params["df"] = arguments["device_filter"]
            else:
                # Build filter from individual parameters
                filter_params = {
                    "organization_ids": arguments.get("organization_ids"),
                    "exclude_organizations": arguments.get("exclude_organizations"),
                    "location_ids": arguments.get("location_ids"),
                    "exclude_locations": arguments.get("exclude_locations"),
                    "role_ids": arguments.get("role_ids") or arguments.get("node_role_ids"),  # Support legacy parameter
                    "exclude_roles": arguments.get("exclude_roles"),
                    "device_ids": arguments.get("device_ids"),
                    "device_classes": arguments.get("device_classes"),
                    "approval_status": arguments.get("approval_status"),
                    "online_status": arguments.get("online_status"),
                    "created_after": arguments.get("created_after"),
                    "created_before": arguments.get("created_before"),
                    "group_ids": arguments.get("group_ids")
                }

                # Remove None values
                filter_params = {k: v for k, v in filter_params.items() if v is not None}

                if filter_params:
                    device_filter = DeviceFilterBuilder.from_parameters(**filter_params)
                    if device_filter:
                        params["df"] = device_filter

            # Handle legacy parameters for backward compatibility
            if arguments.get("organization_ids") and not params.get("df"):
                params["organizationIds"] = ",".join(map(str, arguments["organization_ids"]))

            if arguments.get("node_class_ids"):
                params["nodeClassIds"] = ",".join(map(str, arguments["node_class_ids"]))

            if arguments.get("node_role_ids") and not arguments.get("role_ids"):
                params["nodeRoleIds"] = ",".join(map(str, arguments["node_role_ids"]))

            result = await self.client.get("/devices", "get_devices", params=params)

            return [TextContent(
                type="text",
                text=self.client._safe_json_stringify(result)
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error getting devices: {str(e)}"
            )]


class GetDevicesDetailedTool(BaseTool):
    """Tool to get detailed device information."""
    
    @property
    def name(self) -> str:
        return "get_devices_detailed"
    
    @property
    def description(self) -> str:
        return """Get comprehensive device information with advanced filtering capabilities.

        Returns detailed device information including hardware specs, software, and system details.
        Supports the same comprehensive filtering as get_devices:
        - Organization, location, and role filtering (with inclusion/exclusion)
        - Device class filtering (WINDOWS_SERVER, MAC, LINUX_WORKSTATION, etc.)
        - Online/offline status filtering
        - Device approval status filtering
        - Creation date range filtering
        - Group membership filtering
        - Specific device ID filtering

        Examples:
        - Get detailed info for online Windows servers: online_status="online", device_classes=["WINDOWS_SERVER"]
        - Get detailed info for devices in specific groups: group_ids=[123, 456]
        - Get detailed info excluding certain orgs: exclude_organizations=[789]
        """

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                # Legacy parameters (maintained for backward compatibility)
                "organization_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Filter by organization IDs (legacy parameter, use for backward compatibility)"
                },
                "device_filter": {
                    "type": "string",
                    "description": "Raw device filter string (advanced users). If provided, other filter parameters are ignored."
                },
                "node_class_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Filter by node class IDs (legacy parameter)"
                },
                "node_role_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Filter by node role IDs (legacy parameter)"
                },

                # Enhanced filtering parameters
                "online_status": {
                    "type": "string",
                    "enum": ["online", "offline"],
                    "description": "Filter by device online/offline status"
                },
                "approval_status": {
                    "type": "string",
                    "enum": ["PENDING", "APPROVED"],
                    "description": "Filter by device approval status"
                },
                "device_classes": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "WINDOWS_SERVER", "WINDOWS_WORKSTATION", "LINUX_WORKSTATION", "MAC",
                            "VMWARE_VM_HOST", "VMWARE_VM_GUEST", "LINUX_SERVER", "MAC_SERVER",
                            "CLOUD_MONITOR_TARGET", "NMS_SWITCH", "NMS_ROUTER", "NMS_FIREWALL",
                            "NMS_PRIVATE_NETWORK_GATEWAY", "NMS_PRINTER", "NMS_SCANNER",
                            "NMS_DIAL_MANAGER", "NMS_WAP", "NMS_IPSLA", "NMS_COMPUTER",
                            "NMS_VM_HOST", "NMS_APPLIANCE", "NMS_OTHER", "NMS_SERVER",
                            "NMS_PHONE", "NMS_VIRTUAL_MACHINE", "NMS_NETWORK_MANAGEMENT_AGENT"
                        ]
                    },
                    "description": "Filter by device classes (e.g., ['WINDOWS_SERVER', 'LINUX_SERVER'])"
                },
                "device_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Filter by specific device IDs"
                },
                "location_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Filter by location IDs"
                },
                "role_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Filter by device role IDs"
                },
                "group_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Filter by group membership (devices in these groups)"
                },
                "created_after": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "description": "Filter devices created after this date (YYYY-MM-DD format)"
                },
                "created_before": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "description": "Filter devices created before this date (YYYY-MM-DD format)"
                },

                # Exclusion filters
                "exclude_organizations": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Exclude devices from these organization IDs"
                },
                "exclude_locations": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Exclude devices from these location IDs"
                },
                "exclude_roles": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Exclude devices with these role IDs"
                },

                # Pagination
                "cursor": {
                    "type": "string",
                    "description": "Pagination cursor for next page"
                },
                "page_size": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 1000,
                    "default": 1000,
                    "description": "Number of devices to return (max 1000)"
                }
            },
            "required": []
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute get devices detailed with enhanced filtering."""
        try:
            # Build query parameters
            params = {}

            # Handle pagination parameters
            if arguments.get("cursor"):
                params["cursor"] = arguments["cursor"]
            if arguments.get("page_size"):
                params["pageSize"] = arguments["page_size"]

            # Add detailed information flags
            params["detailed"] = "true"

            # Handle device filter - if raw device_filter is provided, use it directly
            if arguments.get("device_filter"):
                params["df"] = arguments["device_filter"]
            else:
                # Build filter from individual parameters
                filter_params = {
                    "organization_ids": arguments.get("organization_ids"),
                    "exclude_organizations": arguments.get("exclude_organizations"),
                    "location_ids": arguments.get("location_ids"),
                    "exclude_locations": arguments.get("exclude_locations"),
                    "role_ids": arguments.get("role_ids") or arguments.get("node_role_ids"),  # Support legacy parameter
                    "exclude_roles": arguments.get("exclude_roles"),
                    "device_ids": arguments.get("device_ids"),
                    "device_classes": arguments.get("device_classes"),
                    "approval_status": arguments.get("approval_status"),
                    "online_status": arguments.get("online_status"),
                    "created_after": arguments.get("created_after"),
                    "created_before": arguments.get("created_before"),
                    "group_ids": arguments.get("group_ids")
                }

                # Remove None values
                filter_params = {k: v for k, v in filter_params.items() if v is not None}

                if filter_params:
                    device_filter = DeviceFilterBuilder.from_parameters(**filter_params)
                    if device_filter:
                        params["df"] = device_filter

            # Handle legacy parameters for backward compatibility
            if arguments.get("organization_ids") and not params.get("df"):
                params["organizationIds"] = ",".join(map(str, arguments["organization_ids"]))

            if arguments.get("node_class_ids"):
                params["nodeClassIds"] = ",".join(map(str, arguments["node_class_ids"]))

            if arguments.get("node_role_ids") and not arguments.get("role_ids"):
                params["nodeRoleIds"] = ",".join(map(str, arguments["node_role_ids"]))

            result = await self.client.get("/devices-detailed", "get_devices_detailed", params=params)

            return [TextContent(
                type="text",
                text=self.client._safe_json_stringify(result)
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error getting detailed devices: {str(e)}"
            )]


class GetDeviceDetailsTool(BaseTool):
    """Tool to get detailed information about a specific device."""
    
    @property
    def name(self) -> str:
        return "get_device_details"
    
    @property
    def description(self) -> str:
        return "Get detailed information about a specific device by ID"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "device_id": {
                    "type": "integer",
                    "description": "The ID of the device to get details for"
                }
            },
            "required": ["device_id"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute get device details."""
        try:
            device_id = arguments["device_id"]
            result = await self.client.get(f"/device/{device_id}", "get_device_details")
            
            return [TextContent(
                type="text",
                text=self.client._safe_json_stringify(result)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error getting device details: {str(e)}"
            )]


class DeviceTools:
    """Collection of device management tools."""
    
    @staticmethod
    def get_tools(client) -> List[BaseTool]:
        """Get all device management tools."""
        return [
            GetOrganizationsTool(client),
            GetDevicesTool(client),
            GetDevicesDetailedTool(client),
            GetDeviceDetailsTool(client)
        ]
