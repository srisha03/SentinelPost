import logging
from datetime import datetime
from dateutil.parser import parse
import pytz
from app.services.news_fetcher import NewsFetcher
from app.services.preprocessor import ArticlePreprocessor
from app.ml_models.summarizer import TextSummarizer
from app.db_models.models import Article
from app.database import SessionLocal

# Set up logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services and models
news_fetcher = NewsFetcher()
preprocessor = ArticlePreprocessor()
summarizer = TextSummarizer()

# Fetch news
# Define your queries here
queries = ["health"]

for query in queries:
    try:
        logger.info(f"Fetching news for query: {query}...")
        articles = news_fetcher.fetch_news(query, page_size = 3)
        logger.info("News fetched successfully.")
        
        logger.info("Processing articles...")
        processed_articles = preprocessor.process_articles(articles)
        logger.info("Articles processed successfully.")
        
        # Store to DB
        db = SessionLocal()
        for article in processed_articles:
            try:
                content = " ".join(article['content_tokens']['words'])
                description = " ".join(article['description_tokens']['words']) if 'description_tokens' in article else ""
                
                logger.info("Summarizing article...")
                # Generate summary
                summary_sentences = summarizer.summarize(f"{description} {content}")
                summary = " ".join(summary_sentences)
                
                # Store to database
                logger.info("Storing article to database...")
                db_article = Article(
                title=article['title'],
                summary=summary,  # store the summary
                url=article['url'],
                source=article['source']['name'],
                published_at=parse(article['publishedAt']).astimezone(pytz.utc),
                category=article['source']['name'],
                language='en',
                timestamp=datetime.now()
                )
                db.add(db_article)
                logger.info("Article stored successfully.")
            except Exception as e:
                logger.exception("An error occurred while processing an article.")
                continue
        db.commit()
    except Exception as e:
        logger.exception("An error occurred while fetching or processing news.")
