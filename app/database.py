from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .db_models.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./articles.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
