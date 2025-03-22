"""
Researcher agent implementation for gathering and analyzing information.

This module provides a dedicated researcher agent that uses web search and
scraping capabilities to gather comprehensive information about topics.
"""

from typing import Dict, List, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain_core.messages import HumanMessage, AIMessage

from .web_search import WebSearchTool
from .research_cache import ResearchCache

class ResearcherAgent:
    """Agent specialized in gathering and analyzing information from various sources."""
    
    def __init__(self, model: str = "gpt-4o-mini", cache_duration: int = 24):
        """
        Initialize the researcher agent.
        
        Args:
            model (str): The OpenAI model to use for analysis
            cache_duration (int): Duration in hours before cache entries expire
        """
        self.model = model
        self.web_search = WebSearchTool(max_results=5)
        self.llm = ChatOpenAI(model=model, temperature=0)
        self.tools = self._create_tools()
        self.agent = self._create_agent()
        self.cache = ResearchCache(cache_duration)
        
    def _create_tools(self) -> List[Tool]:
        """
        Create the tools available to the researcher agent.
        
        Returns:
            List[Tool]: List of tools for the agent to use.
        """
        return [
            Tool(
                name="web_search",
                func=self.web_search.search_and_scrape,
                description="""Use this tool to search the web and scrape content about a topic.
                Input should be a search query string.
                Returns a list of documents containing relevant information."""
            )
        ]
    
    def _create_agent(self) -> AgentExecutor:
        """
        Create the researcher agent with its tools and prompt.
        
        Returns:
            AgentExecutor: The configured agent executor.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a research assistant specialized in gathering and analyzing information.
            Your goal is to provide comprehensive, accurate, and well-structured information about topics.
            
            Follow these steps:
            1. Start with a focused search query using the most important keywords
            2. If no results, try a broader search or different keyword combinations
            3. Analyze and synthesize the information
            4. Identify key facts, trends, and insights
            5. Structure the information in a clear, organized way
            
            Guidelines:
            - Keep search queries concise and focused
            - Use specific keywords related to the topic
            - If initial search fails, try alternative keywords or broader terms
            - Always cite your sources and provide context for the information
            - If you can't find recent information, acknowledge this and provide historical context"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5  # Limit the number of search attempts
        )
    
    def research_topic(self, topic: str, focus_areas: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Research a topic and provide structured information.
        
        Args:
            topic (str): The topic to research
            focus_areas (Optional[List[str]]): Specific areas to focus on
            
        Returns:
            Dict[str, str]: Structured research results
        """
        # Check cache first
        cached_results = self.cache.get(topic)
        if cached_results:
            return cached_results
        
        # Create research query
        query = f"Research about {topic}"
        if focus_areas:
            query += f" focusing on: {', '.join(focus_areas)}"
        
        try:
            # Run the agent with error handling
            result = self.agent.invoke({
                "input": query,
                "chat_history": []
            })
            
            # Process and structure the results
            research_output = result["output"]
            
            # Extract key components
            structured_output = {
                "summary": self._extract_summary(research_output),
                "key_facts": self._extract_key_facts(research_output),
                "trends": self._extract_trends(research_output),
                "sources": self._extract_sources(research_output)
            }
            
            # Cache the results
            self.cache.set(topic, structured_output)
            
            return structured_output
            
        except Exception as e:
            print(f"Error during research: {str(e)}")
            # Return a default structure with error information
            return {
                "summary": f"Unable to research topic '{topic}' at this time. Please try again later.",
                "key_facts": "No key facts available.",
                "trends": "No trends available.",
                "sources": "No sources available."
            }
    
    def _extract_summary(self, text: str) -> str:
        """Extract the main summary from the research output."""
        return text.split("\n\n")[0] if "\n\n" in text else text
    
    def _extract_key_facts(self, text: str) -> str:
        """Extract key facts from the research output."""
        facts_section = ""
        for line in text.split("\n"):
            if line.lower().startswith(("key fact", "fact:", "•", "-")):
                facts_section += line + "\n"
        return facts_section.strip() or "No key facts found."
    
    def _extract_trends(self, text: str) -> str:
        """Extract trends from the research output."""
        trends_section = ""
        for line in text.split("\n"):
            if line.lower().startswith(("trend:", "current trend", "developing:")):
                trends_section += line + "\n"
        return trends_section.strip() or "No trends found."
    
    def _extract_sources(self, text: str) -> str:
        """Extract sources from the research output."""
        sources_section = ""
        for line in text.split("\n"):
            if line.lower().startswith(("source:", "reference:", "from:", "via:")):
                sources_section += line + "\n"
        return sources_section.strip() or "No sources found." 