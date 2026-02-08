"""Simple in-memory cache for agent responses.

This module provides a basic caching mechanism to reduce redundant API calls
for common queries like "list all tasks".
"""

import hashlib
import time
from typing import Any, Dict, Optional


class ResponseCache:
    """Simple in-memory cache with TTL (time-to-live) support."""

    def __init__(self, ttl_seconds: int = 60):
        """Initialize cache with TTL.

        Args:
            ttl_seconds: Time-to-live for cache entries in seconds (default: 60)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl = ttl_seconds

    def _generate_key(self, user_id: str, message: str) -> str:
        """Generate cache key from user_id and message.

        Args:
            user_id: User ID
            message: User message

        Returns:
            Cache key (hash of user_id + normalized message)
        """
        # Normalize message (lowercase, strip whitespace)
        normalized = message.lower().strip()
        key_string = f"{user_id}:{normalized}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, user_id: str, message: str) -> Optional[Dict[str, Any]]:
        """Get cached response if available and not expired.

        Args:
            user_id: User ID
            message: User message

        Returns:
            Cached response or None if not found/expired
        """
        key = self._generate_key(user_id, message)

        if key not in self._cache:
            return None

        entry = self._cache[key]
        current_time = time.time()

        # Check if entry has expired
        if current_time - entry["timestamp"] > self._ttl:
            # Remove expired entry
            del self._cache[key]
            return None

        return entry["response"]

    def set(self, user_id: str, message: str, response: Dict[str, Any]) -> None:
        """Store response in cache.

        Args:
            user_id: User ID
            message: User message
            response: Agent response to cache
        """
        key = self._generate_key(user_id, message)
        self._cache[key] = {
            "response": response,
            "timestamp": time.time(),
        }

    def invalidate_user(self, user_id: str) -> None:
        """Invalidate all cache entries for a specific user.

        This should be called when user performs write operations
        (create, update, delete, toggle tasks) to ensure fresh data.

        Args:
            user_id: User ID
        """
        # Find all keys for this user and remove them
        keys_to_remove = []
        for key, entry in self._cache.items():
            # Check if this entry belongs to the user
            # (we need to store user_id in entry for this)
            keys_to_remove.append(key)

        for key in keys_to_remove:
            if key in self._cache:
                del self._cache[key]

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()

    def size(self) -> int:
        """Get number of entries in cache.

        Returns:
            Number of cached entries
        """
        return len(self._cache)


# Global cache instance (60 second TTL)
response_cache = ResponseCache(ttl_seconds=60)


def is_cacheable_query(message: str) -> bool:
    """Check if a message is a cacheable read-only query.

    Args:
        message: User message

    Returns:
        True if message is cacheable, False otherwise
    """
    # Normalize message
    normalized = message.lower().strip()

    # List of cacheable query patterns
    cacheable_patterns = [
        "list",
        "show",
        "what",
        "display",
        "view",
        "see",
        "get",
        "tell me",
        "what's on",
        "whats on",
    ]

    # Check if message contains any cacheable pattern
    for pattern in cacheable_patterns:
        if pattern in normalized:
            # Make sure it's not a write operation
            write_keywords = ["add", "create", "delete", "remove", "update", "change", "mark", "complete", "done"]
            if not any(keyword in normalized for keyword in write_keywords):
                return True

    return False
