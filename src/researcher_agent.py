"""
Researcher agent implementation for gathering and analyzing information.

This module provides a dedicated researcher agent that uses web search and
scraping capabilities to gather comprehensive information about topics. The agent
uses LangChain for orchestration and includes caching to optimize performance.

The agent is designed to:
- Perform focused web searches
- Extract and analyze relevant information
- Structure findings for social media content
- Cache results to avoid redundant searches

TODO:
- Add support for academic paper search
- Implement sentiment analysis for research
- Add support for competitor analysis
- Implement trend prediction
- Add support for custom research templates
- Implement research quality scoring
- Add support for research validation
"""

from typing import Dict, List, Optional

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from .research_cache import ResearchCache
from .web_search import WebSearchTool


class ResearcherAgent:
    """Agent specialized in gathering and analyzing information from various sources.

    This class implements a research agent that combines web search capabilities
    with AI-powered analysis to gather comprehensive information about topics.
    It uses LangChain for orchestration and includes caching to optimize performance.

    The agent is designed to:
    - Perform focused web searches
    - Extract and analyze relevant information
    - Structure findings for social media content
    - Cache results to avoid redundant searches
    """

    def __init__(self, model: str = "gpt-4o-mini", cache_duration: int = 24):
        """Initialize the researcher agent.

        Sets up the agent with web search capabilities, LLM for analysis,
        and caching mechanism for optimized performance.

        Args:
            model: The OpenAI model to use for analysis (default: "gpt-4o-mini")
            cache_duration: Duration in hours before cache entries expire (default: 24)
        """
        self.model = model
        self.web_search = WebSearchTool(max_results=5)
        self.llm = ChatOpenAI(model=model, temperature=0)
        self.tools = self._create_tools()
        self.agent = self._create_agent()
        self.cache = ResearchCache(cache_duration)

    def _create_tools(self) -> List[Tool]:
        """Create the tools available to the researcher agent.

        This method sets up the tools that the agent can use for research,
        currently including web search and content scraping capabilities.

        Returns:
            List[Tool]: List of configured tools for the agent to use
        """
        return [
            Tool(
                name="web_search",
                func=self.web_search.search_and_scrape,
                description="""Use this tool to search the web and scrape content about a topic.
                Input should be a search query string.
                Returns a list of documents containing relevant information.""",
            )
        ]

    def _create_agent(self) -> AgentExecutor:
        """Create the researcher agent with its tools and prompt.

        This method configures the LangChain agent with appropriate tools,
        prompts, and execution parameters for effective research.

        Returns:
            AgentExecutor: The configured agent executor ready for research tasks
        """
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """Research assistant for gathering and analyzing information.

Steps:
1. Start with focused keyword search
2. Try broader search if needed
3. Analyze and synthesize info
4. Extract key facts and trends
5. Structure clearly

Guidelines:
- Use specific keywords
- Try alternatives if needed
- Cite sources
- Note if info is not recent

For social media angles:
- Look for viral/trending aspects
- Find relatable elements
- Identify emotional hooks
- Note current discussions
- Find unique perspectives""",
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        # Create the agent with OpenAI functions
        agent = create_openai_functions_agent(
            llm=self.llm, tools=self.tools, prompt=prompt
        )

        # Configure the agent executor with limits and verbosity
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,  # Limit the number of search attempts
        )

    def research_topic(
        self, topic: str, focus_areas: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """Research a topic and provide structured information.

        TODO:
        - Add support for competitor analysis
        - Implement trend prediction
        - Add support for custom research templates
        - Implement research quality scoring
        - Add support for research validation
        - Implement proper error recovery
        - Add support for research history

        Args:
            topic: The topic to research
            focus_areas: Optional list of specific areas to focus on during research

        Returns:
            Dict[str, str]: Structured research results containing:
                - summary: Main overview of the topic
                - key_facts: Important facts and points
                - trends: Current trends and developments
                - sources: References and sources used

        Note:
            If research fails, returns a default structure with error information
        """
        # Check cache first to avoid redundant searches
        cached_results = self.cache.get(topic)
        if cached_results:
            return cached_results

        # Create research query with optional focus areas
        query = f"Research about {topic}"
        if focus_areas:
            query += f" focusing on: {', '.join(focus_areas)}"

        try:
            # Run the agent with error handling
            result = self.agent.invoke({"input": query, "chat_history": []})

            # Process and structure the results
            research_output = result["output"]

            # Extract key components into structured format
            structured_output = {
                "summary": self._extract_summary(research_output),
                "key_facts": self._extract_key_facts(research_output),
                "trends": self._extract_trends(research_output),
                "sources": self._extract_sources(research_output),
            }

            # Cache the results for future use
            self.cache.set(topic, structured_output)

            return structured_output

        except Exception as e:
            print(f"Error during research: {str(e)}")
            # Return a default structure with error information
            return {
                "summary": f"Unable to research topic '{topic}' at this time. Please try again later.",
                "key_facts": "No key facts available.",
                "trends": "No trends available.",
                "sources": "No sources available.",
            }

    def _extract_summary(self, text: str) -> str:
        """Extract the main summary from the research output.

        Args:
            text: The research output text

        Returns:
            str: The first paragraph as the main summary, or the entire text if no paragraphs
        """
        return text.split("\n\n")[0] if "\n\n" in text else text

    def _extract_key_facts(self, text: str) -> str:
        """Extract key facts from the research output.

        This method identifies and extracts lines that contain key facts,
        looking for common indicators like bullet points or fact markers.

        Args:
            text: The research output text

        Returns:
            str: Extracted key facts, or a default message if none found
        """
        facts_section = ""
        for line in text.split("\n"):
            if line.lower().startswith(("key fact", "fact:", "•", "-")):
                facts_section += line + "\n"
        return facts_section.strip() or "No key facts found."

    def _extract_trends(self, text: str) -> str:
        """Extract trends from the research output.

        This method identifies and extracts lines that contain trend information,
        looking for common indicators of trend-related content.

        Args:
            text: The research output text

        Returns:
            str: Extracted trends, or a default message if none found
        """
        trends_section = ""
        for line in text.split("\n"):
            if line.lower().startswith(("trend:", "current trend", "developing:")):
                trends_section += line + "\n"
        return trends_section.strip() or "No trends found."

    def _extract_sources(self, text: str) -> str:
        """Extract sources from the research output.

        This method identifies and extracts lines that contain source information,
        looking for common indicators of source citations.

        Args:
            text: The research output text

        Returns:
            str: Extracted sources, or a default message if none found
        """
        sources_section = ""
        for line in text.split("\n"):
            if line.lower().startswith(("source:", "reference:", "from:", "via:")):
                sources_section += line + "\n"
        return sources_section.strip() or "No sources found."
