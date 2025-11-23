import time
from collections import deque
from threading import Lock
from typing import Deque

class RateLimiter:
    """
    Thread-safe rate limiter using a sliding window algorithm.
    """
    
    def __init__(self, max_calls: int, time_window: float):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum number of allowed calls within the time window.
            time_window: Time window in seconds.
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls: Deque[float] = deque()
        self.lock = Lock()
    
    def is_allowed(self) -> bool:
        """
        Check if an operation is allowed under the current rate limit.
        Records the call if allowed.
        
        Returns:
            True if allowed, False otherwise.
        """
        with self.lock:
            now = time.time()
            
            # Remove old calls outside the time window
            while self.calls and self.calls[0] < now - self.time_window:
                self.calls.popleft()
            
            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True
            
            return False
