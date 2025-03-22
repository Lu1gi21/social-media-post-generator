"""
Web search and scraping utilities for the social media post generator.

This module provides functionality for web searching and content scraping,
integrating with various search engines and web scraping tools. It includes
support for multiple search engines, robust error handling, and content
extraction from both static and dynamic web pages.

Features:
- Multi-engine search support (DuckDuckGo, Google, Bing)
- Dynamic content scraping with Selenium
- Static content extraction with Trafilatura
- Rate limiting and retry mechanisms
- User agent rotation
- Content deduplication

TODO:
- Implement proper rate limiting for all search engines
- Add support for more search engines (Yahoo, Baidu)
- Implement proper proxy rotation
- Add support for custom search filters
- Implement proper error recovery
- Add support for search result caching
- Optimize memory usage in web scraping
"""

import logging
import random
import time
from typing import Dict, List, Optional
from urllib.parse import quote_plus

import requests
import trafilatura
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Set up logging with appropriate level
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebSearchTool:
    """A tool for performing web searches and scraping content.

    This class provides a comprehensive solution for web searching and content
    scraping, with support for multiple search engines and robust error handling.
    It uses a combination of direct APIs and web scraping to ensure reliable
    results.

    Features:
    - Multi-engine search support
    - Dynamic content scraping
    - Rate limiting and retries
    - User agent rotation
    - Content deduplication
    """

    def __init__(self, max_results: int = 5):
        """Initialize the WebSearchTool.

        Sets up the search tool with configuration for maximum results and
        user agent rotation. Also initializes Selenium for dynamic content
        scraping.

        Args:
            max_results: Maximum number of results to return per search (default: 5)
        """
        self.max_results = max_results
        # List of user agents for rotation to avoid detection
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        ]
        self._setup_selenium()
        # List of search engine methods to try in order
        self.search_engines = [
            self._search_duckduckgo,
            self._search_google,
            self._search_bing,
        ]

    def _setup_selenium(self):
        """Set up Selenium WebDriver for dynamic content scraping.

        Configures Chrome WebDriver with appropriate options for headless
        operation and anti-detection measures. Sets up user agent rotation
        and other necessary configurations.
        """
        # Configure Chrome options for headless operation
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)

        # Initialize Chrome WebDriver with custom service
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        # Set random user agent
        self.driver.execute_cdp_cmd(
            "Network.setUserAgentOverride",
            {"userAgent": random.choice(self.user_agents)},
        )

    def _search_duckduckgo(
        self, query: str, max_retries: int = 3
    ) -> List[Dict[str, str]]:
        """Search using DuckDuckGo with retry logic and improved error handling.

        This method implements a robust search using DuckDuckGo, with support
        for both direct API and web scraping approaches. It includes retry
        logic with exponential backoff and comprehensive error handling.

        Args:
            query: The search query to execute
            max_retries: Maximum number of retry attempts (default: 3)

        Returns:
            List[Dict[str, str]]: List of search results, each containing:
                - title: The result title
                - link: The result URL
                - snippet: A brief description or excerpt
        """
        results = []
        retry_count = 0

        while retry_count < max_retries:
            try:
                logger.info(f"Attempting DuckDuckGo search for query: {query}")

                # Try direct API first for better reliability
                with DDGS() as ddgs:
                    search_results = list(
                        ddgs.text(query, max_results=self.max_results)
                    )
                    if search_results:
                        for r in search_results:
                            result = {
                                "title": r.get("title", ""),
                                "link": r.get("link", r.get("url", "")),
                                "snippet": r.get(
                                    "body", r.get("snippet", r.get("description", ""))
                                ),
                            }
                            if result["title"] and result["link"]:
                                results.append(result)
                                logger.debug(f"Found result: {result['title']}")

                # If we got results, return them
                if results:
                    logger.info(f"Successfully found {len(results)} results")
                    break

                # If no results, try alternative search method
                logger.info("No results from direct API, trying alternative method...")
                encoded_query = quote_plus(query)
                url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

                # Set up headers for web request
                headers = {
                    "User-Agent": random.choice(self.user_agents),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Connection": "keep-alive",
                }

                # Make request and parse results
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    for result in soup.select(".result"):
                        title_elem = result.select_one(".result__title a")
                        snippet_elem = result.select_one(".result__snippet")

                        if title_elem:
                            result_dict = {
                                "title": title_elem.get_text(strip=True),
                                "link": title_elem.get("href", ""),
                                "snippet": (
                                    snippet_elem.get_text(strip=True)
                                    if snippet_elem
                                    else ""
                                ),
                            }
                            if result_dict["title"] and result_dict["link"]:
                                results.append(result_dict)
                                logger.debug(f"Found result: {result_dict['title']}")

                    if results:
                        logger.info(
                            f"Successfully found {len(results)} results using alternative method"
                        )
                        break

            except Exception as e:
                retry_count += 1
                logger.error(
                    f"DuckDuckGo search error (attempt {retry_count}/{max_retries}): {str(e)}"
                )
                if retry_count < max_retries:
                    # Exponential backoff with jitter for retries
                    wait_time = (2**retry_count) + random.uniform(0, 2)
                    logger.info(f"Waiting {wait_time:.2f} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error("Max retries reached for DuckDuckGo search")

        return results

    def _search_google(self, query: str) -> List[Dict[str, str]]:
        """Search using Google.

        TODO:
        - Implement Google Custom Search API integration
        - Add support for Google News search
        - Implement proper rate limiting
        - Add support for search filters
        - Implement proper error handling
        - Add support for result pagination

        Args:
            query: The search query to execute

        Returns:
            List[Dict[str, str]]: List of search results
        """
        results = []
        try:
            # Use Google Custom Search API or implement scraping
            # This is a placeholder for Google search implementation
            logger.info("Google search not implemented yet")
            pass
        except Exception as e:
            logger.error(f"Google search error: {str(e)}")
        return results

    def _search_bing(self, query: str) -> List[Dict[str, str]]:
        """Search using Bing.

        TODO:
        - Implement Bing Web Search API integration
        - Add support for Bing News search
        - Implement proper rate limiting
        - Add support for search filters
        - Implement proper error handling
        - Add support for result pagination

        Args:
            query: The search query to execute

        Returns:
            List[Dict[str, str]]: List of search results
        """
        results = []
        try:
            # Use Bing Web Search API or implement scraping
            # This is a placeholder for Bing search implementation
            logger.info("Bing search not implemented yet")
            pass
        except Exception as e:
            logger.error(f"Bing search error: {str(e)}")
        return results

    def search(self, query: str) -> List[Dict[str, str]]:
        """Perform a web search using multiple search engines.

        This method implements a comprehensive search strategy that tries
        multiple search engines in sequence until sufficient results are
        found. It includes fallback to simplified queries and deduplication
        of results.

        Args:
            query: The search query to execute

        Returns:
            List[Dict[str, str]]: List of unique search results, limited to
                max_results, each containing title, link, and snippet
        """
        all_results = []

        # Try each search engine in sequence
        for search_engine in self.search_engines:
            try:
                results = search_engine(query)
                if results:
                    all_results.extend(results)
                    # Stop if we have enough results
                    if len(all_results) >= self.max_results:
                        break
                # Add delay between searches to avoid rate limiting
                time.sleep(random.uniform(2, 4))
            except Exception as e:
                logger.error(f"Search engine error: {str(e)}")
                continue

        # If no results, try with simplified query
        if not all_results:
            simplified_query = " ".join(query.split()[:3])
            logger.info(f"Trying simplified query: {simplified_query}")
            for search_engine in self.search_engines:
                try:
                    results = search_engine(simplified_query)
                    if results:
                        all_results.extend(results)
                        if len(all_results) >= self.max_results:
                            break
                    time.sleep(random.uniform(2, 4))
                except Exception as e:
                    logger.error(f"Simplified search error: {str(e)}")
                    continue

        # Remove duplicate results based on URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result["link"] not in seen_urls:
                seen_urls.add(result["link"])
                unique_results.append(result)

        logger.info(f"Total unique results found: {len(unique_results)}")
        return unique_results[: self.max_results]

    def scrape_content(self, url: str) -> Optional[str]:
        """Scrape content from a webpage.

        This method implements a two-step approach to content scraping:
        1. Try Trafilatura for static content
        2. Fall back to Selenium for dynamic content

        Args:
            url: The URL to scrape

        Returns:
            Optional[str]: The scraped content if successful, None otherwise
        """
        try:
            # First try with Trafilatura for static content
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                return trafilatura.extract(downloaded)

            # Fallback to Selenium for dynamic content
            self.driver.get(url)
            time.sleep(random.uniform(1, 2))  # Add random delay

            # Scroll the page to load dynamic content
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )

            # Get the page content
            page_content = self.driver.page_source
            soup = BeautifulSoup(page_content, "html.parser")

            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()

            # Extract text content
            content = soup.get_text(separator="\n", strip=True)
            return content

        except Exception as e:
            logger.error(f"Error scraping content from {url}: {str(e)}")
            return None

    def search_and_scrape(self, query: str) -> List[Document]:
        """Perform a search and scrape content from results.

        This method combines search and scraping functionality to gather
        comprehensive content about a topic. It searches across multiple
        engines and scrapes content from the results.

        Args:
            query: The search query to execute

        Returns:
            List[Document]: List of LangChain documents containing scraped content
        """
        # Get search results
        results = self.search(query)

        # Scrape content from each result
        documents = []
        for result in results:
            try:
                content = self.scrape_content(result["link"])
                if content:
                    # Split content into chunks for processing
                    splitter = RecursiveCharacterTextSplitter(
                        chunk_size=1000, chunk_overlap=200
                    )
                    chunks = splitter.split_text(content)

                    # Create documents from chunks
                    for chunk in chunks:
                        doc = Document(
                            page_content=chunk,
                            metadata={
                                "source": result["link"],
                                "title": result["title"],
                            },
                        )
                        documents.append(doc)

            except Exception as e:
                logger.error(f"Error processing result {result['link']}: {str(e)}")
                continue

        return documents

    def __del__(self):
        """Clean up resources when the object is destroyed.

        Ensures proper cleanup of the Selenium WebDriver to prevent
        resource leaks.
        """
        try:
            self.driver.quit()
        except:
            pass
