"""NinjaRMM MCP Server - Python Implementation.

A comprehensive MCP server for NinjaRMM API v2 with support for:
- Device management and monitoring
- Activity tracking and script execution
- Alert management
- Backup job monitoring
- Comprehensive ticketing system
- OAuth2 authentication with client credentials and user flows
"""

__version__ = "1.4.4"
__author__ = "Chris Goetz"
__email__ = "goetzcj@gmail.com"

from .server import NinjaRMMServer

__all__ = ["NinjaRMMServer"]
