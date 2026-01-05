import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Database credentials
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_OPTIONS = os.getenv("DB_OPTIONS", "?sslmode=require")

# Construct the connection string
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}{DB_OPTIONS}"

# The Engine (The connection manager)
engine = create_engine(DATABASE_URL)

# The Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# The Base class for models
Base = declarative_base()

# --- ADD THIS FUNCTION BELOW ---
def get_db():
    """
    Dependency to provide a database session for each request.
    This ensures Availability and connection Integrity.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()