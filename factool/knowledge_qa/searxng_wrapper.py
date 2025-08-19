import asyncio
import aiohttp
import os
import logging
from typing import List, Dict, Any


class SearXNGAPIWrapper:

    def __init__(self, snippet_cnt=10, searxng_url=None):
        self.k = snippet_cnt
        self.gl = "us" 
        self.hl = "en"
        
        # Get SearXNG URL 
        self.searxng_url = searxng_url or os.environ.get("SEARXNG_URL", "http://localhost:8080")
        self.searxng_url = self.searxng_url.rstrip('/')
        
        # Test connection to SearXNG
        self._test_connection()
    
    def _test_connection(self):
        try:
            import requests
            response = requests.get(f"{self.searxng_url}/config", timeout=5)
            if response.status_code == 200:
                logging.info(f"SearXNG connection successful at {self.searxng_url}")
            else:
                logging.warning(f"SearXNG responded with status {response.status_code}")
        except Exception as e:
            logging.error(f"Failed to connect to SearXNG at {self.searxng_url}: {e}")
            print(f"Warning: Cannot connect to SearXNG at {self.searxng_url}. Make sure it's running.")
    
    async def _searxng_search_results(self, session, search_term: str, gl: str, hl: str) -> dict:
        """
        Perform search using SearXNG API
        """
        params = {
            'q': search_term,
            'format': 'json',
            'lang': hl,
            'categories': 'general',
            'safesearch': 0,
        }
        
        try:
            async with session.get(
                f"{self.searxng_url}/search",
                params=params,
                timeout=10
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logging.error(f"SearXNG search failed with status {response.status}")
                    return {'results': []}
        except Exception as e:
            logging.error(f"SearXNG search error for '{search_term}': {e}")
            return {'results': []}
    
    def _parse_results(self, results):
        """
        Expected output format:
        [{"content": str, "source": str}, ...]
        """
        snippets = []
        
        searxng_results = results.get('results', [])
        
        if not searxng_results:
            return [{"content": "No good Search Result was found", "source": "None"}]
        
        # Process each result
        for result in searxng_results[:self.k]:
            content = result.get('content', result.get('title', ''))
            source = result.get('url', 'None')
            
            if content:
                element = {
                    "content": content.replace('\n', ' ').strip(),
                    "source": source
                }
                snippets.append(element)
        
        # Default message if nothing found
        if len(snippets) == 0:
            return [{"content": "No good Search Result was found", "source": "None"}]
        
        # Limiting to k/2 snippets to match GoogleSerperAPIWrapper which this file replaces
        snippets = snippets[:int(self.k / 2)]
        
        return snippets
    
    async def parallel_searches(self, search_queries, gl, hl):
        """
        Perform multiple searches in parallel
        Matches the interface from GoogleSerperAPIWrapper
        """
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._searxng_search_results(session, query, gl, hl) 
                for query in search_queries
            ]
            search_results = await asyncio.gather(*tasks, return_exceptions=True)
            return search_results
    
    async def run(self, queries):
        """
        Main run method
        Args:
            queries: List of query pairs, e.g. [['query1a', 'query1b'], ['query2a', 'query2b']]
        
        Returns:
            List of snippet lists, matching GoogleSerperAPIWrapper format
        """
        # Flatten queries
        flattened_queries = []
        for sublist in queries:
            if sublist is None:
                sublist = ['None', 'None']
            for item in sublist:
                flattened_queries.append(item)
        
        # Perform searches
        results = await self.parallel_searches(flattened_queries, gl=self.gl, hl=self.hl)
        
        # Process results
        snippets_list = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"[Warning] Search query '{flattened_queries[i]}' failed with error: {result}")
                snippets_list.append([{"content": "Search failed", "source": "None"}])
            elif isinstance(result, dict):
                snippets_list.append(self._parse_results(result))
            else:
                print(f"[Warning] Unexpected result type: {type(result)} — skipping.")
                snippets_list.append([{"content": "Unexpected result format", "source": "None"}])
        
        # Split results in5o pairs
        snippets_split = [
            snippets_list[i] + snippets_list[i+1] 
            for i in range(0, len(snippets_list), 2)
        ]
        
        return snippets_split


if __name__ == "__main__":
    async def test_searxng():
        search = SearXNGAPIWrapper(snippet_cnt=10)
        
        # Test with single query pair 
        test_queries = [["What is the capital of the United States?", "US capital city"]]
        results = await search.run(test_queries)
        
        print("Test Results:")
        for i, result_group in enumerate(results):
            print(f"Query group {i}:")
            for j, result in enumerate(result_group):
                print(f"  Result {j}: {result['content'][:100]}...")
                print(f"  Source: {result['source']}")
    
    # Run test
    asyncio.run(test_searxng())