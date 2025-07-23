import requests

class SearxNGAPIWrapper:
    def __init__(self, base_url="http://localhost:8888", engines=None):
        self.base_url = base_url.rstrip("/")
        self.engines = engines  # e.g. ["google", "bing"]

    def search(self, query, max_results=5):
        headers = {
            "User-Agent": "FactoolSearxNGClient/1.0 (+https://yourprojecturl.example)"
        }
        params = {
            "q": query,
            "format": "json",
            "language": "en",
            "safesearch": 0,
            "engines": ",".join(self.engines) if self.engines else None,
            # "categories": "general",  # optional, add if you want to restrict categories
        }
        # Remove None or empty values from params
        params = {k: v for k, v in params.items() if v}

        response = requests.get(f"{self.base_url}/search", params=params, headers=headers)

        if response.status_code == 200:
            results = response.json().get("results", [])
            return results[:max_results]
        else:
            raise RuntimeError(f"SearxNG request failed: {response.status_code} {response.text}")
