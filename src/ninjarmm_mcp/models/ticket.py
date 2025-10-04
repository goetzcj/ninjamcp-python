"""Ticket data models."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class TicketFilter(BaseModel):
    """Filter parameters for ticket queries."""
    
    board_id: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    created_by: Optional[str] = None
    organization_ids: Optional[List[int]] = None
    device_ids: Optional[List[int]] = None
    since: Optional[datetime] = None
    until: Optional[datetime] = None
    cursor: Optional[str] = None
    page_size: Optional[int] = Field(default=1000, le=1000)


class TicketComment(BaseModel):
    """Ticket comment/note model."""
    
    id: Optional[int] = None
    ticket_id: int
    author: str
    content: str
    is_public: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    time_spent: Optional[int] = None  # in minutes
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class Ticket(BaseModel):
    """Ticket information model."""
    
    id: int
    board_id: Optional[int] = None
    board_name: Optional[str] = None
    organization_id: Optional[int] = None
    organization_name: Optional[str] = None
    device_id: Optional[int] = None
    device_name: Optional[str] = None
    
    # Core ticket fields
    title: str
    description: Optional[str] = None
    status: str
    priority: Optional[str] = None
    type: Optional[str] = None
    category: Optional[str] = None
    
    # Assignment and ownership
    assigned_to: Optional[str] = None
    assigned_to_id: Optional[int] = None
    created_by: str
    created_by_id: Optional[int] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    # Time tracking
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    billable_hours: Optional[float] = None
    
    # Additional fields
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    comments: Optional[List[TicketComment]] = None
    
    # Workflow and approval
    approval_status: Optional[str] = None
    workflow_step: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
