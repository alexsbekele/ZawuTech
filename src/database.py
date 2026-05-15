from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# This is the database file — will be created automatically
DATABASE_URL = "sqlite:///./zawu.db"

# Engine is the connection to the database
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # needed for SQLite only
)

# Each request gets its own session — like a temporary workspace
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that all our models will inherit from
Base = declarative_base()

# Dependency — gives a database session to each route and closes it after
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()