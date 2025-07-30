# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_USER = "postgres"
DB_PASSWORD = "BtkTestApp!123"
DB_HOST = "34.22.172.29"
DB_PORT = "5432"
DB_NAME = "otizm_db"  # senin oluşturduğun veritabanı adı buysa

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
