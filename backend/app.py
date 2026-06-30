from flask import Flask, jsonify

from backend.config import Config
from backend.database import db, init_db, test_connection


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    init_db(app)

    @app.get("/api/health")
    def health():
        ok, message = test_connection()
        status = 200 if ok else 503
        return jsonify({"database": "connected" if ok else "error", "message": message}), status

    return app


app = create_app()
