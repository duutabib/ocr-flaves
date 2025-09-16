import time
import logging
from typing import Callable, Any, Optional, TypeVar, Type, Tuple, List, Dict
from dataclasses import dataclass
from enum import Enum
from functools import wraps

# Type variable for generic function typing
T = TypeVar('T')

# Configure logger
logger = logging.getLogger(__name__)



class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: int = 60
    expected_exception: type = Exception


class CircuitBreaker:
    """Circuit breaker pattern for external service calls"""

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self.logger = logging.getLogger(__name__) 
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.config.recovery_timeout
        )
    
    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.logger.info("Circuit breaker reset to CLOSED")
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            self.logger.warning(f"Circuit breaker OPEN after {self.failure_count} failures")


def retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    logger: Optional[logging.Logger] = None
):
    """Decorator factory for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff
        max_delay: Maximum delay between retries in seconds
        exceptions: Tuple of exceptions to catch and retry on
        logger: Optional logger instance for logging retries
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            return RetryStrategy.with_exponential_backoff(
                lambda: func(*args, **kwargs),
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                exceptions=exceptions,
                logger=logger
            )
        return wrapper
    return decorator


class RetryStrategy:
    """Strategies for handling retries with various backoff mechanisms"""
    @staticmethod
    def with_exponential_backoff(
        func: Callable[..., T],
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exceptions: Tuple[Type[Exception], ...] = (Exception,),
        logger: Optional[logging.Logger] = None
    ) -> T:
        """Execute function with exponential backoff retry.
        
        Args:
            func: The function to execute
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds for exponential backoff
            max_delay: Maximum delay between retries in seconds
            exceptions: Tuple of exceptions to catch and retry on
            logger: Optional logger instance for logging retries
            
        Returns:
            The result of the function call if successful
            
        Raises:
            Exception: The last exception if all retries are exhausted
        """
        log = logger or logging.getLogger(__name__)
        last_exception = None

        for attempt in range(max_retries):
            try:
                return func()
            except exceptions as e:
                last_exception = e
                if attempt < max_retries - 1:
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    log.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)
                else:
                    log.error(f"All {max_retries} attempts failed. Last error: {str(e)}")
                    raise

        # This line should theoretically never be reached due to the raise in the except block
        raise last_exception or Exception("Unknown error in with_exponential_backoff")