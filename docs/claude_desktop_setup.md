# Claude Desktop Integration Guide

This guide shows how to integrate the NinjaRMM MCP Server with Claude Desktop for seamless RMM operations directly from Claude.

## Prerequisites

1. **Claude Desktop** - Download from [Claude Desktop](https://claude.ai/download)
2. **Python 3.8+** with the NinjaRMM MCP Server installed
3. **NinjaRMM API credentials** (Client ID and Client Secret)

## Installation

### Option 1: Install from PyPI (Recommended)
```bash
pip install ninjamcp-python
```

### Option 2: Install from GitHub
```bash
pip install git+https://github.com/goetzcj/ninjamcp-python.git
```

## Configuration

### Step 1: Create Configuration File

1. Open Claude Desktop
2. Go to **Settings** → **Developer** → **Edit Config**
3. This opens `claude_desktop_config.json`

### Step 2: Add NinjaRMM MCP Server Configuration

Replace the contents with:

```json
{
  "mcpServers": {
    "ninjarmm": {
      "command": "ninjamcp-python",
      "env": {
        "NINJARMM_CLIENT_ID": "your_client_id_here",
        "NINJARMM_CLIENT_SECRET": "your_client_secret_here",
        "NINJARMM_BASE_URL": "https://app.ninjarmm.com",
        "NINJARMM_AUTH_MODE": "hybrid"
      }
    }
  }
}
```

### Step 3: Configure Your Credentials

Replace the placeholder values:

- **`your_client_id_here`**: Your NinjaRMM OAuth2 Client ID
- **`your_client_secret_here`**: Your NinjaRMM OAuth2 Client Secret
- **`https://app.ninjarmm.com`**: Your NinjaRMM instance URL (if different)

### Step 4: Restart Claude Desktop

Completely quit and restart Claude Desktop to load the new configuration.

## Verification

After restart, you should see an MCP server indicator (🔨) in the bottom-right corner of Claude's input box. Click it to verify the NinjaRMM tools are available.

## Available Tools

Once configured, Claude will have access to 26 comprehensive NinjaRMM tools:

### Device Management
- `get_devices` - List and filter devices
- `get_device_details` - Get detailed device information
- `get_device_count` - Efficient device counting

### Script & Automation
- `get_automation_scripts` - List available scripts
- `get_device_scripting_options` - Get device-specific scripts
- `run_script` - Execute scripts on devices

### Alert Management
- `get_alerts` - List system alerts
- `get_device_alerts` - Get device-specific alerts
- `reset_alert` - Reset alert conditions

### Activity Monitoring
- `get_activities` - Monitor device activities
- `track_script_execution` - Track script progress
- `monitor_device_activities` - Real-time activity monitoring

### Ticketing System
- `get_my_tickets` - Your assigned tickets
- `get_ticket_details` - Detailed ticket information
- `update_ticket_status` - Update ticket status
- `add_ticket_note` - Add notes to tickets

### Backup Management
- `get_backup_jobs` - Monitor backup operations

### Authentication
- `get_auth_status` - Check authentication status
- `reauthorize_user` - Refresh user authentication

## Advanced Configuration

### Custom Scopes
```json
{
  "mcpServers": {
    "ninjarmm": {
      "command": "ninjamcp-python",
      "env": {
        "NINJARMM_CLIENT_ID": "your_client_id",
        "NINJARMM_CLIENT_SECRET": "your_client_secret",
        "NINJARMM_CLIENT_SCOPES": "monitoring management control",
        "NINJARMM_USER_SCOPES": "monitoring management control",
        "NINJARMM_AUTH_MODE": "hybrid"
      }
    }
  }
}
```

### Client-Only Mode (No User Authentication)
```json
{
  "mcpServers": {
    "ninjarmm": {
      "command": "ninjamcp-python",
      "env": {
        "NINJARMM_CLIENT_ID": "your_client_id",
        "NINJARMM_CLIENT_SECRET": "your_client_secret",
        "NINJARMM_AUTH_MODE": "client"
      }
    }
  }
}
```

### Custom Token Storage
```json
{
  "mcpServers": {
    "ninjarmm": {
      "command": "ninjamcp-python",
      "env": {
        "NINJARMM_CLIENT_ID": "your_client_id",
        "NINJARMM_CLIENT_SECRET": "your_client_secret",
        "NINJARMM_TOKEN_STORAGE_PATH": "/path/to/custom/tokens.json"
      }
    }
  }
}
```

## Troubleshooting

### Server Not Appearing
1. Check Claude Desktop logs: `~/Library/Logs/Claude/mcp*.log` (macOS)
2. Verify credentials are correct
3. Ensure `ninjamcp-python` command is available: `which ninjamcp-python`
4. Try running manually: `ninjamcp-python` (should start the server)

### Authentication Issues
1. Verify your NinjaRMM API credentials
2. Check if your NinjaRMM instance URL is correct
3. Ensure your OAuth2 application has the required scopes

### Permission Errors
1. Make sure your NinjaRMM user has appropriate permissions
2. Check that your OAuth2 application is properly configured
3. Verify the client credentials have the necessary scopes

## Example Usage

Once configured, you can ask Claude things like:

- "Show me all offline devices"
- "Get the details for device ID 123"
- "Run a Windows update script on server-01"
- "What alerts are currently active?"
- "Show me my assigned tickets"
- "Get backup status for all servers"

Claude will use the NinjaRMM MCP Server to execute these requests and provide detailed responses with the actual data from your NinjaRMM instance.

## Security Notes

- Store credentials securely in the Claude Desktop configuration
- Use environment-specific credentials (dev/staging/prod)
- Regularly rotate your OAuth2 client credentials
- Monitor API usage through NinjaRMM's admin interface
- Consider using client-only mode for read-only operations

## Support

For issues with the MCP server:
- GitHub Issues: [ninjamcp-python issues](https://github.com/goetzcj/ninjamcp-python/issues)
- Documentation: [Project README](https://github.com/goetzcj/ninjamcp-python)

For Claude Desktop issues:
- Claude Support: [Claude Help Center](https://support.anthropic.com/)
