"""Device data models."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DeviceFilter(BaseModel):
    """Filter parameters for device queries."""
    
    organization_ids: Optional[List[int]] = None
    device_filter: Optional[str] = None
    node_class_ids: Optional[List[int]] = None
    node_role_ids: Optional[List[int]] = None
    cursor: Optional[str] = None
    page_size: Optional[int] = Field(default=1000, le=1000)


class Device(BaseModel):
    """Device information model."""
    
    id: int
    organization_id: int
    organization_name: Optional[str] = None
    node_name: str
    node_class: Optional[str] = None
    node_role: Optional[str] = None
    system_name: Optional[str] = None
    dns_name: Optional[str] = None
    ip_addresses: Optional[List[str]] = None
    mac_addresses: Optional[List[str]] = None
    os: Optional[str] = None
    os_version: Optional[str] = None
    cpu: Optional[str] = None
    memory: Optional[str] = None
    disk_space: Optional[str] = None
    last_contact: Optional[datetime] = None
    approval_status: Optional[str] = None
    is_online: Optional[bool] = None
    
    # Additional fields for detailed device info
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    bios_version: Optional[str] = None
    domain: Optional[str] = None
    workgroup: Optional[str] = None
    antivirus: Optional[Dict[str, Any]] = None
    patches: Optional[Dict[str, Any]] = None
    software: Optional[List[Dict[str, Any]]] = None
    hardware: Optional[Dict[str, Any]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
