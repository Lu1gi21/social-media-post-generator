"""
Research cache implementation for storing and managing research results.

This module provides a caching mechanism to store research results and avoid
redundant searches for the same topic across different social media platforms.
"""

from typing import Dict, Optional
from datetime import datetime, timedelta

class ResearchCache:
    """Cache for storing research results with expiration."""
    
    def __init__(self, cache_duration: int = 24):
        """
        Initialize the research cache.
        
        Args:
            cache_duration (int): Duration in hours before cache entries expire
        """
        self.cache: Dict[str, Dict] = {}
        self.cache_duration = timedelta(hours=cache_duration)
    
    def get(self, topic: str) -> Optional[Dict]:
        """
        Retrieve cached research results for a topic.
        
        Args:
            topic (str): The topic to look up
            
        Returns:
            Optional[Dict]: Cached research results if available and not expired
        """
        if topic in self.cache:
            entry = self.cache[topic]
            if datetime.now() - entry['timestamp'] < self.cache_duration:
                return entry['data']
            else:
                del self.cache[topic]
        return None
    
    def set(self, topic: str, data: Dict) -> None:
        """
        Store research results in the cache.
        
        Args:
            topic (str): The topic to cache
            data (Dict): The research results to store
        """
        self.cache[topic] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    def clear(self) -> None:
        """Clear all cached entries."""
        self.cache.clear()
    
    def remove_expired(self) -> None:
        """Remove all expired cache entries."""
        current_time = datetime.now()
        expired_topics = [
            topic for topic, entry in self.cache.items()
            if current_time - entry['timestamp'] >= self.cache_duration
        ]
        for topic in expired_topics:
            del self.cache[topic] 