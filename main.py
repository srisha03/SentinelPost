
import logging
import streamlit as st
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import and_
from datetime import datetime
from app.db_models.models import Base, Article
from app.services.news_fetcher import NewsFetcher  
from app.ml_models.summarizer import TextSummarizer

# Set up logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "sqlite:///articles.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

# Initialize services and models
news_fetcher = NewsFetcher()
summarizer = TextSummarizer()

def main():
    state = st.session_state

    # Streamlit UI
    st.title("SentinelPost")
    st.write("Your personalized, safe AI news platform")

    initialize_state(state)

    # User Search Bar
    with st.form("search_bar"):
        state.user_query = st.text_input("Search for news", "")
        submitted = st.form_submit_button("Submit")

    if submitted:
        state.articles_to_display = []
        user_tokens = state.user_query.split()
        # Create a list of conditions to check if each token is present in the Article summary
        conditions = [Article.summary.contains(token) for token in user_tokens]
        # Combine the conditions using the and_ operator
        combined_condition = and_(*conditions)
        # Query articles that contain most, if not all, of the tokens in the user_query and have lower rank values
        state.articles_to_display = SessionLocal().query(Article).filter(combined_condition).order_by(Article.rank).limit(5).all()

        # News Section
        if len(state.articles_to_display) == 5:
            display_news(state.articles_to_display)
        else:
            fetch_and_store_articles(user_tokens)
            state.articles_to_display = SessionLocal().query(Article).filter(combined_condition).order_by(Article.rank).limit(5).all()
            display_news(state.articles_to_display)

    # # Recommended Section
    # category = st.selectbox("Recommended Categories", ["Hottest", "Sports", "Technology", "Politics", "Education", "Global"])
    # if category and not user_query:
    #     articles_to_display = SessionLocal().query(Article).filter(Article.category.contains(category)).limit(5).all()
    #     display_news(articles_to_display)

    # Fetch and store articles (can be triggered by a Streamlit button or other mechanism)
    # For now, using a static list of queries
    # queries = ["technology"]
    # fetch_and_store_articles(queries)

def initialize_state(state):
    state.user_query = ''
    state.articles_to_display = []

def reset_state(state):
    state.user_query = ''

def fetch_and_store_articles(queries):
    """Fetches articles based on queries, summarizes them, and stores in the database."""
    try:
        logger.info(f"Fetching news for query: {queries}...")
        articles = news_fetcher.fetch_news(keywords=queries)
        logger.info("News fetched successfully.")

        try:
            published_date = datetime.strptime(article['published_date'], '%Y-%m-%d %H:%M:%S')
        except:
            published_date = datetime.now()
    
        db = SessionLocal()
        for article in articles:
            print(f"Processing article: {article}")
            # Check for essential keys before processing
            if all(key in article for key in ['title', 'link', 'rights', 'published_date']):
                
                logger.info("Summarizing article...")
                content = article['summary']
                summarized_content = summarizer.summarize(content)

                # Ensure the summary is a string and not a list
                if isinstance(summarized_content, list) and len(summarized_content) > 0:
                    summarized_content = ".".join(summarized_content)

                logger.info("Storing article to database...")
                # Create and store the Article object
                db_article = Article(title=article['title']
                                     , summary=summarized_content
                                     , content=content
                                     , url=article.get('link', 'N/A')
                                     , source=article.get('rights', 'N/A')
                                     , published_at=published_date
                                     , category=article.get('topic', 'N/A')
                                     , query_param=','.join(queries)
                                     , language=article.get('language', 'N/A')
                                     , country=article.get('country', 'N/A')
                                     , timestamp=datetime.now() 
                                     , rank = article['rank']
                                     )
                db.add(db_article)
            else:
                missing_keys = [key for key in ['title', 'link', 'rights', 'published_date'] if key not in article]
                print(f"Article missing essential keys: {missing_keys}")
                logger.warning(f"Article missing essential keys: {article}")

        db.commit()
    except Exception as e:
        logger.error(f"Error while fetching and storing articles: {e}")
        print(f"Exception raised: {e}")  # Print the exception
        raise

def display_news(articles):
    """Displays news articles in the Streamlit UI."""
    for article in articles:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image("https://via.placeholder.com/150", caption=article.title, use_column_width=True)
        with col2:
            st.subheader(article.title)
            st.write(article.summary)
            st.write(article.published_at)


# Main Execution
if __name__ == "__main__":
    main()