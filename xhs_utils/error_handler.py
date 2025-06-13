"""Enhanced error handling for XHS Spider"""
import json
from typing import Optional, Dict, Any, Tuple

try:
    from loguru import logger
except ImportError:
    # Fallback logger for testing without dependencies
    class FallbackLogger:
        def debug(self, msg): print(f"DEBUG: {msg}")
        def info(self, msg): print(f"INFO: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
    logger = FallbackLogger()


class XHSError(Exception):
    """Base exception for XHS Spider"""
    pass


class XHSAuthError(XHSError):
    """Authentication related errors"""
    pass


class XHSRateLimitError(XHSError):
    """Rate limiting errors"""
    pass


class XHSNotFoundError(XHSError):
    """Resource not found errors"""
    pass


class XHSAPIError(XHSError):
    """General API errors"""
    pass


def parse_response(response) -> Tuple[bool, str, Optional[Dict[Any, Any]]]:
    """Enhanced response parsing with proper error handling"""
    try:
        # Check HTTP status code first
        if response.status_code == 461:
            raise XHSRateLimitError(f"Rate limited (HTTP 461)")
        
        if response.status_code == 401:
            raise XHSAuthError(f"Authentication failed (HTTP 401)")
        
        if response.status_code == 403:
            raise XHSAuthError(f"Access forbidden (HTTP 403)")
        
        if response.status_code == 404:
            raise XHSNotFoundError(f"Resource not found (HTTP 404)")
        
        if response.status_code >= 500:
            raise XHSAPIError(f"Server error (HTTP {response.status_code})")
        
        if response.status_code != 200:
            raise XHSAPIError(f"HTTP error {response.status_code}: {response.text[:200]}")
        
        # Try to parse JSON
        try:
            res_json = response.json()
        except json.JSONDecodeError:
            raise XHSAPIError(f"Invalid JSON response: {response.text[:200]}")
        
        # Validate response structure
        if not isinstance(res_json, dict):
            raise XHSAPIError(f"Invalid response format: expected dict, got {type(res_json)}")
        
        # Check XHS API success flag
        if "success" not in res_json:
            raise XHSAPIError(f"Missing 'success' field in response: {res_json}")
        
        success = res_json["success"]
        msg = res_json.get("msg", "Unknown error")
        
        # Handle XHS-specific error codes
        if not success:
            if "登录" in msg or "login" in msg.lower():
                raise XHSAuthError(f"Authentication required: {msg}")
            elif "频繁" in msg or "rate" in msg.lower():
                raise XHSRateLimitError(f"Rate limited: {msg}")
            elif "不存在" in msg or "not found" in msg.lower():
                raise XHSNotFoundError(f"Resource not found: {msg}")
            else:
                raise XHSAPIError(f"API error: {msg}")
        
        return success, msg, res_json
        
    except (XHSError, json.JSONDecodeError) as e:
        # Re-raise our custom exceptions
        raise e
    except Exception as e:
        # Wrap other exceptions
        logger.error(f"Unexpected error parsing response: {e}")
        raise XHSAPIError(f"Unexpected error: {str(e)}")


def validate_cookies(cookies_str: str) -> bool:
    """Validate if cookies string contains required fields"""
    if not cookies_str:
        return False
    
    required_fields = ['a1', 'web_session']
    
    # Simple validation - check if required fields are present
    for field in required_fields:
        if field not in cookies_str:
            logger.warning(f"Missing required cookie field: {field}")
            return False
    
    return True


def log_request_details(method: str, url: str, headers: Dict[str, Any], data: Any = None):
    """Log request details for debugging"""
    logger.debug(f"Request: {method} {url}")
    logger.debug(f"Headers: {headers}")
    if data:
        logger.debug(f"Data: {data}")