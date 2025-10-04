# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
