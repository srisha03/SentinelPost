from dotenv import load_dotenv
from pathlib import Path
import httpx
from datetime import datetime, timedelta
from typing import List, Dict
import os

dotenv_path = Path('.env')
# print(dotenv_path.resolve())

load_dotenv(dotenv_path=dotenv_path)

class NewsFetcher:
    BASE_URL = "https://api.newscatcherapi.com/v2/search"
    HEADERS = {
        "x-api-key": os.getenv("NEWSFETCHER_API_KEY")
    }

    @classmethod
    def fetch_latest_news(cls, keywords: List[str], lang: str = "en", page: int = 3) -> List[Dict]:
        # Calculate date range for today and yesterday
        today = datetime.today().strftime('%Y-%m-%d')
        yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Combine keywords using 'AND' operator
        query = " AND ".join(keywords)
        
        params = {
            "q": query,
            "lang": lang,
            "from": yesterday,
            "to": today,
            "page": page
        }
        
        response = httpx.get(cls.BASE_URL, headers=cls.HEADERS, params=params)
        data = response.json()
        return data.get("articles", [])

if __name__ == "__main__":
    keywords = ["technology","china","environment"]
    articles = NewsFetcher.fetch_latest_news(keywords=keywords)
    for article in articles:
        print("Title:", article["title"])
        print("Author:", article["author"])
        print("Published Date:", article["published_date"])
        print("Summary:", article["summary"])
        print("URL:", article["link"])
        print("-------------------------------------------------")
