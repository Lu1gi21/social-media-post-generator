"""Main agent implementation for social media post generation.

This module implements a social media post generation agent using LangGraph for workflow management.
The agent handles research, content generation, formatting, and validation of social media posts
across different platforms while maintaining platform-specific requirements and best practices.

Typical usage:
    agent = SocialMediaAgent()
    post = agent.generate_post("Your topic", "twitter", tone="casual")

TODO:
- Implement proper error handling for OpenAI API calls
- Add retry mechanism for failed API calls
- Add support for custom templates per platform
- Implement proper logging throughout the class
- Add type hints for all method parameters and return values
"""

import os
import re
from typing import Any, Dict, List, TypedDict

from dotenv import load_dotenv
from langgraph.graph import Graph, StateGraph
from langgraph.prebuilt import ToolExecutor
from openai import OpenAI

from .config import Config
from .prompts import Prompts
from .researcher_agent import ResearcherAgent
from .web_search import WebSearchTool


class AgentState(TypedDict):
    """Type definition for the agent's state.

    Attributes:
        content: The original topic or content to be posted
        platform: The target social media platform
        tone: The desired tone of the post (e.g., casual, professional)
        researched_content: Content gathered from research phase
        generated_content: Initial content generated by the model
        formatted_content: Content after platform-specific formatting
        final_content: The final validated and ready-to-post content
    """

    content: str
    platform: str
    tone: str
    researched_content: str
    generated_content: str
    formatted_content: str
    final_content: str


class SocialMediaAgent:
    """Agent for generating platform-specific social media posts.

    This class implements a workflow-based approach to social media post generation,
    handling research, content creation, formatting, and validation in a structured manner.

    The agent uses LangGraph for workflow management and OpenAI's GPT models for content
    generation. It supports multiple social media platforms with platform-specific
    optimizations and constraints.
    """

    def __init__(self):
        """Initialize the social media agent.

        Sets up the OpenAI client, researcher agent, and workflow graph.
        Also initializes the emoji guide for Gen Z style optimization.
        """
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.researcher = ResearcherAgent()  # Single instance for all platforms
        self.graph = self._create_graph()

        # Cache the emoji guide for reuse across all content generation
        self.emoji_guide = Prompts.GENZ_EMOJI_GUIDE

    def _optimize_emoji_usage(self, content: str, platform: str) -> str:
        """Optimize emoji usage in the content based on platform and Gen Z style.

        This method uses GPT to analyze and enhance emoji usage in the content,
        ensuring it aligns with platform-specific best practices and Gen Z communication
        patterns.

        Args:
            content: The post content to optimize
            platform: The social media platform for which to optimize

        Returns:
            str: Content with optimized emoji usage, maintaining the original message
                while enhancing engagement through strategic emoji placement
        """
        # Skip optimization for platforms that don't support emojis
        if not Config.get_platform_config(platform).emoji_support:
            return content

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are a Gen Z emoji optimization expert. 
                Use this guide to optimize emoji usage in the content:
                {self.emoji_guide}
                
                Guidelines:
                1. Use emojis naturally and authentically
                2. Match the platform's vibe (e.g., more professional for LinkedIn)
                3. Don't overuse emojis
                4. Use combinations when appropriate
                5. Keep the original message intact""",
                },
                {
                    "role": "user",
                    "content": f"Optimize emoji usage in this content for {platform}:\n\n{content}",
                },
            ],
        )

        return response.choices[0].message.content

    def _create_graph(self) -> Graph:
        """Create the LangGraph workflow for post generation.

        This method sets up the workflow graph that defines the sequence of operations
        for post generation, including research, content generation, formatting, and
        validation steps.

        Returns:
            Graph: A compiled LangGraph workflow defining the post generation process
        """
        workflow = StateGraph(AgentState)

        # Add nodes for different stages of post generation
        workflow.add_node("research_topic", self._research_topic)
        workflow.add_node("generate_content", self._generate_content)
        workflow.add_node("format_post", self._format_post)
        workflow.add_node("validate_post", self._validate_post)

        # Define edges and flow between stages
        workflow.add_edge("research_topic", "generate_content")
        workflow.add_edge("generate_content", "format_post")
        workflow.add_edge("format_post", "validate_post")

        # Set entry and exit points for the workflow
        workflow.set_entry_point("research_topic")
        workflow.set_finish_point("validate_post")

        return workflow.compile()

    def _research_topic(self, state: AgentState) -> AgentState:
        """Research the topic to gather relevant information.

        This method performs comprehensive research on the given topic, focusing on
        current developments, key statistics, relevant context, and social media angles.
        The research results are then analyzed to identify the most engaging aspects
        for social media content.

        Args:
            state: Current state of the workflow containing the topic to research

        Returns:
            AgentState: Updated state containing the researched content and analysis
        """
        topic = state["content"]

        # Define focus areas for comprehensive research
        focus_areas = [
            "current developments",
            "key statistics",
            "relevant context",
            "social media angles",
        ]

        # Perform research using the researcher agent
        research_results = self.researcher.research_topic(topic, focus_areas)

        # Create a structured prompt for analyzing research results
        research_prompt = f"""Based on the following research about {topic}:

Summary:
{research_results['summary']}

Key Facts:
{research_results['key_facts']}

Current Trends:
{research_results['trends']}

Sources:
{research_results['sources']}

Please provide a comprehensive analysis focusing on:
1. Most relevant information for social media
2. Key insights and takeaways
3. Potential angles for engagement
4. Supporting data and statistics
5. Current context and relevance

Format the response in a clear, structured way that will help create engaging social media content."""

        # Generate analysis using GPT
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a social media content strategist specializing in analyzing research and identifying the most engaging aspects for social media posts.",
                },
                {"role": "user", "content": research_prompt},
            ],
        )

        state["researched_content"] = response.choices[0].message.content
        return state

    def _generate_content(self, state: AgentState) -> AgentState:
        """Generate the initial content for the post.

        This method creates the initial content for the social media post using the
        researched information and platform-specific requirements. It also handles
        emoji optimization for platforms that support it.

        Args:
            state: Current state containing the topic, platform, and researched content

        Returns:
            AgentState: Updated state containing the generated content
        """
        platform = state["platform"]
        topic = state["content"]
        researched_content = state["researched_content"]
        tone = state.get("tone", "neutral")

        # Combine topic and research for comprehensive context
        full_content = f"""Topic: {topic}

Research:
{researched_content}

Please create a social media post based on this information."""

        # Apply platform-specific prompt with emoji guidance
        system_prompt = f"""{Prompts.SYSTEM_PROMPTS[platform]}

Note: When using emojis:
- Use them naturally and authentically
- Match the platform's vibe
- Don't overuse them
- Use combinations when appropriate"""

        # Generate initial content
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": Prompts.get_user_prompt(full_content, platform, tone),
                },
            ],
        )

        # Optimize emoji usage if supported by the platform
        content = response.choices[0].message.content
        optimized_content = self._optimize_emoji_usage(content, platform)

        state["generated_content"] = optimized_content
        return state

    def _format_post(self, state: AgentState) -> AgentState:
        """Format the post according to platform requirements.

        This method applies platform-specific formatting rules, including hashtag
        generation and placement, while respecting platform constraints.

        Args:
            state: Current state containing the generated content and platform info

        Returns:
            AgentState: Updated state containing the formatted content
        """
        platform = state["platform"]
        content = state["generated_content"]
        config = Config.get_platform_config(platform)

        # Start with the generated content
        formatted_content = content

        # Add hashtags if the platform supports them
        if config.hashtag_limit > 0:
            hashtags = self._generate_hashtags(content, config.hashtag_limit)
            formatted_content += f"\n\n{' '.join(hashtags)}"

        state["formatted_content"] = formatted_content
        return state

    def _validate_post(self, state: AgentState) -> AgentState:
        """Validate the post against platform constraints.

        This method ensures the post meets all platform-specific requirements,
        including length limits, hashtag limits, and thread formatting for X/Twitter.

        Args:
            state: Current state containing the formatted content and platform info

        Returns:
            AgentState: Updated state containing the validated final content
        """
        platform = state["platform"]
        content = state["formatted_content"]
        config = Config.get_platform_config(platform)

        # Handle X/Twitter thread formatting
        if platform == "x":
            tweets = self._split_into_thread(content)
            content = "\n\n---\n\n".join(tweets)
        else:
            # Enforce length limits for other platforms
            if len(content) > config.max_length:
                content = content[: config.max_length - 3] + "..."

        # Validate and adjust hashtag count
        hashtags = [tag for tag in content.split() if tag.startswith("#")]
        if len(hashtags) > config.hashtag_limit:
            content = " ".join(content.split()[: -len(hashtags) + config.hashtag_limit])

        state["final_content"] = content
        return state

    def _split_into_thread(self, content: str) -> List[str]:
        """Split content into a thread of tweets for X/Twitter.

        This method splits long content into a thread of tweets while maintaining
        context and following X/Twitter's best practices. It handles:
        - Character limits (280 chars per tweet)
        - Thread context markers (🧵, 1/N, etc.)
        - Hashtag placement
        - Natural break points

        Args:
            content: The content to split into tweets

        Returns:
            List[str]: List of tweets forming the thread
        """
        # Constants
        MAX_TWEET_LENGTH = 280
        THREAD_MARKER = "🧵"
        HASHTAG_PATTERN = r"#\w+"

        # Extract hashtags from the content
        hashtags = re.findall(HASHTAG_PATTERN, content)
        content = re.sub(HASHTAG_PATTERN, "", content).strip()

        # Split content into sentences for natural breaks
        sentences = re.split(r"(?<=[.!?])\s+", content)

        tweets = []
        current_tweet = ""
        tweet_count = 0

        # Process each sentence
        for sentence in sentences:
            # Calculate potential tweet length with thread marker and counter
            potential_length = len(current_tweet) + len(sentence) + 1  # +1 for space
            counter_text = f" ({tweet_count + 1}/N)" if tweet_count > 0 else ""

            # If adding this sentence would exceed the limit
            if potential_length + len(counter_text) > MAX_TWEET_LENGTH:
                # Save current tweet if not empty
                if current_tweet:
                    tweet_count += 1
                    tweets.append(current_tweet.strip())

                # Start new tweet with this sentence
                current_tweet = sentence
            else:
                # Add sentence to current tweet
                current_tweet += " " + sentence if current_tweet else sentence

        # Add the last tweet if not empty
        if current_tweet:
            tweet_count += 1
            tweets.append(current_tweet.strip())

        # Add thread markers and counters
        for i, tweet in enumerate(tweets):
            # Add thread marker to first tweet
            if i == 0:
                tweet = f"{tweet} {THREAD_MARKER}"

            # Add counter to all tweets
            tweet = f"{tweet} ({i + 1}/{tweet_count})"

            # Add hashtags to last tweet if they fit
            if i == len(tweets) - 1 and hashtags:
                hashtag_text = " " + " ".join(hashtags)
                if len(tweet) + len(hashtag_text) <= MAX_TWEET_LENGTH:
                    tweet += hashtag_text

            tweets[i] = tweet

        return tweets

    def _generate_hashtags(self, content: str, limit: int) -> List[str]:
        """Generate relevant hashtags for the content.

        TODO:
        - Implement hashtag generation using GPT
        - Add support for trending hashtags
        - Add platform-specific hashtag rules
        - Implement hashtag analytics
        - Add support for custom hashtag sets

        Args:
            content: The post content to generate hashtags for
            limit: Maximum number of hashtags to generate

        Returns:
            List[str]: List of generated hashtags
        """
        # Implementation details...
        pass

    def generate_post(self, content: str, platform: str, tone: str = "neutral") -> str:
        """Generate a complete social media post.

        TODO:
        - Implement proper error handling
        - Add support for media attachments
        - Add support for post scheduling
        - Implement post analytics
        - Add support for A/B testing
        - Add support for post series

        Args:
            content: The topic or content to post about
            platform: The target social media platform
            tone: The desired tone of the post (default: "neutral")

        Returns:
            str: The final, validated post ready for publishing
        """
        # Implementation details...
        pass
