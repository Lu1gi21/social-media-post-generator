"""
Web search and scraping utilities for the social media post generator.

This module provides functionality for web searching and content scraping,
integrating with various search engines and web scraping tools.
"""

from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import trafilatura
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import time
import random
import logging
from urllib.parse import quote_plus

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSearchTool:
    """A tool for performing web searches and scraping content."""
    
    def __init__(self, max_results: int = 5):
        """
        Initialize the WebSearchTool.
        
        Args:
            max_results (int): Maximum number of results to return per search.
        """
        self.max_results = max_results
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
        ]
        self._setup_selenium()
        self.search_engines = [
            self._search_duckduckgo,
            self._search_google,
            self._search_bing
        ]
    
    def _setup_selenium(self):
        """Set up Selenium WebDriver for dynamic content scraping."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": random.choice(self.user_agents)
        })
    
    def _search_duckduckgo(self, query: str, max_retries: int = 3) -> List[Dict[str, str]]:
        """
        Search using DuckDuckGo with retry logic and improved error handling.
        
        Args:
            query (str): The search query
            max_retries (int): Maximum number of retry attempts
            
        Returns:
            List[Dict[str, str]]: List of search results
        """
        results = []
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                logger.info(f"Attempting DuckDuckGo search for query: {query}")
                
                # Try direct API first
                with DDGS() as ddgs:
                    search_results = list(ddgs.text(query, max_results=self.max_results))
                    if search_results:
                        for r in search_results:
                            result = {
                                'title': r.get('title', ''),
                                'link': r.get('link', r.get('url', '')),
                                'snippet': r.get('body', r.get('snippet', r.get('description', '')))
                            }
                            if result['title'] and result['link']:
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
                
                headers = {
                    'User-Agent': random.choice(self.user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Connection': 'keep-alive',
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    for result in soup.select('.result'):
                        title_elem = result.select_one('.result__title a')
                        snippet_elem = result.select_one('.result__snippet')
                        
                        if title_elem:
                            result_dict = {
                                'title': title_elem.get_text(strip=True),
                                'link': title_elem.get('href', ''),
                                'snippet': snippet_elem.get_text(strip=True) if snippet_elem else ''
                            }
                            if result_dict['title'] and result_dict['link']:
                                results.append(result_dict)
                                logger.debug(f"Found result: {result_dict['title']}")
                    
                    if results:
                        logger.info(f"Successfully found {len(results)} results using alternative method")
                        break
                
            except Exception as e:
                retry_count += 1
                logger.error(f"DuckDuckGo search error (attempt {retry_count}/{max_retries}): {str(e)}")
                if retry_count < max_retries:
                    # Exponential backoff with jitter
                    wait_time = (2 ** retry_count) + random.uniform(0, 2)
                    logger.info(f"Waiting {wait_time:.2f} seconds before retry...")
                    time.sleep(wait_time)
                else:
                    logger.error("Max retries reached for DuckDuckGo search")
        
        return results
    
    def _search_google(self, query: str) -> List[Dict[str, str]]:
        """Search using Google."""
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
        """Search using Bing."""
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
        """
        Perform a web search using multiple search engines.
        
        Args:
            query (str): The search query.
            
        Returns:
            List[Dict[str, str]]: List of search results with title, link, and snippet.
        """
        all_results = []
        
        # Try each search engine
        for search_engine in self.search_engines:
            try:
                results = search_engine(query)
                if results:
                    all_results.extend(results)
                    # If we have enough results, stop searching
                    if len(all_results) >= self.max_results:
                        break
                # Add a small delay between searches
                time.sleep(random.uniform(2, 4))  # Increased delay to avoid rate limiting
            except Exception as e:
                logger.error(f"Search engine error: {str(e)}")
                continue
        
        # If no results from any engine, try a simplified query
        if not all_results:
            simplified_query = ' '.join(query.split()[:3])
            logger.info(f"Trying simplified query: {simplified_query}")
            for search_engine in self.search_engines:
                try:
                    results = search_engine(simplified_query)
                    if results:
                        all_results.extend(results)
                        if len(all_results) >= self.max_results:
                            break
                    time.sleep(random.uniform(2, 4))  # Increased delay
                except Exception as e:
                    logger.error(f"Simplified search error: {str(e)}")
                    continue
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result['link'] not in seen_urls:
                seen_urls.add(result['link'])
                unique_results.append(result)
        
        logger.info(f"Total unique results found: {len(unique_results)}")
        return unique_results[:self.max_results]
    
    def scrape_content(self, url: str) -> Optional[str]:
        """
        Scrape content from a webpage.
        
        Args:
            url (str): The URL to scrape.
            
        Returns:
            Optional[str]: The scraped content or None if failed.
        """
        try:
            # First try with trafilatura
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                return trafilatura.extract(downloaded)
            
            # Fallback to Selenium for dynamic content
            self.driver.get(url)
            time.sleep(random.uniform(1, 2))  # Add random delay
            
            # Scroll the page to load dynamic content
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'iframe']):
                element.decompose()
            
            # Get the main content
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            if main_content:
                return main_content.get_text(separator='\n', strip=True)
            
            return soup.get_text(separator='\n', strip=True)
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None
    
    def search_and_scrape(self, query: str) -> List[Document]:
        """
        Perform a search and scrape content from results.
        
        Args:
            query (str): The search query.
            
        Returns:
            List[Document]: List of LangChain documents containing scraped content.
        """
        results = self.search(query)
        documents = []
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        for result in results:
            content = self.scrape_content(result['link'])
            if content:
                # Split content into chunks
                chunks = text_splitter.split_text(content)
                for chunk in chunks:
                    documents.append(Document(
                        page_content=chunk,
                        metadata={
                            'source': result['link'],
                            'title': result['title']
                        }
                    ))
        
        return documents
    
    def __del__(self):
        """Clean up Selenium WebDriver on object destruction."""
        if hasattr(self, 'driver'):
            self.driver.quit() 