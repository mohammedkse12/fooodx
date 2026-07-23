from datetime import datetime
from urllib.parse import quote_plus

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    account_status = db.Column(db.String(30), nullable=False, default="pending_review")
    phone = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(255), nullable=True)
    factory_name = db.Column(db.String(120), nullable=True)
    shipping_available = db.Column(db.String(10), nullable=True)
    commercial_register = db.Column(db.String(80), nullable=True)
    store_name = db.Column(db.String(120), nullable=True)
    national_id = db.Column(db.String(20), nullable=True)
    trade_license = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


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
    """Link Flask app to the configured database and create all tables."""
    db.init_app(app)
    with app.app_context():
        db.create_all()


def serialize_account(account: Account) -> dict:
    """Return a safe JSON-serializable representation of an account."""
    return {
        "id": account.id,
        "username": account.username,
        "email": account.email,
        "role": account.role,
        "account_status": account.account_status,
        "phone": account.phone,
        "location": account.location,
        "factory_name": account.factory_name,
        "shipping_available": account.shipping_available,
        "commercial_register": account.commercial_register,
        "store_name": account.store_name,
        "national_id": account.national_id,
        "trade_license": account.trade_license,
        "created_at": account.created_at.isoformat() if account.created_at else None,
    }


def test_connection() -> tuple[bool, str]:
    """Verify the configured database is reachable."""
    try:
        with db.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True, "Connected to the database successfully."
    except Exception as exc:
        return False, str(exc)
