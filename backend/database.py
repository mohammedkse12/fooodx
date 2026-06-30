from urllib.parse import quote_plus

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()


def build_database_url(
    user: str,
    password: str,
    host: str,
    port: str,
    name: str,
) -> str:
    """Build a PostgreSQL connection URL with a safely encoded password."""
    return (
        f"postgresql://{quote_plus(user)}:{quote_plus(password)}"
        f"@{host}:{port}/{name}"
    )


def init_db(app) -> None:
    """Link Flask app to PostgreSQL via SQLAlchemy."""
    db.init_app(app)


def test_connection() -> tuple[bool, str]:
    """Verify the PostgreSQL connection is reachable."""
    try:
        db.session.execute(text("SELECT 1"))
        db.session.commit()
        return True, "Connected to PostgreSQL successfully."
    except Exception as exc:
        db.session.rollback()
        return False, str(exc)
