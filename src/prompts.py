"""System and user prompts for the social media post generator."""

from typing import Dict

class Prompts:
    """Collection of prompts for different social media platforms."""
    
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
  * Clear thread flow"""
    }

    @staticmethod
    def get_user_prompt(content: str, platform: str, tone: str = "neutral") -> str:
        """Generate a user prompt for the given content and platform."""
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