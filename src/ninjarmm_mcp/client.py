"""NinjaRMM API client with authentication and error handling."""

import json
import logging
from typing import Optional, Dict, Any, Union, List
import httpx
from mcp.types import ErrorData

from .auth import AuthenticationManager

logger = logging.getLogger(__name__)


class NinjaRMMAPIError(Exception):
    """Custom exception for NinjaRMM API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class NinjaRMMClient:
    """HTTP client for NinjaRMM API v2 with authentication and error handling."""
    
    def __init__(self, auth_manager: AuthenticationManager):
        self.auth_manager = auth_manager
        self.base_url = auth_manager.base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/v2"
        
        # HTTP client configuration
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        self.limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)
    
    def _safe_json_stringify(self, obj: Any, max_depth: int = 10) -> str:
        """Safely stringify objects with circular reference handling."""
        def serialize_obj(o: Any, depth: int = 0) -> Any:
            if depth > max_depth:
                return "[Max depth reached]"
            
            if isinstance(o, (str, int, float, bool)) or o is None:
                return o
            elif isinstance(o, dict):
                return {k: serialize_obj(v, depth + 1) for k, v in o.items()}
            elif isinstance(o, (list, tuple)):
                return [serialize_obj(item, depth + 1) for item in o]
            else:
                return str(o)
        
        try:
            return json.dumps(serialize_obj(obj), indent=2)
        except Exception as e:
            logger.warning(f"Failed to stringify object: {e}")
            return str(obj)
    
    def _handle_api_error(self, response: httpx.Response, operation: str) -> None:
        """Handle API error responses."""
        try:
            error_data = response.json()
        except Exception:
            error_data = {"error": "Failed to parse error response"}
        
        status_code = response.status_code
        error_message = f"API request failed for {operation}"
        
        if isinstance(error_data, dict):
            if "error" in error_data:
                error_message = f"{operation}: {error_data['error']}"
            elif "message" in error_data:
                error_message = f"{operation}: {error_data['message']}"
        
        logger.error(f"API Error {status_code}: {error_message}")
        logger.debug(f"Error response: {self._safe_json_stringify(error_data)}")
        
        raise NinjaRMMAPIError(error_message, status_code, error_data)
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        operation: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make authenticated HTTP request to NinjaRMM API."""
        
        # Get authentication token
        try:
            access_token = await self.auth_manager.authenticate(operation)
        except Exception as e:
            logger.error(f"Authentication failed for {operation}: {e}")
            raise NinjaRMMAPIError(f"Authentication failed: {e}", None, None)
        
        # Prepare request
        url = f"{self.api_base}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "NinjaRMM-MCP-Server/1.4.1"
        }
        
        # Add content type for JSON requests
        if data and not files:
            headers["Content-Type"] = "application/json"
        
        logger.debug(f"Making {method} request to {url}")
        if params:
            logger.debug(f"Query params: {self._safe_json_stringify(params)}")
        if data:
            logger.debug(f"Request data: {self._safe_json_stringify(data)}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout, limits=self.limits) as client:
                if files:
                    # For file uploads, use files parameter
                    response = await client.request(
                        method=method,
                        url=url,
                        headers={k: v for k, v in headers.items() if k != "Content-Type"},
                        params=params,
                        data=data,
                        files=files
                    )
                else:
                    # For regular requests
                    json_data = data if data else None
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        params=params,
                        json=json_data
                    )
                
                logger.debug(f"Response status: {response.status_code}")
                
                # Handle non-success status codes
                if not response.is_success:
                    self._handle_api_error(response, operation)
                
                # Parse response
                try:
                    result = response.json()
                    logger.debug(f"Response data: {self._safe_json_stringify(result)}")
                    return result
                except Exception as e:
                    logger.warning(f"Failed to parse JSON response: {e}")
                    return {"raw_response": response.text}
                
        except httpx.TimeoutException:
            error_msg = f"Request timeout for {operation}"
            logger.error(error_msg)
            raise NinjaRMMAPIError(error_msg, None, None)
        except httpx.NetworkError as e:
            error_msg = f"Network error for {operation}: {e}"
            logger.error(error_msg)
            raise NinjaRMMAPIError(error_msg, None, None)
        except NinjaRMMAPIError:
            # Re-raise API errors as-is
            raise
        except Exception as e:
            error_msg = f"Unexpected error for {operation}: {e}"
            logger.error(error_msg)
            raise NinjaRMMAPIError(error_msg, None, None)
    
    async def get(self, endpoint: str, operation: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request."""
        return await self._make_request("GET", endpoint, operation, params=params)
    
    async def post(self, endpoint: str, operation: str, data: Optional[Dict[str, Any]] = None, 
                  files: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make POST request."""
        return await self._make_request("POST", endpoint, operation, data=data, files=files)
    
    async def put(self, endpoint: str, operation: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make PUT request."""
        return await self._make_request("PUT", endpoint, operation, data=data)
    
    async def patch(self, endpoint: str, operation: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make PATCH request."""
        return await self._make_request("PATCH", endpoint, operation, data=data)
    
    async def delete(self, endpoint: str, operation: str) -> Dict[str, Any]:
        """Make DELETE request."""
        return await self._make_request("DELETE", endpoint, operation)
