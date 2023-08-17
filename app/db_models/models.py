from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    url = Column(String(500), nullable=True)
    source = Column(String(200), nullable=True)
    published_at = Column(DateTime, nullable=True)
    category = Column(String(100), nullable=False)
    query_param = Column(Text, nullable=True)
    language = Column(String(20), nullable=False)
    country = Column(String(50), nullable=True)
    timestamp = Column(DateTime, nullable=False)
    rank = Column(Integer, nullable=True)
    image = Column(Text, nullable=True)
    user_histories = relationship('UserHistory', back_populates='article')

class UserHistory(Base):
    __tablename__ = 'user_histories'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(200), nullable=False)
    article_id = Column(Integer, ForeignKey('articles.id'))

    article = relationship('Article', back_populates='user_histories')
