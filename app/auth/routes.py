import re
from flask import Blueprint, request, g
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import db
from app.models import User
from app.utils import success_response, error_response, generate_token
from app.auth.decorators import jwt_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _validate_email(email: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user.
    ---
    tags: [Auth]
    parameters:
      - in: body
        name: body
        schema:
          required: [username, email, password]
          properties:
            username: {type: string}
            email: {type: string}
            password: {type: string}
    responses:
      201:
        description: User created
      400:
        description: Validation error
    """
    data = request.get_json(silent=True)
    if not data:
        return error_response("Invalid JSON body", 400)

    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not username:
        return error_response("Username is required", 400)
    if len(username) > 50:
        return error_response("Username must be 50 characters or fewer", 400)
    if not email:
        return error_response("Email is required", 400)
    if not _validate_email(email):
        return error_response("Invalid email format", 400)
    if not password:
        return error_response("Password is required", 400)
    if len(password) < 6:
        return error_response("Password must be at least 6 characters", 400)

    if User.query.filter_by(username=username).first():
        return error_response("Username already taken", 400)
    if User.query.filter_by(email=email).first():
        return error_response("Email already registered", 400)

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role="user",
    )
    db.session.add(user)
    db.session.commit()
    return success_response(user.to_dict(), 201)


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login and receive a JWT token.
    ---
    tags: [Auth]
    parameters:
      - in: body
        name: body
        schema:
          required: [email, password]
          properties:
            email: {type: string}
            password: {type: string}
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    data = request.get_json(silent=True)
    if not data:
        return error_response("Invalid JSON body", 400)

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email:
        return error_response("Email is required", 400)
    if not password:
        return error_response("Password is required", 400)

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return error_response("Invalid email or password", 401)

    token = generate_token(user.id)
    return success_response({
        "token": token,
        "user_id": user.id,
        "username": user.username,
        "role": user.role,
    })


@auth_bp.route("/me", methods=["GET"])
@jwt_required
def me():
    """
    Get current authenticated user profile.
    ---
    tags: [Auth]
    security:
      - Bearer: []
    responses:
      200:
        description: User profile
      401:
        description: Unauthorized
    """
    return success_response(g.current_user.to_dict())


@auth_bp.route("/logout", methods=["POST"])
@jwt_required
def logout():
    """
    Logout current user.
    ---
    tags: [Auth]
    security:
      - Bearer: []
    responses:
      200:
        description: Logged out
    """
    return success_response({"message": "Logged out successfully"})
