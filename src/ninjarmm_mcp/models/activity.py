"""Activity data models."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ActivityFilter(BaseModel):
    """Filter parameters for activity queries."""
    
    device_ids: Optional[List[int]] = None
    organization_ids: Optional[List[int]] = None
    activity_types: Optional[List[str]] = None
    status: Optional[str] = None
    since: Optional[datetime] = None
    until: Optional[datetime] = None
    cursor: Optional[str] = None
    page_size: Optional[int] = Field(default=1000, le=1000)


class Activity(BaseModel):
    """Activity/event information model."""
    
    id: int
    device_id: Optional[int] = None
    device_name: Optional[str] = None
    organization_id: Optional[int] = None
    organization_name: Optional[str] = None
    activity_type: str
    status: Optional[str] = None
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    user: Optional[str] = None
    
    # Script execution specific fields
    script_id: Optional[int] = None
    script_name: Optional[str] = None
    execution_id: Optional[str] = None
    exit_code: Optional[int] = None
    output: Optional[str] = None
    error_output: Optional[str] = None
    duration: Optional[int] = None  # in seconds
    
    # Additional metadata
    source: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
