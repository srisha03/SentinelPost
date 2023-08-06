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
    def fetch_news(cls, keywords: List[str], lang: str = "en", page_size: int = 5, page: int = 1) -> List[Dict]:
        # Calculate date range for today and yesterday
        today = datetime.today().strftime('%Y-%m-%d')
        from_ = (datetime.today() - timedelta(days=3)).strftime('%Y-%m-%d')
        
        # Combine keywords using 'AND' operator
        query = " AND ".join(keywords)
        
        params = {
            "q": query,
            "lang": lang,
            "from": from_,
            "to": today,
            "page_size": page_size,
            "page": page
        }
        
        response = httpx.get(cls.BASE_URL, headers=cls.HEADERS, params=params)
        data = response.json()
        return data.get("articles", [])

if __name__ == "__main__":
    keywords = ["environment"]
    articles = NewsFetcher.fetch_news(keywords=keywords, page= 1)
    print(articles)

    # for article in articles:
    #     print("Title:", article["title"])
    #     print("Author:", article["author"])
    #     print("Published Date:", article["published_date"])
    #     print("Content:", article["summary"])
    #     print("URL:", article["link"])
    #     print("-------------------------------------------------")
