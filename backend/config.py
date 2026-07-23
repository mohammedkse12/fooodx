import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "foodx_db")
    DB_USER = os.getenv("DB_USER", "mohammed")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "077366")

    use_postgres = os.getenv("USE_POSTGRES", "0") == "1"
    if use_postgres:
        SQLALCHEMY_DATABASE_URI = os.getenv(
            "DATABASE_URL",
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        )
    else:
        SQLALCHEMY_DATABASE_URI = os.getenv(
            "SQLALCHEMY_DATABASE_URI",
            "sqlite:///foodx.db",
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

    # Comma-separated frontend origins allowed to call /api/* (Option B: static server on 8080)
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:8080").split(",")
        if origin.strip()
    ]
