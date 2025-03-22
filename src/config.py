"""Configuration settings for the social media post generator.

This module provides configuration settings and platform-specific rules for
the social media post generator. It defines the constraints and capabilities
of each supported social media platform, including character limits, formatting
options, and content restrictions.

The configuration is implemented using Pydantic models for type safety and
validation of platform-specific settings.

TODO:
- Add support for more social media platforms
- Implement platform-specific validation rules
- Add support for custom platform configurations
- Implement platform-specific rate limiting
- Add support for platform-specific analytics
- Implement platform-specific error handling
"""

from typing import Dict, Any
from pydantic import BaseModel

class PlatformConfig(BaseModel):
    """Configuration for a specific social media platform.
    
    This class defines the configuration parameters for each social media
    platform, including content limits, supported features, and formatting
    rules. It uses Pydantic for data validation and type safety.
    
    Attributes:
        max_length: Maximum character length for posts
        hashtag_limit: Maximum number of hashtags allowed
        emoji_support: Whether the platform supports emojis
        link_support: Whether the platform supports clickable links
        formatting_rules: Dictionary of supported formatting options
    """
    max_length: int
    hashtag_limit: int
    emoji_support: bool
    link_support: bool
    formatting_rules: Dict[str, Any]

class Config:
    """Main configuration class for the social media post generator.
    
    TODO:
    - Add support for TikTok platform
    - Add support for Pinterest platform
    - Add support for Reddit platform
    - Implement platform-specific validation rules
    - Add support for custom platform configurations
    - Implement platform-specific rate limiting
    - Add support for platform-specific analytics
    
    The configuration is implemented as a class with static platform
    definitions to ensure consistent settings across the application.
    """
    
    # Platform-specific configurations with their respective constraints
    PLATFORMS = {
        "instagram": PlatformConfig(
            max_length=2200,  # Instagram's post length limit
            hashtag_limit=30,  # Instagram's hashtag limit
            emoji_support=True,
            link_support=False,  # Instagram doesn't support clickable links in posts
            formatting_rules={
                "line_breaks": True,
                "bold": False,
                "italic": False,
                "lists": False
            }
        ),
        "linkedin": PlatformConfig(
            max_length=3000,  # LinkedIn's post length limit
            hashtag_limit=5,  # LinkedIn's recommended hashtag limit
            emoji_support=True,
            link_support=True,
            formatting_rules={
                "line_breaks": True,
                "bold": True,
                "italic": True,
                "lists": True
            }
        ),
        "facebook": PlatformConfig(
            max_length=63206,  # Facebook's post length limit
            hashtag_limit=10,  # Facebook's recommended hashtag limit
            emoji_support=True,
            link_support=True,
            formatting_rules={
                "line_breaks": True,
                "bold": True,
                "italic": True,
                "lists": True
            }
        ),
        "x": PlatformConfig(
            max_length=280,  # X/Twitter's tweet length limit
            hashtag_limit=5,  # X/Twitter's recommended hashtag limit
            emoji_support=True,
            link_support=True,
            formatting_rules={
                "line_breaks": False,
                "bold": False,
                "italic": False,
                "lists": False
            }
        )
    }

    @classmethod
    def get_platform_config(cls, platform: str) -> PlatformConfig:
        """Get configuration for a specific platform.
        
        This method retrieves the configuration settings for a specified
        social media platform. It handles case-insensitive platform names
        and validates that the platform is supported.
        
        Args:
            platform: Name of the social media platform (case-insensitive)
            
        Returns:
            PlatformConfig: Configuration object for the specified platform
            
        Raises:
            ValueError: If the specified platform is not supported
            
        Example:
            >>> config = Config.get_platform_config("instagram")
            >>> print(config.max_length)
            2200
        """
        if platform.lower() not in cls.PLATFORMS:
            raise ValueError(f"Unsupported platform: {platform}")
        return cls.PLATFORMS[platform.lower()] 