import logging
from datetime import datetime
from app.services.news_fetcher import NewsFetcher  
from app.ml_models.summarizer import TextSummarizer
from app.db_models.models import Article
from app.database import SessionLocal

# Set up logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
# Initialize services and models
news_fetcher = NewsFetcher()
summarizer = TextSummarizer()

# Fetch news
# Defining the categories to pull news on
queries = ["technology"]

try:
    logger.info(f"Fetching news for query: {queries}...")
    articles = news_fetcher.fetch_news(keywords=queries)
    logger.info("News fetched successfully.")
    
    db = SessionLocal()
    for article in articles:
        try:
            content = article['summary']
            
            logger.info("Summarizing article...")
            # Generate summary
            summarized_content = summarizer.summarize(content)            
            logger.info("Storing article to database...")

            try:
                published_date = datetime.strptime(article['published_date'], '%Y-%m-%d %H:%M:%S')
            except:
                published_date = datetime.now()

            # Print the data being inserted
            # print("Inserting Data:", {
            #     "title": article['title'],
            #     "summary": summarized_content,
            #     "url": article['link'],
            #     "source": article['rights'],
            #     "published_at": published_date,
            #     "category": article['topic'],
            #     "query_param": str(queries),
            #     "language": 'en',
            #     "country": article['country'],
            #     "timestamp": datetime.now(),
            #     "rank" : article['rank']
                
            # })

            # Ensure the summary is a string and not a list
            if isinstance(summarized_content, list) and len(summarized_content) > 0:
                summarized_content = summarized_content[0]

            db_article = Article(
                title=article['title'],
                summary=summarized_content,
                content = article['summary'],
                url=article['link'],
                source = article['rights'],
                published_at=published_date,
                category=article['topic'],
                query_param = str(queries), # list of keywords passed
                language='en',
                country=article['country'],
                timestamp=datetime.now(),
                rank = article['rank']
            )
            db.add(db_article)
            logger.info("Article stored successfully.")
        except Exception as e:
            logger.exception("An error occurred while processing an article.")
            continue
    db.commit()

except Exception as e:
    logger.exception("An error occurred while fetching or processing news.")