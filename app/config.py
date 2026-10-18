import os
from urllib.parse import quote
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

# إنشاء كائن قاعدة البيانات هنا في ملف config
db = SQLAlchemy()

class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "foodx_db")
    DB_USER = os.getenv("DB_USER", "mohammed")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "077366")

    use_postgres = os.getenv("USE_POSTGRES", "0") == "1"
    DB_SCHEMA = os.getenv("DB_SCHEMA", "public")
    if use_postgres:
        SQLALCHEMY_DATABASE_URI = os.getenv(
            "DATABASE_URL",
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        if DB_SCHEMA and DB_SCHEMA != "public":
            SQLALCHEMY_DATABASE_URI += (
                "?options=" + quote(f"-c search_path={DB_SCHEMA}")
            )
    else:
        SQLALCHEMY_DATABASE_URI = os.getenv(
            "SQLALCHEMY_DATABASE_URI",
            "sqlite:///foodx.db"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    WTF_CSRF_ENABLED = False

    # Mail configuration for OTP
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "1") == "1"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "no-reply@foodx.com")
    
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:8080").split(",")
        if origin.strip()
    ]