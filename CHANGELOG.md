# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.3] - 2025-10-14

### Added
- **New Device-Specific Tools**: Added two new tools for enhanced device management
  - `get_device_scripting_options` - Retrieves available built-in actions and custom scripts for a specific device
  - `get_device_alerts` - Retrieves active alerts (triggered conditions) for a specific device
  - Both tools support optional language and timezone parameters
  - Integrated into existing ScriptTools and AlertTools collections

### Technical Details
- Added `GetDeviceScriptingOptionsTool` to `src/ninjarmm_mcp/tools/scripts.py`
- Added `GetDeviceAlertsTool` to `src/ninjarmm_mcp/tools/alerts.py`
- Tools follow established patterns with proper error handling and parameter validation
- Based on NinjaRMM API v2 endpoints:
  - `GET /v2/device/{id}/scripting/options`
  - `GET /v2/device/{id}/alerts`

## [1.4.2] - 2025-10-10

### Fixed
- **URL Protocol Validation**: Fixed "Request URL is missing an 'http://' or 'https://' protocol" error
  - Added automatic protocol normalization for `NINJARMM_BASE_URL` environment variable
  - Empty or whitespace-only URLs default to `https://app.ninjarmm.com`
  - URLs without protocol automatically get `https://` prefix
  - Case-insensitive protocol detection preserves original URL format
  - Handles edge cases: localhost, IP addresses, URLs with paths

### Technical Details
- Added `_normalize_base_url()` method to `NinjaRMMServer` class
- Validates and normalizes base URL during server initialization
- Prevents HTTP client errors when users set invalid base URLs
- Maintains backward compatibility with properly formatted URLs

## [1.4.1] - 2025-10-10

### Fixed
- **CRITICAL**: Fixed "BaseModel.__init__() takes 1 positional argument but 3 were given" error
  - Incorrect usage of `JSONRPCError` from MCP library causing tool execution failures
  - Replaced improper positional arguments with correct keyword arguments
  - All tools now properly handle errors and return expected error messages
  - Affects all API operations when authentication or network errors occur

### Technical Details
- Updated `client.py` to use `NinjaRMMAPIError` instead of incorrectly constructed `JSONRPCError`
- Updated `server.py` to use standard Python exceptions for tool execution errors
- Removed incorrect imports of `INTERNAL_ERROR` and `METHOD_NOT_FOUND` constants
- Proper error propagation now shows meaningful authentication and API error messages

## [1.4.0] - 2025-10-10

### Added
- **Credential Management System Integration**: Enterprise-grade token injection capability
  - Environment variable injection: Automatically detect tokens from `NINJARMM_*_ACCESS_TOKEN` environment variables
  - Programmatic injection: `inject_tokens()` method for external credential management systems
  - Server-level injection: Direct token injection via `NinjaRMMServer.inject_tokens()`
  - Backward compatibility: Falls back to standard OAuth2 flows if no tokens are injected
  - Token refresh support: Automatic refresh using injected refresh tokens

### Enhanced
- **Authentication Manager**: New methods for token injection and credential management integration
  - `inject_client_token()`: Inject client credentials tokens
  - `inject_user_token()`: Inject user authorization tokens
  - `inject_tokens_from_dict()`: Bulk token injection from dictionary
- **Documentation**: Comprehensive credential management integration guide and examples
- **Examples**: Complete example script demonstrating integration patterns

### Use Cases
- **Enterprise Environments**: Centralized credential management without browser-based OAuth2
- **Production Deployments**: Pre-authenticated tokens from secure credential stores
- **CI/CD Pipelines**: Automated authentication using stored credentials
- **Multi-tenant Systems**: Isolated credential management per tenant

## [1.3.1] - 2025-10-04

### Fixed
- **CRITICAL**: Fixed MCP protocol compliance bug where `notification_options=None` was passed to `get_capabilities()`
  - The MCP server was trying to access `notification_options.tools_changed` but `notification_options` was `None`
  - Now properly creates `NotificationOptions` with `tools_changed=True`, `prompts_changed=True`, `resources_changed=True`
  - This resolves compatibility issues with current MCP library versions
  - Fixes server initialization failures in MCP client applications

### Technical Details
- Added import for `NotificationOptions` from `mcp.server`
- Updated `get_capabilities()` call in server initialization to use proper `NotificationOptions` object
- Changed `experimental_capabilities` from `None` to `{}` for consistency

## [1.3.0] - 2025-10-04

### Added
- **Efficient Counting Tools**: New tools for scalable device counting
  - `get_device_count`: Count total devices without transferring full device data (99.9% less data transfer)
  - `get_device_count_by_organization`: Count devices grouped by organization
- **Enhanced Device Filtering**: Complete NinjaRMM API v2.0.5 Device Filter Syntax support
  - 19 new filtering parameters for precise device selection
  - Support for organization, location, role, device class, approval status, online status filtering
  - Date range filtering and group membership filtering
  - Backward compatibility with existing parameters

### Improved
- **Package Structure**: Clean, production-ready codebase
  - Comprehensive `.gitignore` for security and package cleanliness
  - Modern `pyproject.toml` configuration without deprecation warnings
  - `MANIFEST.in` for proper package distribution control
  - Enhanced documentation with filtering guide

### Technical
- **24 comprehensive tools** across 8 categories
- **DeviceFilterBuilder utility** for constructing complex filters
- **Comprehensive test suite** with 23 device filter tests
- **Security best practices** with no hardcoded credentials

## [1.2.0] - 2025-10-03

### Added
- Complete Python port of Node.js MCP server
- OAuth2 authentication with hybrid mode support
- 22 comprehensive tools across 6 categories:
  - Device Management (4 tools)
  - Activity Monitoring (4 tools) 
  - Alert Management (2 tools)
  - Backup Management (1 tool)
  - Script Management (2 tools)
  - Ticketing System (6 tools)
  - Authentication Management (3 tools)

### Features
- **Robust Authentication**: Client credentials and user authorization flows
- **Comprehensive API Coverage**: Full NinjaRMM API v2 integration
- **Modern Python Packaging**: pip-installable with proper dependencies
- **Complete Documentation**: Setup guides and usage examples

## [1.0.0] - Initial Release

### Added
- Basic MCP server framework
- Initial NinjaRMM API integration
- Core authentication system
