"""Configuration settings for the social media post generator."""

from typing import Dict, Any
from pydantic import BaseModel

class PlatformConfig(BaseModel):
    """Configuration for a specific social media platform."""
    max_length: int
    hashtag_limit: int
    emoji_support: bool
    link_support: bool
    formatting_rules: Dict[str, Any]

class Config:
    """Main configuration class for the social media post generator."""
    
    PLATFORMS = {
        "instagram": PlatformConfig(
            max_length=2200,
            hashtag_limit=30,
            emoji_support=True,
            link_support=False,
            formatting_rules={
                "line_breaks": True,
                "bold": False,
                "italic": False,
                "lists": False
            }
        ),
        "linkedin": PlatformConfig(
            max_length=3000,
            hashtag_limit=5,
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
            max_length=63206,
            hashtag_limit=10,
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
            max_length=280,
            hashtag_limit=5,
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
        
        Args:
            platform: Name of the social media platform
            
        Returns:
            PlatformConfig object for the specified platform
            
        Raises:
            ValueError: If platform is not supported
        """
        if platform.lower() not in cls.PLATFORMS:
            raise ValueError(f"Unsupported platform: {platform}")
        return cls.PLATFORMS[platform.lower()] 