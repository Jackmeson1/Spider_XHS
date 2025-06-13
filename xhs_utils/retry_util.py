"""Retry utilities with exponential backoff and better error handling"""
import time
import random
from typing import Callable, Any, Tuple
from functools import wraps
from loguru import logger
from .error_handler import XHSRateLimitError, XHSAuthError


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True
):
    """
    Decorator for retrying functions with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        backoff_factor: Multiplier for delay on each retry
        jitter: Add random jitter to avoid thundering herd
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    # If function returns (success, msg, data) tuple
                    if isinstance(result, tuple) and len(result) == 3:
                        success, msg, data = result
                        if success:
                            return result
                        else:
                            # If it's an auth error, don't retry
                            if "login" in msg.lower() or "authentication" in msg.lower():
                                logger.error(f"Authentication error, not retrying: {msg}")
                                return result
                            # If it's rate limiting, use longer delay
                            if "rate" in msg.lower() or "频繁" in msg:
                                if attempt < max_retries:
                                    delay = min(base_delay * (backoff_factor ** attempt) * 2, max_delay)
                                    logger.warning(f"Rate limited, waiting {delay:.1f}s before retry {attempt + 1}/{max_retries}")
                                    time.sleep(delay)
                                    continue
                            # For other errors, use normal backoff
                            raise Exception(msg)
                    else:
                        return result
                        
                except XHSAuthError as e:
                    logger.error(f"Authentication error, not retrying: {e}")
                    return False, str(e), None
                    
                except XHSRateLimitError as e:
                    if attempt < max_retries:
                        delay = min(base_delay * (backoff_factor ** attempt) * 2, max_delay)
                        if jitter:
                            delay *= (0.5 + random.random() * 0.5)
                        logger.warning(f"Rate limited, waiting {delay:.1f}s before retry {attempt + 1}/{max_retries}: {e}")
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(f"Max retries exceeded for rate limiting: {e}")
                        return False, str(e), None
                        
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                        if jitter:
                            delay *= (0.5 + random.random() * 0.5)
                        logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay:.1f}s: {e}")
                        time.sleep(delay)
                    else:
                        logger.error(f"Max retries exceeded: {e}")
                        
            return False, str(last_exception), None
            
        return wrapper
    return decorator


def smart_delay(last_request_time: float, min_interval: float = 2.0) -> None:
    """
    Add intelligent delay between requests to avoid rate limiting
    
    Args:
        last_request_time: Timestamp of last request
        min_interval: Minimum interval between requests in seconds
    """
    if last_request_time > 0:
        elapsed = time.time() - last_request_time
        if elapsed < min_interval:
            delay = min_interval - elapsed + random.uniform(0.1, 0.5)
            logger.debug(f"Adding delay of {delay:.1f}s to avoid rate limiting")
            time.sleep(delay)