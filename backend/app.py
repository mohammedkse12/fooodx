from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import or_
from werkzeug.security import check_password_hash, generate_password_hash

from backend.config import Config
from backend.database import Account, db, init_db, serialize_account, test_connection


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    init_db(app)

    def get_form_payload() -> dict:
        payload = request.form.to_dict(flat=True)
        if payload:
            return payload
        return request.get_json(silent=True) or {}

    def get_required_fields(payload: dict, required_fields: list[str]) -> list[str]:
        return [field for field in required_fields if not str(payload.get(field, "")).strip()]

    @app.get("/api/health")
    def health():
        ok, message = test_connection()
        status = 200 if ok else 503
        return jsonify({"database": "connected" if ok else "error", "message": message}), status

    @app.post("/api/auth/factory/register")
    def factory_register():
        payload = get_form_payload()
        required_fields = [
            "username",
            "password",
            "factory_name",
            "email",
            "phone",
            "location",
            "commercial_register",
        ]
        missing = get_required_fields(payload, required_fields)
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        username = str(payload["username"]).strip()
        email = str(payload["email"]).strip().lower()
        existing_account = Account.query.filter(
            or_(Account.username == username, Account.email == email)
        ).first()
        if existing_account:
            return jsonify({"error": "Username or email already registered"}), 409

        account = Account(
            username=username,
            email=email,
            role="factory",
            account_status=str(payload.get("account_status", "pending_review")).strip() or "pending_review",
            phone=str(payload["phone"]).strip(),
            location=str(payload["location"]).strip(),
            factory_name=str(payload["factory_name"]).strip(),
            shipping_available=str(payload.get("shipping_available", "yes")).strip() or "yes",
            commercial_register=str(payload["commercial_register"]).strip(),
        )
        account.set_password(str(payload["password"]))

        db.session.add(account)
        db.session.commit()
        return jsonify(
            {
                "message": "Factory account created successfully. Pending review.",
                "account": serialize_account(account),
            }
        ), 201

    @app.post("/api/auth/merchant/register")
    def merchant_register():
        payload = get_form_payload()
        required_fields = [
            "username",
            "password",
            "email",
            "store_name",
            "phone",
            "other_location",
            "national_id",
        ]
        missing = get_required_fields(payload, required_fields)
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        username = str(payload["username"]).strip()
        email = str(payload["email"]).strip().lower()
        existing_account = Account.query.filter(
            or_(Account.username == username, Account.email == email)
        ).first()
        if existing_account:
            return jsonify({"error": "Username or email already registered"}), 409

        account = Account(
            username=username,
            email=email,
            role="merchant",
            account_status="pending_review",
            phone=str(payload["phone"]).strip(),
            location=str(payload.get("other_location") or payload.get("location") or "").strip(),
            store_name=str(payload["store_name"]).strip(),
            national_id=str(payload["national_id"]).strip(),
            trade_license=str(payload.get("trade_license") or "").strip(),
        )
        account.set_password(str(payload["password"]))

        db.session.add(account)
        db.session.commit()
        return jsonify(
            {
                "message": "Merchant account created successfully. Pending review.",
                "account": serialize_account(account),
            }
        ), 201

    @app.post("/api/auth/login")
    def login():
        payload = get_form_payload()
        user_id = str(payload.get("user_id") or payload.get("username") or payload.get("email") or "").strip()
        password = str(payload.get("password") or "")

        if not user_id or not password:
            return jsonify({"error": "Username and password are required"}), 400

        account = Account.query.filter(or_(Account.username == user_id, Account.email == user_id)).first()
        if not account or not check_password_hash(account.password_hash, password):
            return jsonify({"error": "Invalid credentials"}), 401

        return jsonify({"message": "Login successful", "account": serialize_account(account)})

    return app


app = create_app()
