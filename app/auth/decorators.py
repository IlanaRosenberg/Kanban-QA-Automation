import jwt
from functools import wraps
from flask import request, g, current_app
from app.utils import error_response


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return error_response("Missing or invalid Authorization header", 401)
        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return error_response("Token has expired", 401)
        except jwt.InvalidTokenError:
            return error_response("Invalid token", 401)
        from app.models import User
        user = db_get_user(payload["user_id"])
        if not user:
            return error_response("User not found", 401)
        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    @jwt_required
    def decorated(*args, **kwargs):
        if g.current_user.role != "admin":
            return error_response("Admin access required", 403)
        return f(*args, **kwargs)
    return decorated


def db_get_user(user_id):
    from app.models import User
    from app.database import db
    return db.session.get(User, user_id)
