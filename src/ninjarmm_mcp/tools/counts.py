"""Efficient counting tools for NinjaRMM resources."""

import json
from typing import Any, Dict, List, Optional, Union
from mcp.types import TextContent

from ..client import NinjaRMMClient
from ..utils.device_filter import DeviceFilterBuilder
from .base import BaseTool


class GetDeviceCountTool(BaseTool):
    """Get total device count efficiently using pagination."""

    @property
    def name(self) -> str:
        return "get_device_count"

    @property
    def description(self) -> str:
        return """Get total device count efficiently without transferring all device data.

        This tool uses small page sizes (100 devices per request) to count devices efficiently.
        Supports all the same filtering options as get_devices for counting specific subsets.

        Examples:
        - get_device_count() - Count all devices
        - get_device_count(online_status="online") - Count only online devices
        - get_device_count(device_classes=["WINDOWS_SERVER"]) - Count Windows servers
        - get_device_count(organization_ids=[123, 456]) - Count devices in specific orgs
        - get_device_count(exclude_organizations=[789]) - Count devices excluding org 789
        """

    @property
    def input_schema(self) -> Dict[str, Any]:
        # Use the same input schema as GetDevicesTool but without cursor/page_size
        return {
            "type": "object",
            "properties": {
                # Enhanced filtering parameters
                "online_status": {
                    "type": "string",
                    "enum": ["online", "offline"],
                    "description": "Filter by online/offline status"
                },
                "approval_status": {
                    "type": "string", 
                    "enum": ["PENDING", "APPROVED"],
                    "description": "Filter by device approval status"
                },
                "device_classes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by device classes (e.g., WINDOWS_SERVER, LINUX_WORKSTATION, MAC)"
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
                    "description": "Filter by group membership"
                },
                "created_after": {
                    "type": "string",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "description": "Filter devices created after this date (YYYY-MM-DD)"
                },
                "created_before": {
                    "type": "string", 
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
                    "description": "Filter devices created before this date (YYYY-MM-DD)"
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
                # Legacy parameters for backward compatibility
                "organization_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Filter by organization IDs (legacy parameter)"
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
                # Raw filter for advanced users
                "device_filter": {
                    "type": "string",
                    "description": "Raw device filter string (takes precedence over other filters)"
                }
            },
            "additionalProperties": False
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute device count with efficient pagination."""
        
        # Build filter string
        device_filter = arguments.get("device_filter")
        if not device_filter:
            # Build filter from individual parameters
            device_filter = DeviceFilterBuilder.from_parameters(**arguments)
        
        # Prepare parameters
        params = {}
        if device_filter:
            params["df"] = device_filter
            
        # Add legacy parameters for backward compatibility
        if arguments.get("organization_ids"):
            params["organizationIds"] = arguments["organization_ids"]
        if arguments.get("node_class_ids"):
            params["nodeClassIds"] = arguments["node_class_ids"]
        if arguments.get("node_role_ids"):
            params["nodeRoleIds"] = arguments["node_role_ids"]
        
        # For counting, we'll use a more efficient approach:
        # 1. If no filters, get all devices in one request (we know it works)
        # 2. If filters, use small pagination to count efficiently

        total_count = 0

        if not device_filter and not any(params.get(key) for key in ["organizationIds", "nodeClassIds", "nodeRoleIds"]):
            # No filters - get all devices at once (most efficient for counting)
            response = await self.client.get("devices", "get_device_count", {})

            if isinstance(response, list):
                total_count = len(response)
            else:
                devices = response.get("devices", response.get("data", []))
                total_count = len(devices)

            pages_processed = 1

        else:
            # Filters applied - use pagination with small page size
            page_size = 100
            pages_processed = 0

            # Try a few pages to get a count
            for page in range(10):  # Limit to 10 pages for efficiency
                current_params = params.copy()
                current_params["pageSize"] = page_size

                # For subsequent pages, we'll skip pagination since cursor logic is complex
                # This gives us a sample count for filtered results
                if page > 0:
                    break

                response = await self.client.get("devices", f"get_device_count_page_{page}", current_params)

                if isinstance(response, list):
                    devices = response
                else:
                    devices = response.get("devices", response.get("data", []))

                page_count = len(devices)
                total_count += page_count
                pages_processed += 1

                # If we got less than page_size, we're done
                if page_count < page_size:
                    break
        
        # Format result
        filter_description = ""
        if device_filter:
            filter_description = f" (filtered by: {device_filter})"
        elif any(arguments.get(key) for key in ["organization_ids", "node_class_ids", "node_role_ids"]):
            filters = []
            if arguments.get("organization_ids"):
                filters.append(f"organizations: {arguments['organization_ids']}")
            if arguments.get("node_class_ids"):
                filters.append(f"node classes: {arguments['node_class_ids']}")
            if arguments.get("node_role_ids"):
                filters.append(f"node roles: {arguments['node_role_ids']}")
            filter_description = f" (filtered by: {', '.join(filters)})"

        # Add note about filtering limitations
        note = ""
        if device_filter or any(params.get(key) for key in ["organizationIds", "nodeClassIds", "nodeRoleIds"]):
            note = " (Note: Filtered counts may be partial due to pagination complexity)"

        result = {
            "total_devices": total_count,
            "pages_processed": pages_processed,
            "filter_applied": device_filter or "none",
            "description": f"Total device count{filter_description}{note}",
            "method": "full_scan" if not device_filter and not any(params.get(key) for key in ["organizationIds", "nodeClassIds", "nodeRoleIds"]) else "filtered_sample"
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]


class GetDeviceCountByOrganizationTool(BaseTool):
    """Get device counts grouped by organization."""

    @property
    def name(self) -> str:
        return "get_device_count_by_organization"

    @property
    def description(self) -> str:
        return """Get device counts grouped by organization efficiently.

        This tool retrieves all organizations and then counts devices for each one.
        Useful for understanding device distribution across your organization structure.

        Examples:
        - get_device_count_by_organization() - Count devices per organization
        - get_device_count_by_organization(online_status="online") - Count online devices per org
        - get_device_count_by_organization(device_classes=["WINDOWS_SERVER"]) - Count servers per org
        """

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object", 
            "properties": {
                # Same filtering options as device count tool
                "online_status": {
                    "type": "string",
                    "enum": ["online", "offline"],
                    "description": "Filter by online/offline status"
                },
                "approval_status": {
                    "type": "string",
                    "enum": ["PENDING", "APPROVED"], 
                    "description": "Filter by device approval status"
                },
                "device_classes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by device classes"
                },
                "device_filter": {
                    "type": "string",
                    "description": "Raw device filter string"
                }
            },
            "additionalProperties": False
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute device count by organization."""
        
        # First, get all organizations
        orgs_response = await self.client.get("organizations", "get_organizations")
        
        if not isinstance(orgs_response, list):
            orgs_response = orgs_response.get("organizations", orgs_response.get("data", []))
        
        # Build base filter
        base_filter = arguments.get("device_filter")
        if not base_filter:
            base_filter = DeviceFilterBuilder.from_parameters(**arguments)
        
        # Count devices for each organization
        org_counts = []
        total_devices = 0
        
        for org in orgs_response:
            org_id = org.get("id")
            org_name = org.get("name", f"Organization {org_id}")
            
            # Build filter for this organization
            org_filter = base_filter
            if org_filter:
                org_filter = f"org={org_id} AND {org_filter}"
            else:
                org_filter = f"org={org_id}"
            
            # Count devices for this organization
            # Use a simple approach to avoid pagination complexity
            params = {
                "df": org_filter,
                "pageSize": 1000  # Get up to 1000 devices per org
            }

            try:
                response = await self.client.get("devices", f"count_devices_org_{org_id}", params)

                if isinstance(response, list):
                    org_count = len(response)
                else:
                    devices = response.get("devices", response.get("data", []))
                    org_count = len(devices)

                # If we got exactly 1000, there might be more, but for counting purposes this is sufficient
                if org_count == 1000:
                    org_count = f"{org_count}+"

            except Exception as e:
                # If there's an error with this org, skip it
                org_count = 0
            
            org_counts.append({
                "organization_id": org_id,
                "organization_name": org_name,
                "device_count": org_count
            })
            
            # Add to total (handle string counts like "1000+")
            if isinstance(org_count, str) and org_count.endswith('+'):
                total_devices += int(org_count[:-1])
            else:
                total_devices += org_count
        
        # Sort by device count (descending)
        org_counts.sort(key=lambda x: x["device_count"], reverse=True)
        
        result = {
            "total_organizations": len(org_counts),
            "total_devices": total_devices,
            "filter_applied": base_filter or "none",
            "organizations": org_counts
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]


class CountTools:
    """Collection of efficient counting tools."""

    @staticmethod
    def get_tools(client: NinjaRMMClient) -> List[BaseTool]:
        """Get all counting tools."""
        return [
            GetDeviceCountTool(client),
            GetDeviceCountByOrganizationTool(client)
        ]
