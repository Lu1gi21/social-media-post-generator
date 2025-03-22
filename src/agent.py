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
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": Prompts.SYSTEM_PROMPTS[platform]},
                {"role": "user", "content": Prompts.get_user_prompt(full_content, platform, tone)}
            ]
        )
        
        state["generated_content"] = response.choices[0].message.content
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
        
        # Check length
        if len(content) > config.max_length:
            content = content[:config.max_length-3] + "..."
            
        # Validate hashtags
        hashtags = [tag for tag in content.split() if tag.startswith("#")]
        if len(hashtags) > config.hashtag_limit:
            # Remove excess hashtags
            content = " ".join(content.split()[:-len(hashtags)+config.hashtag_limit])
            
        state["final_content"] = content
        return state
    
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