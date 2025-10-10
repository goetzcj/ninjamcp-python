# NinjaMCP Python

A comprehensive Model Context Protocol (MCP) server for NinjaRMM API v2, providing seamless integration with NinjaRMM's remote monitoring and management platform.

## Features

**24 comprehensive tools** for complete NinjaRMM management across 8 categories:

### 🔐 Credential Management System Integration

The server supports integration with external credential management systems for enterprise environments:

- **Environment variable injection**: Automatically detect tokens from environment variables
- **Programmatic injection**: Inject tokens via API calls from your credential management system
- **Centralized authentication**: No browser-based OAuth2 flows in production
- **Token refresh support**: Automatic token refresh using provided refresh tokens
- **Backward compatibility**: Falls back to standard OAuth2 flows if no tokens are injected

See [Credential Management Integration Guide](docs/credential_management_integration.md) for detailed implementation.

### Device Management
- **get_organizations**: List all organizations with IDs and names
- **get_devices**: Get basic device information with **advanced filtering capabilities**
- **get_devices_detailed**: Get comprehensive device information with **advanced filtering capabilities**
- **get_device_details**: Get detailed information about a specific device

#### 🎯 Enhanced Device Filtering
Both device tools now support comprehensive filtering based on NinjaRMM API v2.0.5 Device Filter Syntax:
- **Status filtering**: Online/offline, approval status
- **Device classification**: Windows/Linux servers, workstations, Mac, network devices
- **Organizational filtering**: Include/exclude organizations, locations, roles
- **Date filtering**: Creation date ranges
- **Group membership**: Filter by device groups
- **Specific selection**: Filter by device IDs

**Example**: Get all online Windows servers excluding specific organizations:
```python
get_devices(
    online_status="online",
    device_classes=["WINDOWS_SERVER"],
    exclude_organizations=[123, 456]
)
```

📖 See [Device Filtering Guide](docs/device_filtering_guide.md) for comprehensive examples and usage.

### Efficient Counting Tools (2 tools)
- **get_device_count** - Get total device count efficiently without transferring all device data
- **get_device_count_by_organization** - Get device counts grouped by organization

#### 🚀 **Efficient Counting for Scale**
These tools are designed for efficiency as your device count grows:
- **Smart counting**: Uses full scan for unfiltered counts, sampling for filtered counts
- **No data transfer**: Only counts devices without downloading full device information
- **Organization breakdown**: Understand device distribution across your organization structure

**Example**: Get total device count efficiently:
```python
get_device_count()  # Returns: {"total_devices": 569, "method": "full_scan"}
```

**Example**: Count online devices only:
```python
get_device_count(online_status="online")  # Efficient filtered counting
```

### Activity Monitoring
- **get_activities**: Retrieve activities/events with optional filtering
- **monitor_device_activities**: Monitor activities for specific devices with real-time capabilities
- **track_script_execution**: Track script execution outcomes with detailed monitoring
- **wait_for_activity_outcome**: Wait for and monitor action outcomes with polling

### Alert Management
- **get_alerts**: Retrieve alerts with optional filtering by device or organization
- **reset_alert**: Reset/acknowledge specific alerts

### Backup & Automation
- **get_backup_jobs**: Retrieve backup job information
- **get_automation_scripts**: Get available automation scripts
- **run_script**: Execute automation scripts on devices

### Comprehensive Ticketing System
- **get_tickets_open**: Get all open tickets with advanced filtering
- **get_tickets_unassigned**: Get unassigned tickets for quick triage
- **get_ticket_details**: Get detailed ticket information including notes and history
- **update_ticket_status**: Update ticket status with proper validation
- **add_ticket_note**: Add public or private notes to tickets with time tracking

### Authentication Management
- **get_auth_status**: Check current authentication status and capabilities
- **reauthorize_user**: Re-authenticate user for ticket operations
- **clear_tokens**: Clear stored authentication tokens

## Authentication

The server supports sophisticated OAuth2 authentication with multiple flows:

- **Client Credentials Flow**: For machine-to-machine operations
- **User Authorization Flow**: For user-context operations (required for ticketing)
- **Hybrid Mode**: Intelligently chooses the best authentication method
- **Token Management**: Automatic token refresh and storage

## Installation

```bash
pip install ninjamcp-python
```

## Configuration

Create a `.env` file with your NinjaRMM credentials:

```env
NINJARMM_CLIENT_ID=your_client_id
NINJARMM_CLIENT_SECRET=your_client_secret
NINJARMM_BASE_URL=https://app.ninjarmm.com
NINJARMM_AUTH_MODE=hybrid
NINJARMM_CLIENT_SCOPES=monitoring management control
NINJARMM_USER_SCOPES=monitoring management control
NINJARMM_USER_REDIRECT_PORT=8090
NINJARMM_TOKEN_STORAGE_PATH=./tokens.json
```

## Usage

### As a Standalone Server

```bash
ninjamcp-python
```

### As a Python Package

```python
from ninjarmm_mcp import NinjaRMMServer

server = NinjaRMMServer()
await server.run()
```

## Requirements

- Python 3.8+
- NinjaRMM API v2 access
- Valid OAuth2 client credentials

## License

MIT License - see LICENSE file for details.
