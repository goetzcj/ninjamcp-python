"""Ticketing system tools for NinjaRMM MCP Server."""

from typing import Dict, Any, List
from mcp.types import TextContent

from .base import BaseTool


class GetTicketBoardsTool(BaseTool):
    """Tool to get ticket boards."""
    
    @property
    def name(self) -> str:
        return "get_ticket_boards"
    
    @property
    def description(self) -> str:
        return "Get all available ticket boards"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute get ticket boards."""
        try:
            result = await self.client.get("/ticketing/boards", "get_ticket_boards")
            
            return [TextContent(
                type="text",
                text=self.client._safe_json_stringify(result)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error getting ticket boards: {str(e)}"
            )]


class GetMyTicketsTool(BaseTool):
    """Tool to get tickets assigned to the current user."""
    
    @property
    def name(self) -> str:
        return "get_my_tickets"
    
    @property
    def description(self) -> str:
        return "Get tickets assigned to the current user with optional filtering"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "board_id": {
                    "type": "integer",
                    "description": "Filter by ticket board ID"
                },
                "status": {
                    "type": "string",
                    "description": "Filter by ticket status (e.g., 'OPEN', 'IN_PROGRESS', 'RESOLVED')"
                },
                "priority": {
                    "type": "string",
                    "description": "Filter by priority (e.g., 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL')"
                },
                "since": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Get tickets since this timestamp (ISO format)"
                },
                "until": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Get tickets until this timestamp (ISO format)"
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
                    "description": "Number of tickets to return (max 1000)"
                }
            },
            "required": []
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute get my tickets."""
        try:
            # Build query parameters
            params = {"assignedToMe": "true"}
            
            if arguments.get("board_id"):
                params["boardId"] = arguments["board_id"]
            
            if arguments.get("status"):
                params["status"] = arguments["status"]
            
            if arguments.get("priority"):
                params["priority"] = arguments["priority"]
            
            if arguments.get("since"):
                params["since"] = arguments["since"]
            
            if arguments.get("until"):
                params["until"] = arguments["until"]
            
            if arguments.get("cursor"):
                params["cursor"] = arguments["cursor"]
            
            if arguments.get("page_size"):
                params["pageSize"] = arguments["page_size"]
            
            result = await self.client.get("/ticketing/tickets", "get_my_tickets", params=params)
            
            return [TextContent(
                type="text",
                text=self.client._safe_json_stringify(result)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error getting my tickets: {str(e)}"
            )]


class GetUnassignedTicketsTool(BaseTool):
    """Tool to get unassigned tickets for quick triage."""
    
    @property
    def name(self) -> str:
        return "get_unassigned_tickets"
    
    @property
    def description(self) -> str:
        return "Get unassigned tickets for quick triage with optional filtering"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "board_id": {
                    "type": "integer",
                    "description": "Filter by ticket board ID"
                },
                "priority": {
                    "type": "string",
                    "description": "Filter by priority (e.g., 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL')"
                },
                "organization_ids": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Filter by organization IDs"
                },
                "since": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Get tickets since this timestamp (ISO format)"
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
                    "description": "Number of tickets to return (max 1000)"
                }
            },
            "required": []
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute get unassigned tickets."""
        try:
            # Build query parameters
            params = {"unassigned": "true"}
            
            if arguments.get("board_id"):
                params["boardId"] = arguments["board_id"]
            
            if arguments.get("priority"):
                params["priority"] = arguments["priority"]
            
            if arguments.get("organization_ids"):
                params["organizationIds"] = ",".join(map(str, arguments["organization_ids"]))
            
            if arguments.get("since"):
                params["since"] = arguments["since"]
            
            if arguments.get("cursor"):
                params["cursor"] = arguments["cursor"]
            
            if arguments.get("page_size"):
                params["pageSize"] = arguments["page_size"]
            
            result = await self.client.get("/ticketing/tickets", "get_unassigned_tickets", params=params)
            
            return [TextContent(
                type="text",
                text=self.client._safe_json_stringify(result)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error getting unassigned tickets: {str(e)}"
            )]


class GetTicketDetailsTool(BaseTool):
    """Tool to get detailed ticket information including notes and history."""
    
    @property
    def name(self) -> str:
        return "get_ticket_details"
    
    @property
    def description(self) -> str:
        return "Get detailed information about a specific ticket including notes, history, and attachments"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "ticket_id": {
                    "type": "integer",
                    "description": "The ID of the ticket to get details for"
                },
                "include_comments": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include ticket comments/notes in the response"
                },
                "include_history": {
                    "type": "boolean",
                    "default": True,
                    "description": "Include ticket history in the response"
                }
            },
            "required": ["ticket_id"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute get ticket details."""
        try:
            ticket_id = arguments["ticket_id"]
            include_comments = arguments.get("include_comments", True)
            include_history = arguments.get("include_history", True)
            
            # Build query parameters
            params = {}
            if include_comments:
                params["includeComments"] = "true"
            if include_history:
                params["includeHistory"] = "true"
            
            result = await self.client.get(f"/ticketing/tickets/{ticket_id}", "get_ticket_details", params=params)
            
            return [TextContent(
                type="text",
                text=self.client._safe_json_stringify(result)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error getting ticket details: {str(e)}"
            )]


class UpdateTicketStatusTool(BaseTool):
    """Tool to update ticket status with proper validation."""

    @property
    def name(self) -> str:
        return "update_ticket_status"

    @property
    def description(self) -> str:
        return "Update ticket status with proper validation and optional notes"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "ticket_id": {
                    "type": "integer",
                    "description": "The ID of the ticket to update"
                },
                "status": {
                    "type": "string",
                    "description": "New status for the ticket (e.g., 'OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED')"
                },
                "assigned_to": {
                    "type": "string",
                    "description": "User to assign the ticket to (optional)"
                },
                "priority": {
                    "type": "string",
                    "description": "New priority for the ticket (optional)"
                },
                "note": {
                    "type": "string",
                    "description": "Optional note to add when updating status"
                },
                "is_public_note": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether the note should be public (visible to customer)"
                }
            },
            "required": ["ticket_id", "status"]
        }

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute update ticket status."""
        try:
            ticket_id = arguments["ticket_id"]
            status = arguments["status"]
            assigned_to = arguments.get("assigned_to")
            priority = arguments.get("priority")
            note = arguments.get("note")
            is_public_note = arguments.get("is_public_note", True)

            # Prepare request data
            data = {"status": status}

            if assigned_to:
                data["assignedTo"] = assigned_to

            if priority:
                data["priority"] = priority

            if note:
                data["note"] = note
                data["isPublicNote"] = is_public_note

            result = await self.client.patch(f"/ticketing/tickets/{ticket_id}", "update_ticket_status", data=data)

            return [TextContent(
                type="text",
                text=self.client._safe_json_stringify(result)
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error updating ticket status: {str(e)}"
            )]


class AddTicketNoteTool(BaseTool):
    """Tool to add public or private notes to tickets with time tracking."""

    @property
    def name(self) -> str:
        return "add_ticket_note"

    @property
    def description(self) -> str:
        return "Add public or private notes to tickets with optional time tracking"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "ticket_id": {
                    "type": "integer",
                    "description": "The ID of the ticket to add a note to"
                },
                "content": {
                    "type": "string",
                    "description": "The content of the note"
                },
                "is_public": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether the note should be public (visible to customer)"
                },
                "time_spent": {
                    "type": "integer",
                    "minimum": 0,
                    "description": "Time spent in minutes (for time tracking)"
                },
                "billable": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether the time spent is billable"
                }
            },
            "required": ["ticket_id", "content"]
        }

    async def execute(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Execute add ticket note."""
        try:
            ticket_id = arguments["ticket_id"]
            content = arguments["content"]
            is_public = arguments.get("is_public", True)
            time_spent = arguments.get("time_spent")
            billable = arguments.get("billable", False)

            # Prepare request data
            data = {
                "content": content,
                "isPublic": is_public
            }

            if time_spent is not None:
                data["timeSpent"] = time_spent
                data["billable"] = billable

            result = await self.client.post(f"/ticketing/tickets/{ticket_id}/notes", "add_ticket_note", data=data)

            return [TextContent(
                type="text",
                text=self.client._safe_json_stringify(result)
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error adding ticket note: {str(e)}"
            )]


class TicketTools:
    """Collection of ticketing system tools."""

    @staticmethod
    def get_tools(client) -> List[BaseTool]:
        """Get all ticketing system tools."""
        return [
            GetTicketBoardsTool(client),
            GetMyTicketsTool(client),
            GetUnassignedTicketsTool(client),
            GetTicketDetailsTool(client),
            UpdateTicketStatusTool(client),
            AddTicketNoteTool(client)
        ]
