import os
import logging
import tempfile
import streamlit as st
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import and_
from datetime import datetime
import base64
from app.db_models.models import Base, Article
from app.services.news_fetcher import NewsFetcher
from PIL import Image
from app.services.img_gen import ImageGenerator
from app.ml_models.summarizer import TextSummarizer
from app.services.utils import preprocess_query
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import torch

# Set up logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("Starting Streamlit app...Main Function\n")
    state = st.session_state

    # Streamlit UI
    st.title("SentinelPost")
    st.write("Your personalized, safe AI news platform")

    # Initialize services and models
    print("Initializing State...\n")
    news_fetcher, summarizer, SessionLocal = initialize_state(state)

    # User Search Bar
    with st.form("search_bar"):
        state.user_query = st.text_input("Search for news", "")
        submitted = st.form_submit_button("Submit")

    image_filenames = []  # Initialize

    if submitted:
        # Fetch News if not fetched already
        if "NewsFetched" not in state.submitted_forms:
            logger.info("Attempting to Fetch News...")
            state.articles_to_display = get_news(state, submitted, news_fetcher, summarizer, SessionLocal)
            state.submitted_forms.append("NewsFetched")
            print(state.submitted_forms)

        # Create placeholders for articles
        article_placeholders = [st.empty() for _ in state.articles_to_display]

        # Display articles without images
        for placeholder, article in zip(article_placeholders, state.articles_to_display):
            display_single_article(placeholder, article, None)

        # Fetch Images if News has been fetched but Images haven't
        if "NewsFetched" in state.submitted_forms and "ImagesFetched" not in state.submitted_forms:
            logger.info("Attempting to Fetch Images...")
            logger.info("Clearing CUDA Cache...")
            torch.cuda.empty_cache()
            image_generator = ImageGenerator()
            image_filenames = get_images(state, image_generator)
            state.submitted_forms.append("ImagesFetched")

        # Update placeholders with articles and images
        for placeholder, article, image_filename in zip(article_placeholders, state.articles_to_display, image_filenames):
            display_single_article(placeholder, article, image_filename)

def display_single_article(placeholder, article, image_filename):
    """Displays the articles in the given placeholder."""
    col1, col2 = placeholder.columns([1, 3])
    with col1:
        if image_filename:
            img_to_display = Image.open(image_filename)
            col1.image(img_to_display, caption=article.title, use_column_width=True)
        else:
            col1.image("https://via.placeholder.com/150", caption=article.title, use_column_width=True)
    with col2:
        col2.subheader(article.title)
        col2.write(article.summary)
        col2.write(article.published_at)

def initialize_state(state):
    # Early exit if services and database are already initialized
    if getattr(state, "db_and_services_init", False):
        return state.news_fetcher, state.summarizer, state.SessionLocal

    logger.info("Attempting to Initializing state...")

    if "submitted_forms" not in state:
        state.submitted_forms = []
    if "user_query" not in state:
        state.user_query = ''
    if "articles_to_display" not in state:
        state.articles_to_display = []

    # Database setup
    DATABASE_URL = "sqlite:///articles.db"
    engine = create_engine(DATABASE_URL)

    # Check if SQLite database exists create tables if it not
    if DATABASE_URL.startswith("sqlite"):
        logger.info("Checking if database exists...")
        db_path = DATABASE_URL.split("///")[1]
        if not os.path.exists(db_path):
            # Create tables in the database
            Base.metadata.create_all(engine)
            print("Database and tables created successfully!")
        else:
            print("Database already exists.")

    # Initialize the database session
    state.SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    # Initialize services and models
    state.news_fetcher = NewsFetcher()
    state.summarizer = TextSummarizer()
    
    state.db_and_services_init = True

    logger.info("DB and Services Initializing successful.")
    return state.news_fetcher, state.summarizer, state.SessionLocal

def reset_state(state):
    state.user_query = ''
    state.articles_to_display = []
    state.submitted_forms = []

def get_news(state, submitted, news_fetcher, summarizer, SessionLocal, recursion_depth=0):
    if submitted:
        logger.info("Attempting to Fetch News...")
        with st.spinner("Fetching news..."):

            if recursion_depth == 0:
                # Preprocess the user query
                user_tokens = preprocess_query(state.user_query)
                user_query_for_tfidf = ' '.join(user_tokens)
            
            # Fetch all articles from the database
            all_articles = SessionLocal().query(Article).all()
            summaries = [article.summary for article in all_articles]
            
            # Using TfidfVectorizer to transform summaries and user query
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(summaries)
            user_query_vector = vectorizer.transform([user_query_for_tfidf])
            
            # Calculate cosine similarity between user query and all articles
            cosine_similarities = linear_kernel(user_query_vector, tfidf_matrix).flatten()
            
            # Pair each article with its similarity score
            scored_articles = [(score, article) for score, article in zip(cosine_similarities, all_articles)]

            # Sort articles based on their scores (in descending order) and rank
            scored_articles.sort(key=lambda x: (-x[0], x[1].rank))

            # Filter to get top 5 unique articles based on title
            seen_titles = set()
            state.articles_to_display = []
            for _, article in scored_articles:
                if article.title not in seen_titles:
                    seen_titles.add(article.title)
                    state.articles_to_display.append(article)
                if len(state.articles_to_display) == 5:
                    break

            # If we have 5 articles, return
            if len(state.articles_to_display) == 5:
                st.success("News fetched successfully!")
                return state.articles_to_display
            else:
                logger.info("Could not fetch relevant news. Attempting to fetch new articles...")
                # Limit the number of recursive calls to avoid infinite loops
                if recursion_depth >= 2:
                    st.warning("Could not fetch relevant news after multiple attempts.")
                    return []

                # Fetch new articles, summarize, store, and recursively call the function
                fetch_and_store_articles(news_fetcher, summarizer, SessionLocal, user_tokens)
                return get_news(state, submitted, news_fetcher, summarizer, SessionLocal, recursion_depth+1)

def fetch_and_store_articles(news_fetcher, summarizer, SessionLocal, queries):
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
                db_article = Article(title=article['title'], summary=summarized_content, content=content, url=article.get('link', 'N/A'), source=article.get('rights', 'N/A'), published_at=published_date, category=article.get('topic', 'N/A'), query_param=','.join(queries), language=article.get('language', 'N/A'), country=article.get('country', 'N/A'), timestamp=datetime.now() , rank = article['rank'], image = '')
                db.add(db_article)

            else:
                missing_keys = [key for key in ['title', 'link', 'rights', 'published_date'] if key not in article]
                print(f"Article missing essential keys: {missing_keys}")
                logger.warning(f"Article missing essential keys: {article}")

        db.commit()
        logger.info("Articles stored successfully.")
        return
        
    except Exception as e:
        logger.error(f"Error while fetching and storing articles: {e}")
        raise

def get_images(state, image_generator):
    with st.spinner("Generating images..."):
        logger.info("Attempting to Fetch Images...")

        # Generate images for each article and store their filenames
        image_filenames = []
        for article in state.articles_to_display:
            image_filename = image_generator.generate_image(article)
            image_filenames.append(image_filename)

        state.submitted_forms.append("ImagesFetched")
        return image_filenames if image_filenames else []

# Main Execution
if __name__ == "__main__":
    main()