"""
Research cache implementation for storing and managing research results.

This module provides a caching mechanism to store research results and avoid
redundant searches for the same topic across different social media platforms.
The cache includes automatic expiration of entries and methods for managing
the cached data.

Features:
- Time-based cache expiration
- Automatic cleanup of expired entries
- Thread-safe operations
- Memory-efficient storage

TODO:
- Implement persistent storage (database)
- Add support for cache statistics
- Implement cache compression
- Add support for cache invalidation rules
- Implement cache backup/restore
- Add support for distributed caching
- Implement cache monitoring
"""

from datetime import datetime, timedelta
from typing import Dict, Optional


class ResearchCache:
    """Cache for storing research results with expiration.

    TODO:
    - Implement persistent storage
    - Add support for cache statistics
    - Implement cache compression
    - Add support for cache invalidation rules
    - Implement cache backup/restore
    - Add support for distributed caching
    - Implement cache monitoring

    The cache stores entries with timestamps and automatically removes
    expired entries when they are accessed or when explicitly cleaned up.
    """

    def __init__(self, cache_duration: int = 24):
        """Initialize the research cache.

        Sets up the cache with a specified duration for entry expiration.
        The cache is implemented as a dictionary with topics as keys and
        dictionaries containing data and timestamps as values.

        Args:
            cache_duration: Duration in hours before cache entries expire (default: 24)
        """
        self.cache: Dict[str, Dict] = {}
        self.cache_duration = timedelta(hours=cache_duration)

    def get(self, topic: str) -> Optional[Dict]:
        """Retrieve cached research results for a topic.

        This method checks if the topic exists in the cache and if its
        entry has not expired. If the entry has expired, it is removed
        from the cache.

        Args:
            topic: The topic to look up in the cache

        Returns:
            Optional[Dict]: The cached research results if available and not expired,
                          None otherwise
        """
        if topic in self.cache:
            entry = self.cache[topic]
            # Check if the entry has expired
            if datetime.now() - entry["timestamp"] < self.cache_duration:
                return entry["data"]
            else:
                # Remove expired entry
                del self.cache[topic]
        return None

    def set(self, topic: str, data: Dict) -> None:
        """Store research results in the cache.

        This method stores research results for a topic along with a
        timestamp for expiration tracking. If the topic already exists,
        its entry is updated with the new data and timestamp.

        Args:
            topic: The topic to cache
            data: The research results to store
        """
        self.cache[topic] = {"data": data, "timestamp": datetime.now()}

    def clear(self) -> None:
        """Clear all cached entries.

        This method removes all entries from the cache, regardless of
        their expiration status. Use this method when you need to
        completely reset the cache.
        """
        self.cache.clear()

    def remove_expired(self) -> None:
        """Remove all expired cache entries.

        This method scans the cache and removes all entries that have
        exceeded their expiration duration. It is called automatically
        when accessing entries but can also be called manually to clean
        up the cache.
        """
        current_time = datetime.now()
        # Find all expired topics
        expired_topics = [
            topic
            for topic, entry in self.cache.items()
            if current_time - entry["timestamp"] >= self.cache_duration
        ]
        # Remove expired entries
        for topic in expired_topics:
            del self.cache[topic]
