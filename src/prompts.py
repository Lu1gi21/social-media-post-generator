"""System and user prompts for the social media post generator.

This module contains a collection of prompts and formatting guidelines used by the
social media post generator to create platform-specific content. It includes system
prompts for different platforms, emoji guides, and user prompt templates.

The prompts are designed to ensure consistent, engaging, and platform-appropriate
content generation across different social media platforms.
"""

from typing import Dict


class Prompts:
    """Collection of prompts for different social media platforms.

    This class provides a centralized repository of prompts and formatting guidelines
    for generating social media content across different platforms. It includes:
    - Platform-specific system prompts
    - Emoji usage guidelines
    - User prompt templates
    """

    # Comprehensive guide for Gen Z emoji usage across platforms
    GENZ_EMOJI_GUIDE = """
    Emotions & Reactions:
    🫡 - Saluting, respect
    🫣 - Peeking, sneaky
    🫢 - Shocked, surprised
    🫥 - Invisible, done
    🫤 - Annoyed, whatever
    🫶 - Love, thanks
    
    Status & Mood:
    💅 - Confidence, sass
    💀 - Dying laughing
    💯 - 100% agree
    🔥 - Amazing, on fire
    🎯 - On point
    🫂 - Support
    🫰 - Money
    
    Reactions:
    😭 - Intense emotion
    😮‍💨 - Exhausted
    🥲 - Happy but sad
    🥹 - Emotional
    
    Common combos:
    💀😭 - Dying laughing
    💅✨ - Best life
    🫡💯 - Respect
    🫣😮‍💨 - Can't believe it
    """

    # Platform-specific system prompts with formatting guidelines
    SYSTEM_PROMPTS = {
        "instagram": """Format:
- Max 30 hashtags
- Line breaks for readability
- Structure:
  * Engaging opening
  * Clear paragraphs
  * Bullet points when needed
  * Strong call-to-action
  * Hashtags on new line
- Style:
  * Natural, conversational tone
  * Relatable content
  * Current references
  * Strategic emojis
  * Authentic voice""",
        "linkedin": """Format:
- Max 5 hashtags
- Rich formatting
- Structure:
  * Attention-grabbing headline
  * Formatted paragraphs
  * Key point lists
  * Professional call-to-action
  * End hashtags
- Style:
  * Professional insights
  * Industry expertise
  * Thoughtful analysis
  * Current trends
  * Strategic emojis""",
        "facebook": """Format:
- Max 10 hashtags
- Rich formatting
- Structure:
  * Engaging opening
  * Clear paragraphs
  * Visual breaks
  * Interactive elements
  * End hashtags
- Style:
  * Social insights
  * Personal experiences
  * Current events
  * Authentic voice
  * Strategic emojis""",
        "x": """Format:
- Max 5 hashtags
- 280 char limit per tweet
- Thread structure:
  * First tweet: Hook + "🧵"
  * Middle tweets: Key points
  * Last tweet: Call-to-action + hashtags
- Style:
  * Current topics
  * Concise insights
  * Modern language
  * Relatable content
  * Strategic emojis
  * Clear thread flow""",
    }

    @staticmethod
    def get_user_prompt(content: str, platform: str, tone: str = "neutral") -> str:
        """Generate a user prompt for the given content and platform.

        This method creates a structured prompt that guides the content generation
        process while maintaining platform-specific requirements and desired tone.

        Args:
            content: The main content or topic to be posted
            platform: The target social media platform
            tone: The desired tone of the post (default: "neutral")

        Returns:
            str: A formatted prompt that includes content, platform requirements,
                and generation guidelines
        """
        return f"""Create {tone} tone {platform} post with:
{content}

Format:
1. Platform best practices
2. Clear structure
3. Supported formatting
4. Platform hashtag limits
5. Consistent tone
6. Strong open/close
7. Strategic emojis
8. Readable format
9. Natural language
10. Relatable content
11. Current topics
12. Authentic voice"""
