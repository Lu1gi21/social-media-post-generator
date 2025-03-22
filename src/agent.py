"""Main agent implementation for social media post generation."""

import os
from typing import Dict, Any, List, TypedDict
from dotenv import load_dotenv
from langgraph.graph import Graph, StateGraph
from langgraph.prebuilt import ToolExecutor
from openai import OpenAI

from .config import Config
from .prompts import Prompts
from .web_search import WebSearchTool
from .researcher_agent import ResearcherAgent

class AgentState(TypedDict):
    """Type definition for the agent's state."""
    content: str
    platform: str
    tone: str
    researched_content: str
    generated_content: str
    formatted_content: str
    final_content: str

class SocialMediaAgent:
    """Agent for generating platform-specific social media posts."""
    
    def __init__(self):
        """Initialize the social media agent."""
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.researcher = ResearcherAgent()  # Single instance for all platforms
        self.graph = self._create_graph()
        
        # Cache the emoji guide for reuse
        self.emoji_guide = Prompts.GENZ_EMOJI_GUIDE
        
    def _optimize_emoji_usage(self, content: str, platform: str) -> str:
        """Optimize emoji usage in the content based on platform and Gen Z style.
        
        Args:
            content: The post content
            platform: The social media platform
            
        Returns:
            Content with optimized emoji usage
        """
        # Only optimize if the platform supports emojis
        if not Config.get_platform_config(platform).emoji_support:
            return content
            
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"""You are a Gen Z emoji optimization expert. 
                Use this guide to optimize emoji usage in the content:
                {self.emoji_guide}
                
                Guidelines:
                1. Use emojis naturally and authentically
                2. Match the platform's vibe (e.g., more professional for LinkedIn)
                3. Don't overuse emojis
                4. Use combinations when appropriate
                5. Keep the original message intact"""},
                {"role": "user", "content": f"Optimize emoji usage in this content for {platform}:\n\n{content}"}
            ]
        )
        
        return response.choices[0].message.content
        
    def _create_graph(self) -> Graph:
        """Create the LangGraph workflow for post generation.
        
        Returns:
            Graph object representing the workflow
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes for different stages of post generation
        workflow.add_node("research_topic", self._research_topic)
        workflow.add_node("generate_content", self._generate_content)
        workflow.add_node("format_post", self._format_post)
        workflow.add_node("validate_post", self._validate_post)
        
        # Define edges and flow
        workflow.add_edge("research_topic", "generate_content")
        workflow.add_edge("generate_content", "format_post")
        workflow.add_edge("format_post", "validate_post")
        
        # Set entry and exit points
        workflow.set_entry_point("research_topic")
        workflow.set_finish_point("validate_post")
        
        return workflow.compile()
    
    def _research_topic(self, state: AgentState) -> AgentState:
        """Research the topic to gather relevant information.
        
        Args:
            state: Current state of the workflow
            
        Returns:
            Updated state with researched content
        """
        topic = state["content"]
        
        # Perform research with focus areas
        focus_areas = [
            "current developments",
            "key statistics",
            "relevant context",
            "social media angles"
        ]
        
        research_results = self.researcher.research_topic(topic, focus_areas)
        
        # Format research results for content generation
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

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a social media content strategist specializing in analyzing research and identifying the most engaging aspects for social media posts."},
                {"role": "user", "content": research_prompt}
            ]
        )
        
        state["researched_content"] = response.choices[0].message.content
        return state
    
    def _generate_content(self, state: AgentState) -> AgentState:
        """Generate the initial content for the post.
        
        Args:
            state: Current state of the workflow
            
        Returns:
            Updated state with generated content
        """
        platform = state["platform"]
        topic = state["content"]
        researched_content = state["researched_content"]
        tone = state.get("tone", "neutral")
        
        # Combine topic and researched content for better context
        full_content = f"""Topic: {topic}

Research:
{researched_content}

Please create a social media post based on this information."""
        
        # Use platform-specific prompt with basic emoji guidance
        system_prompt = f"""{Prompts.SYSTEM_PROMPTS[platform]}

Note: When using emojis:
- Use them naturally and authentically
- Match the platform's vibe
- Don't overuse them
- Use combinations when appropriate"""
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": Prompts.get_user_prompt(full_content, platform, tone)}
            ]
        )
        
        # Optimize emoji usage after initial content generation
        content = response.choices[0].message.content
        optimized_content = self._optimize_emoji_usage(content, platform)
        
        state["generated_content"] = optimized_content
        return state
    
    def _format_post(self, state: AgentState) -> AgentState:
        """Format the post according to platform requirements.
        
        Args:
            state: Current state of the workflow
            
        Returns:
            Updated state with formatted content
        """
        platform = state["platform"]
        content = state["generated_content"]
        config = Config.get_platform_config(platform)
        
        # Apply platform-specific formatting
        formatted_content = content
        
        # Add hashtags if needed
        if config.hashtag_limit > 0:
            hashtags = self._generate_hashtags(content, config.hashtag_limit)
            formatted_content += f"\n\n{' '.join(hashtags)}"
        
        state["formatted_content"] = formatted_content
        return state
    
    def _validate_post(self, state: AgentState) -> AgentState:
        """Validate the post against platform constraints.
        
        Args:
            state: Current state of the workflow
            
        Returns:
            Updated state with validation results
        """
        platform = state["platform"]
        content = state["formatted_content"]
        config = Config.get_platform_config(platform)
        
        # Special handling for X/Twitter threads
        if platform == "x":
            # Split content into tweets
            tweets = self._split_into_thread(content)
            content = "\n\n---\n\n".join(tweets)
        else:
            # Check length for other platforms
            if len(content) > config.max_length:
                content = content[:config.max_length-3] + "..."
            
        # Validate hashtags
        hashtags = [tag for tag in content.split() if tag.startswith("#")]
        if len(hashtags) > config.hashtag_limit:
            # Remove excess hashtags
            content = " ".join(content.split()[:-len(hashtags)+config.hashtag_limit])
            
        state["final_content"] = content
        return state
    
    def _split_into_thread(self, content: str) -> List[str]:
        """Split content into a thread of tweets.
        
        Args:
            content: The full content to split into tweets
            
        Returns:
            List of tweets in the thread
        """
        # Generate thread structure
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """You are a Twitter thread expert. Split the content into a thread following these rules:
1. First tweet: Hook + "🧵"
2. Middle tweets: Key points (max 280 chars each)
3. Last tweet: Call-to-action + hashtags
4. Each tweet should be self-contained
5. Use "..." at the end of tweets that continue
6. Keep hashtags for the last tweet"""},
                {"role": "user", "content": f"Split this content into a Twitter thread:\n\n{content}"}
            ]
        )
        
        # Split the response into individual tweets
        thread = response.choices[0].message.content.strip().split("\n\n")
        return [tweet.strip() for tweet in thread if tweet.strip()]
    
    def _generate_hashtags(self, content: str, limit: int) -> List[str]:
        """Generate relevant hashtags for the content.
        
        Args:
            content: The post content
            limit: Maximum number of hashtags to generate
            
        Returns:
            List of generated hashtags
        """
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a hashtag expert. Generate relevant hashtags for the given content."},
                {"role": "user", "content": f"Generate up to {limit} relevant hashtags for this content:\n\n{content}"}
            ]
        )
        
        hashtags = response.choices[0].message.content.strip().split()
        return [tag if tag.startswith("#") else f"#{tag}" for tag in hashtags[:limit]]
    
    def generate_post(self, content: str, platform: str, tone: str = "neutral") -> str:
        """Generate a platform-specific social media post.
        
        Args:
            content: The main content to be posted
            platform: The social media platform
            tone: The desired tone of the post
            
        Returns:
            Generated and formatted post content
            
        Raises:
            ValueError: If platform is not supported
        """
        if platform.lower() not in Config.PLATFORMS:
            raise ValueError(f"Unsupported platform: {platform}")
            
        initial_state: AgentState = {
            "content": content,
            "platform": platform.lower(),
            "tone": tone,
            "researched_content": "",
            "generated_content": "",
            "formatted_content": "",
            "final_content": ""
        }
        
        final_state = self.graph.invoke(initial_state)
        return final_state["final_content"] 