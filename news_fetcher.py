# news_fetcher.py

import os
import requests
from typing import List, Dict


class NewsFetcher:
    """
    Module 1: Data Acquisition
    Fetches US top headlines and relevant international news.
    """

    HEADLINES_URL = "https://newsapi.org/v2/top-headlines"

    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Please set the 'NEWS_API_KEY' environment variable.")

    def fetch_us_headlines(self, page_size: int = 100) -> List[Dict]:
        """
        Fetches all top business headlines from the US.
        """
        params = {
            "country": "us",
            "category": "business",
            "pageSize": page_size,
            "apiKey": self.api_key
        }
        try:
            response = requests.get(self.HEADLINES_URL, params=params)
            response.raise_for_status()
            return self._clean_articles(response.json())
        except requests.exceptions.RequestException as e:
            print(f"Error fetching US headlines: {e}")
            return []

    def fetch_international_keyword_news(self, query: str, country: str, page_size: int = 25) -> List[Dict]:
        """
        Fetches top headlines from a specific country that match a keyword query.
        """
        params = {
            "country": country,
            "q": query,
            "pageSize": page_size,
            "apiKey": self.api_key
        }
        try:
            response = requests.get(self.HEADLINES_URL, params=params)
            response.raise_for_status()
            return self._clean_articles(response.json())
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news for country '{country}' with query '{query}': {e}")
            return []

    def _clean_articles(self, data: Dict) -> List[Dict]:
        """
        Helper function to parse and clean articles from an API response.
        """
        articles = data.get("articles", [])
        cleaned_articles = []
        for article in articles:
            if article.get("content"):
                cleaned_articles.append({
                    "source": article["source"]["name"],
                    "title": article["title"],
                    "url": article["url"],
                    "published_at": article["publishedAt"],
                    "content": article["content"]
                })
        return cleaned_articles