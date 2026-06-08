from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

URL = "postgresql://postgres:123456@localhost:5432/depo_db"
engine = create_engine(URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

