# NinjaRMM Device Filtering Guide

This guide explains how to use the enhanced device filtering capabilities in the NinjaRMM MCP Server.

## Overview

The `get_devices` and `get_devices_detailed` tools now support comprehensive filtering based on the official NinjaRMM API v2.0.5 Device Filter Syntax. You can filter devices by organization, location, device class, online status, creation date, and much more.

## Basic Usage

### Simple Filtering Examples

```python
# Get all online devices
get_devices(online_status="online")

# Get all Windows servers
get_devices(device_classes=["WINDOWS_SERVER"])

# Get devices pending approval
get_devices(approval_status="PENDING")

# Get devices created in 2024
get_devices(created_after="2024-01-01", created_before="2024-12-31")
```

### Advanced Filtering Examples

```python
# Get online Windows and Linux servers, excluding specific organizations
get_devices(
    online_status="online",
    device_classes=["WINDOWS_SERVER", "LINUX_SERVER"],
    exclude_organizations=[123, 456]
)

# Get devices in specific groups created after a certain date
get_devices(
    group_ids=[789, 101112],
    created_after="2024-06-01",
    approval_status="APPROVED"
)

# Get specific devices by ID
get_devices(device_ids=[1001, 1002, 1003])
```

## Filter Parameters

### Status Filters

- **`online_status`**: Filter by online/offline status
  - Values: `"online"`, `"offline"`
  - Example: `online_status="online"`

- **`approval_status`**: Filter by device approval status
  - Values: `"PENDING"`, `"APPROVED"`
  - Example: `approval_status="APPROVED"`

### Device Classification

- **`device_classes`**: Filter by device types
  - Values: Array of device class names
  - Available classes:
    - `WINDOWS_SERVER`, `WINDOWS_WORKSTATION`
    - `LINUX_SERVER`, `LINUX_WORKSTATION`
    - `MAC`, `MAC_SERVER`
    - `VMWARE_VM_HOST`, `VMWARE_VM_GUEST`
    - Network devices: `NMS_SWITCH`, `NMS_ROUTER`, `NMS_FIREWALL`
    - And many more (see full list in tool schema)
  - Example: `device_classes=["WINDOWS_SERVER", "LINUX_SERVER"]`

### Organizational Filters

- **`organization_ids`**: Include devices from specific organizations
  - Values: Array of organization IDs
  - Example: `organization_ids=[123, 456]`

- **`exclude_organizations`**: Exclude devices from specific organizations
  - Values: Array of organization IDs
  - Example: `exclude_organizations=[789]`

- **`location_ids`**: Include devices from specific locations
  - Values: Array of location IDs
  - Example: `location_ids=[101, 102]`

- **`exclude_locations`**: Exclude devices from specific locations
  - Values: Array of location IDs
  - Example: `exclude_locations=[103]`

### Role and Group Filters

- **`role_ids`**: Filter by device role IDs
  - Values: Array of role IDs
  - Example: `role_ids=[1, 2, 3]`

- **`exclude_roles`**: Exclude devices with specific roles
  - Values: Array of role IDs
  - Example: `exclude_roles=[4, 5]`

- **`group_ids`**: Filter by group membership
  - Values: Array of group IDs
  - Example: `group_ids=[789, 101112]`

### Date Filters

- **`created_after`**: Devices created after this date
  - Format: `YYYY-MM-DD`
  - Example: `created_after="2024-01-01"`

- **`created_before`**: Devices created before this date
  - Format: `YYYY-MM-DD`
  - Example: `created_before="2024-12-31"`

### Specific Device Selection

- **`device_ids`**: Filter by specific device IDs
  - Values: Array of device IDs
  - Example: `device_ids=[1001, 1002, 1003]`

## Advanced Usage

### Raw Filter Strings

For advanced users who want to write custom filter expressions, you can use the `device_filter` parameter with raw NinjaRMM filter syntax:

```python
# Raw filter string (bypasses all other filter parameters)
get_devices(device_filter="class=WINDOWS_SERVER AND online AND org!=123")

# Complex filter with date ranges
get_devices(device_filter="created after 2024-01-01 AND class in (WINDOWS_SERVER, LINUX_SERVER)")
```

### Combining Multiple Filters

All filter parameters are combined with AND logic:

```python
# This creates: online AND class=WINDOWS_SERVER AND org!=123
get_devices(
    online_status="online",
    device_classes=["WINDOWS_SERVER"],
    exclude_organizations=[123]
)
```

## Backward Compatibility

The enhanced filtering maintains full backward compatibility with existing usage:

```python
# Legacy usage still works
get_devices(organization_ids=[123], node_class_ids=[1, 2])

# New enhanced usage
get_devices(organization_ids=[123], device_classes=["WINDOWS_SERVER"])
```

## Error Handling

The filter builder includes validation:

- **Invalid device classes**: Raises `ValueError` with list of valid classes
- **Invalid date formats**: Raises `ValueError` for non-YYYY-MM-DD dates
- **Invalid status values**: Raises `ValueError` for invalid online/approval statuses

## Performance Tips

1. **Use specific filters**: More specific filters return results faster
2. **Combine filters**: Use multiple filter types to narrow results
3. **Use pagination**: Set appropriate `page_size` for large result sets
4. **Cache organization/location IDs**: Look up IDs once and reuse them

## Examples by Use Case

### IT Asset Management
```python
# Get all Windows workstations for inventory
get_devices(device_classes=["WINDOWS_WORKSTATION"], approval_status="APPROVED")

# Get all servers across multiple organizations
get_devices(
    device_classes=["WINDOWS_SERVER", "LINUX_SERVER"],
    organization_ids=[123, 456, 789]
)
```

### Security Monitoring
```python
# Get all offline devices for security check
get_devices(online_status="offline", approval_status="APPROVED")

# Get devices pending approval (potential security risk)
get_devices(approval_status="PENDING")
```

### Maintenance Planning
```python
# Get old devices (created before 2022) for replacement planning
get_devices(created_before="2022-01-01", online_status="online")

# Get devices in specific groups for maintenance
get_devices(group_ids=[100, 101], device_classes=["WINDOWS_SERVER"])
```

### Troubleshooting
```python
# Get specific problematic devices
get_devices(device_ids=[1001, 1002, 1003])

# Get devices in a specific location that are offline
get_devices(location_ids=[50], online_status="offline")
```
