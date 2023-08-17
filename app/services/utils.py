import nltk
nltk.download('stopwords')
import re
from nltk.corpus import stopwords

STOPWORDS = set(stopwords.words('english'))

def preprocess_query(query):
    # Convert to lowercase and remove special characters
    tokens = re.findall(r'\b\w+\b', query.lower())
    
    # Filter out common stop words
    tokens = [token for token in tokens if token not in STOPWORDS]
    
    return tokens
