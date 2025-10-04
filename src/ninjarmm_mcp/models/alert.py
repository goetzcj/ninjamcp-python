"""Alert data models."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AlertFilter(BaseModel):
    """Filter parameters for alert queries."""
    
    device_ids: Optional[List[int]] = None
    organization_ids: Optional[List[int]] = None
    alert_types: Optional[List[str]] = None
    status: Optional[str] = None
    severity: Optional[str] = None
    since: Optional[datetime] = None
    until: Optional[datetime] = None
    cursor: Optional[str] = None
    page_size: Optional[int] = Field(default=1000, le=1000)


class Alert(BaseModel):
    """Alert information model."""
    
    id: int
    device_id: Optional[int] = None
    device_name: Optional[str] = None
    organization_id: Optional[int] = None
    organization_name: Optional[str] = None
    alert_type: str
    status: str
    severity: Optional[str] = None
    title: str
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    
    # Additional metadata
    source: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
