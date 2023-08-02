import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import string
from typing import List, Dict
from app.services.news_fetcher import NewsFetcher

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

class ArticlePreprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))

    def clean_text(self, text: str) -> str:
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        return text

    def tokenize(self, text: str) -> Dict[str, List[str]]:
        # Tokenize into words and sentences
        word_tokens = word_tokenize(text)
        sentence_tokens = sent_tokenize(text)
        return {"words": word_tokens, "sentences": sentence_tokens}

    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        return [word for word in tokens if word not in self.stop_words]

    def process_articles(self, articles: List[Dict[str, str]]) -> List[Dict[str, str]]:
        for article in articles:
            content = self.clean_text(article["content"])
            tokens = self.tokenize(content)
            tokens["words"] = self.remove_stopwords(tokens["words"])
            article["content_tokens"] = tokens  # changed the key name to avoid confusion

            if "description" in article:
                description = self.clean_text(article["description"])
                description_tokens = self.tokenize(description)
                description_tokens["words"] = self.remove_stopwords(description_tokens["words"])
                article["description_tokens"] = description_tokens
        return articles



# Test the class
if __name__ == "__main__":
    fetcher = NewsFetcher()
    articles = fetcher.fetch_news('Apple')
    
    preprocessor = ArticlePreprocessor()
    processed_articles = preprocessor.process_articles(articles)
    print(processed_articles)
