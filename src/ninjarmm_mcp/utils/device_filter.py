"""Device filter builder utility for NinjaRMM API."""

import urllib.parse
from typing import List, Optional, Union, Dict, Any
from datetime import datetime
import re


class DeviceFilterBuilder:
    """Utility class to build NinjaRMM device filter strings from individual parameters."""
    
    # Valid device classes as per NinjaRMM documentation
    VALID_DEVICE_CLASSES = {
        "WINDOWS_SERVER",
        "WINDOWS_WORKSTATION", 
        "LINUX_WORKSTATION",
        "MAC",
        "VMWARE_VM_HOST",
        "VMWARE_VM_GUEST",
        "LINUX_SERVER",
        "MAC_SERVER",
        "CLOUD_MONITOR_TARGET",
        "NMS_SWITCH",
        "NMS_ROUTER",
        "NMS_FIREWALL",
        "NMS_PRIVATE_NETWORK_GATEWAY",
        "NMS_PRINTER",
        "NMS_SCANNER",
        "NMS_DIAL_MANAGER",
        "NMS_WAP",
        "NMS_IPSLA",
        "NMS_COMPUTER",
        "NMS_VM_HOST",
        "NMS_APPLIANCE",
        "NMS_OTHER",
        "NMS_SERVER",
        "NMS_PHONE",
        "NMS_VIRTUAL_MACHINE",
        "NMS_NETWORK_MANAGEMENT_AGENT"
    }
    
    VALID_APPROVAL_STATUSES = {"PENDING", "APPROVED"}
    VALID_ONLINE_STATUSES = {"online", "offline"}
    
    def __init__(self):
        """Initialize the filter builder."""
        self.filters = []
    
    def add_organization_filter(self, org_ids: Union[int, List[int]], exclude: bool = False) -> 'DeviceFilterBuilder':
        """Add organization filter.
        
        Args:
            org_ids: Single organization ID or list of organization IDs
            exclude: If True, exclude these organizations (use != or nin)
        """
        if isinstance(org_ids, int):
            org_ids = [org_ids]
        
        if not org_ids:
            return self
            
        if len(org_ids) == 1:
            operator = "!=" if exclude else "="
            self.filters.append(f"org{operator}{org_ids[0]}")
        else:
            operator = "nin" if exclude else "in"
            ids_str = ", ".join(map(str, org_ids))
            self.filters.append(f"org {operator} ({ids_str})")
        
        return self
    
    def add_location_filter(self, loc_ids: Union[int, List[int]], exclude: bool = False) -> 'DeviceFilterBuilder':
        """Add location filter.
        
        Args:
            loc_ids: Single location ID or list of location IDs
            exclude: If True, exclude these locations (use != or nin)
        """
        if isinstance(loc_ids, int):
            loc_ids = [loc_ids]
        
        if not loc_ids:
            return self
            
        if len(loc_ids) == 1:
            operator = "!=" if exclude else "="
            self.filters.append(f"loc{operator}{loc_ids[0]}")
        else:
            operator = "nin" if exclude else "in"
            ids_str = ", ".join(map(str, loc_ids))
            self.filters.append(f"loc {operator} ({ids_str})")
        
        return self
    
    def add_role_filter(self, role_ids: Union[int, List[int]], exclude: bool = False) -> 'DeviceFilterBuilder':
        """Add device role filter.
        
        Args:
            role_ids: Single role ID or list of role IDs
            exclude: If True, exclude these roles (use != or nin)
        """
        if isinstance(role_ids, int):
            role_ids = [role_ids]
        
        if not role_ids:
            return self
            
        if len(role_ids) == 1:
            operator = "!=" if exclude else "="
            self.filters.append(f"role{operator}{role_ids[0]}")
        else:
            operator = "nin" if exclude else "in"
            ids_str = ", ".join(map(str, role_ids))
            self.filters.append(f"role {operator} ({ids_str})")
        
        return self
    
    def add_device_id_filter(self, device_ids: Union[int, List[int]]) -> 'DeviceFilterBuilder':
        """Add device ID filter.
        
        Args:
            device_ids: Single device ID or list of device IDs
        """
        if isinstance(device_ids, int):
            device_ids = [device_ids]
        
        if not device_ids:
            return self
            
        if len(device_ids) == 1:
            self.filters.append(f"id={device_ids[0]}")
        else:
            ids_str = ", ".join(map(str, device_ids))
            self.filters.append(f"id in ({ids_str})")
        
        return self
    
    def add_device_class_filter(self, device_classes: Union[str, List[str]]) -> 'DeviceFilterBuilder':
        """Add device class filter.
        
        Args:
            device_classes: Single device class or list of device classes
        """
        if isinstance(device_classes, str):
            device_classes = [device_classes]
        
        if not device_classes:
            return self
        
        # Validate device classes
        invalid_classes = set(device_classes) - self.VALID_DEVICE_CLASSES
        if invalid_classes:
            raise ValueError(f"Invalid device classes: {invalid_classes}. Valid classes: {self.VALID_DEVICE_CLASSES}")
        
        if len(device_classes) == 1:
            self.filters.append(f"class={device_classes[0]}")
        else:
            classes_str = ", ".join(device_classes)
            self.filters.append(f"class in ({classes_str})")
        
        return self
    
    def add_approval_status_filter(self, status: str) -> 'DeviceFilterBuilder':
        """Add device approval status filter.
        
        Args:
            status: Approval status ('PENDING' or 'APPROVED')
        """
        if status not in self.VALID_APPROVAL_STATUSES:
            raise ValueError(f"Invalid approval status: {status}. Valid statuses: {self.VALID_APPROVAL_STATUSES}")
        
        self.filters.append(f"status={status}")
        return self
    
    def add_online_status_filter(self, status: str) -> 'DeviceFilterBuilder':
        """Add device online/offline status filter.
        
        Args:
            status: Online status ('online' or 'offline')
        """
        if status not in self.VALID_ONLINE_STATUSES:
            raise ValueError(f"Invalid online status: {status}. Valid statuses: {self.VALID_ONLINE_STATUSES}")
        
        self.filters.append(status)
        return self
    
    def add_creation_date_filter(self, after: Optional[str] = None, before: Optional[str] = None) -> 'DeviceFilterBuilder':
        """Add device creation date filter.
        
        Args:
            after: Return devices created after this date (YYYY-MM-DD format)
            before: Return devices created before this date (YYYY-MM-DD format)
        """
        if after:
            if not self._validate_date_format(after):
                raise ValueError(f"Invalid date format for 'after': {after}. Use YYYY-MM-DD format.")
            self.filters.append(f"created after {after}")
        
        if before:
            if not self._validate_date_format(before):
                raise ValueError(f"Invalid date format for 'before': {before}. Use YYYY-MM-DD format.")
            self.filters.append(f"created before {before}")
        
        return self
    
    def add_group_filter(self, group_ids: Union[int, List[int]]) -> 'DeviceFilterBuilder':
        """Add group membership filter.
        
        Args:
            group_ids: Single group ID or list of group IDs
        """
        if isinstance(group_ids, int):
            group_ids = [group_ids]
        
        if not group_ids:
            return self
        
        for group_id in group_ids:
            self.filters.append(f"group {group_id}")
        
        return self
    
    def build(self) -> str:
        """Build the final filter string.

        Returns:
            Filter string ready for use in API calls (not URL-encoded)
        """
        if not self.filters:
            return ""

        # Join filters with AND operator
        filter_string = " AND ".join(self.filters)

        # Return raw filter string (httpx will handle URL encoding)
        return filter_string
    
    def clear(self) -> 'DeviceFilterBuilder':
        """Clear all filters."""
        self.filters = []
        return self
    
    @staticmethod
    def _validate_date_format(date_str: str) -> bool:
        """Validate date format (YYYY-MM-DD).
        
        Args:
            date_str: Date string to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    @classmethod
    def from_parameters(cls, **kwargs) -> str:
        """Build a filter string from keyword parameters.
        
        Args:
            **kwargs: Filter parameters
            
        Returns:
            URL-encoded filter string
        """
        builder = cls()
        
        # Organization filters
        if kwargs.get("organization_ids"):
            builder.add_organization_filter(kwargs["organization_ids"])
        if kwargs.get("exclude_organizations"):
            builder.add_organization_filter(kwargs["exclude_organizations"], exclude=True)
        
        # Location filters
        if kwargs.get("location_ids"):
            builder.add_location_filter(kwargs["location_ids"])
        if kwargs.get("exclude_locations"):
            builder.add_location_filter(kwargs["exclude_locations"], exclude=True)
        
        # Role filters
        if kwargs.get("role_ids"):
            builder.add_role_filter(kwargs["role_ids"])
        if kwargs.get("exclude_roles"):
            builder.add_role_filter(kwargs["exclude_roles"], exclude=True)
        
        # Device ID filter
        if kwargs.get("device_ids"):
            builder.add_device_id_filter(kwargs["device_ids"])
        
        # Device class filter
        if kwargs.get("device_classes"):
            builder.add_device_class_filter(kwargs["device_classes"])
        
        # Status filters
        if kwargs.get("approval_status"):
            builder.add_approval_status_filter(kwargs["approval_status"])
        if kwargs.get("online_status"):
            builder.add_online_status_filter(kwargs["online_status"])
        
        # Date filters
        if kwargs.get("created_after") or kwargs.get("created_before"):
            builder.add_creation_date_filter(
                after=kwargs.get("created_after"),
                before=kwargs.get("created_before")
            )
        
        # Group filter
        if kwargs.get("group_ids"):
            builder.add_group_filter(kwargs["group_ids"])
        
        return builder.build()
