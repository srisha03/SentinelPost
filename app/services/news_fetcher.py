import requests
import os
from typing import List
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('.env')
# print(dotenv_path.resolve())

load_dotenv(dotenv_path=dotenv_path)

class NewsFetcher:
    def __init__(self):
        self.API_KEY = os.getenv("NEWSAPI_API_KEY")
        self.BASE_URL = "https://newsapi.org/v2/"

    def fetch_news(self, query: str, days_ago: int = 1, sort_by: str = 'popularity', page_size: int = 10) -> List[dict]:
        """
        Fetch news articles from NewsAPI based on a query, from a certain number of days ago.
        :param query: The topic of interest to fetch news about
        :param days_ago: The number of days ago from which to fetch news
        :param sort_by: How to sort the fetched news. Default is 'popularity'
        :param page_size: The number of articles to return per request. Default is 10
        :return: A list of news articles, each represented as a dictionary
        """
        from_date = (datetime.now() - timedelta(days=days_ago)).date().isoformat()
        url = f"{self.BASE_URL}everything?q={query}&from={from_date}&sortBy={sort_by}&pageSize={page_size}&apiKey={self.API_KEY}"

        response = requests.get(url)
        data = response.json()

        if data['status'] != 'ok':
            print(f"Error fetching news: {data.get('message', 'No message provided')}")
            return []

        return data['articles']

# Test the class
if __name__ == "__main__":
    fetcher = NewsFetcher()
    articles = fetcher.fetch_news('technology')
    print(articles)
