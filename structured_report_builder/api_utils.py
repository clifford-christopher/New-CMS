"""
API Utility Module for handling retries and timeouts with data validation
"""

import requests
import time
from typing import Optional, Dict, Any, Callable

def validate_api_response(result: Dict, required_fields: Optional[list] = None, check_main_header: bool = True) -> bool:
    """
    Validate that API response contains actual data, not just success status

    Args:
        result: API response dictionary
        required_fields: Optional list of fields that must be present in 'data'
        check_main_header: Whether to check for main_header (default True)

    Returns:
        bool: True if response is valid with data, False otherwise
    """
    # Check if result exists and has success code (handle both string and int)
    code = str(result.get('code')) if result else None
    if not result or code != '200':
        return False

    # Check if data exists and is not empty
    data = result.get('data', {})
    if not data:
        print("[VALIDATION] Response has empty data object")
        return False

    # Only check for main_header if requested (for primary APIs like summary, company_cv)
    if check_main_header:
        # Check for main_header at minimum
        if 'main_header' not in data:
            print("[VALIDATION] Response missing main_header")
            return False

        # Validate main_header has some content
        main_header = data.get('main_header', {})
        if not main_header or not main_header.get('stock_name'):
            print("[VALIDATION] main_header is empty or missing stock_name")
            return False

    # Check specific required fields if provided
    if required_fields:
        for field in required_fields:
            if field not in data or not data[field]:
                print(f"[VALIDATION] Required field '{field}' is missing or empty")
                return False

    return True

class APIRetryHandler:
    """
    Handles API requests with automatic retry logic and exponential backoff
    """

    def __init__(self, max_retries: int = 5, timeout: int = 30):
        """
        Initialize retry handler with progressive delays

        Args:
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
        """
        self.max_retries = max_retries
        self.timeout = timeout
        # Progressive delays: 2s, 5s, 10s, 20s, 30s
        self.retry_delays = [2, 5, 10, 20, 30]

    def make_request(self, url: str, method: str = 'GET', headers: Optional[Dict] = None,
                    params: Optional[Dict] = None, json_data: Optional[Dict] = None,
                    description: str = "API", validate_func: Optional[Callable] = None,
                    required_fields: Optional[list] = None, check_main_header: bool = True) -> Optional[Dict[str, Any]]:
        """
        Make HTTP request with retry logic and data validation

        Args:
            url: API endpoint URL
            method: HTTP method (GET, POST, etc.)
            headers: Request headers
            params: Query parameters
            json_data: JSON payload for POST requests
            description: Description for logging
            validate_func: Optional custom validation function
            required_fields: Optional list of required fields in data
            check_main_header: Whether to check for main_header in response

        Returns:
            Response JSON or None if all retries failed
        """
        for attempt in range(self.max_retries):
            try:
                # Make the request
                if method.upper() == 'GET':
                    response = requests.get(url, headers=headers, params=params, timeout=self.timeout)
                elif method.upper() == 'POST':
                    response = requests.post(url, headers=headers, params=params, json=json_data, timeout=self.timeout)
                else:
                    response = requests.request(method, url, headers=headers, params=params, json=json_data, timeout=self.timeout)

                # Check if successful
                if response.status_code == 200:
                    result = response.json()

                    # Validate the response data
                    if validate_func:
                        # Use custom validation function
                        if validate_func(result):
                            print(f"[OK] {description} successful with valid data (attempt {attempt + 1}/{self.max_retries})")
                            return result
                        else:
                            print(f"[RETRY] {description} returned 200 but data validation failed (attempt {attempt + 1}/{self.max_retries})")
                    else:
                        # Use default validation
                        if validate_api_response(result, required_fields, check_main_header):
                            print(f"[OK] {description} successful with valid data (attempt {attempt + 1}/{self.max_retries})")
                            return result
                        else:
                            print(f"[RETRY] {description} returned 200 but data validation failed (attempt {attempt + 1}/{self.max_retries})")
                else:
                    print(f"[RETRY] {description} returned {response.status_code} (attempt {attempt + 1}/{self.max_retries})")

                    # Don't retry on 4xx errors (client errors)
                    if 400 <= response.status_code < 500:
                        print(f"[ERROR] {description} client error: {response.status_code}")
                        return None

            except requests.exceptions.Timeout:
                print(f"[TIMEOUT] {description} timed out (attempt {attempt + 1}/{self.max_retries})")
            except requests.exceptions.ConnectionError:
                print(f"[CONNECTION ERROR] {description} connection failed (attempt {attempt + 1}/{self.max_retries})")
            except requests.exceptions.RequestException as e:
                print(f"[ERROR] {description} request failed: {str(e)} (attempt {attempt + 1}/{self.max_retries})")
            except Exception as e:
                print(f"[ERROR] {description} unexpected error: {str(e)} (attempt {attempt + 1}/{self.max_retries})")

            # If not the last attempt, wait before retrying
            if attempt < self.max_retries - 1:
                # Use progressive delays from the list
                wait_time = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
                print(f"[WAITING] Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

        print(f"[FAILED] {description} failed after {self.max_retries} attempts")
        return None

    def make_request_with_fallback(self, primary_url: str, fallback_url: Optional[str] = None,
                                  method: str = 'GET', headers: Optional[Dict] = None,
                                  params: Optional[Dict] = None, json_data: Optional[Dict] = None,
                                  description: str = "API") -> Optional[Dict[str, Any]]:
        """
        Make request with fallback URL if primary fails

        Args:
            primary_url: Primary API endpoint
            fallback_url: Fallback API endpoint
            method: HTTP method
            headers: Request headers
            params: Query parameters
            json_data: JSON payload
            description: Description for logging

        Returns:
            Response JSON or None if both URLs failed
        """
        # Try primary URL
        result = self.make_request(primary_url, method, headers, params, json_data, f"{description} (primary)")

        if result is not None:
            return result

        # Try fallback URL if provided
        if fallback_url:
            print(f"[INFO] Trying fallback URL for {description}")
            result = self.make_request(fallback_url, method, headers, params, json_data, f"{description} (fallback)")

        return result


# Global instance for convenience
default_retry_handler = APIRetryHandler()

def fetch_with_retry(url: str, headers: Optional[Dict] = None, params: Optional[Dict] = None,
                    description: str = "API", max_retries: int = 5,
                    timeout: int = 30) -> Optional[Dict[str, Any]]:
    """
    Convenience function for making GET requests with retry logic

    Args:
        url: API endpoint URL
        headers: Request headers
        params: Query parameters
        description: Description for logging
        max_retries: Maximum retry attempts
        timeout: Request timeout

    Returns:
        Response JSON or None if failed
    """
    handler = APIRetryHandler(max_retries=max_retries, timeout=timeout)
    return handler.make_request(url, 'GET', headers, params, None, description)

def post_with_retry(url: str, json_data: Optional[Dict] = None, headers: Optional[Dict] = None,
                   params: Optional[Dict] = None, description: str = "API",
                   max_retries: int = 5, timeout: int = 30,
                   validate_func: Optional[Callable] = None,
                   required_fields: Optional[list] = None,
                   check_main_header: bool = True) -> Optional[Dict[str, Any]]:
    """
    Convenience function for making POST requests with retry logic and validation

    Args:
        url: API endpoint URL
        json_data: JSON payload
        headers: Request headers
        params: Query parameters
        description: Description for logging
        max_retries: Maximum retry attempts
        timeout: Request timeout
        validate_func: Optional custom validation function
        required_fields: Optional list of required fields in data
        check_main_header: Whether to check for main_header in response

    Returns:
        Response JSON or None if failed
    """
    handler = APIRetryHandler(max_retries=max_retries, timeout=timeout)
    return handler.make_request(url, 'POST', headers, params, json_data, description, validate_func, required_fields, check_main_header)