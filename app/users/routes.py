from flask import Blueprint, g
from app.models import User
from app.utils import success_response, error_response
from app.auth.decorators import jwt_required

users_bp = Blueprint("users", __name__, url_prefix="/api/users")


@users_bp.route("/", methods=["GET"])
@jwt_required
def list_users():
    """
    List all users (admin only).
    ---
    tags: [Users]
    security:
      - Bearer: []
    responses:
      200:
        description: List of users
      403:
        description: Admin required
    """
    if g.current_user.role != "admin":
        return error_response("Admin access required", 403)
    users = User.query.all()
    return success_response({"users": [u.to_dict() for u in users], "total": len(users)})


@users_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required
def get_user(user_id):
    """
    Get a user by ID.
    ---
    tags: [Users]
    security:
      - Bearer: []
    responses:
      200:
        description: User profile
      404:
        description: User not found
    """
    from app.database import db
    user = db.session.get(User, user_id)
    if not user:
        return error_response("User not found", 404)
    return success_response(user.to_dict())
