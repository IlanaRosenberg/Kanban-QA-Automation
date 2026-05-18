from flask import Blueprint, request, g
from app.database import db
from app.models import Board, BoardMember, User, Card
from app.utils import success_response, error_response
from app.auth.decorators import jwt_required

boards_bp = Blueprint("boards", __name__, url_prefix="/api/boards")


def _is_board_member(board, user):
    return any(m.user_id == user.id for m in board.members)


def _is_board_admin(board, user):
    if board.owner_id == user.id:
        return True
    for m in board.members:
        if m.user_id == user.id and m.role == "admin":
            return True
    return False


def _get_board_or_404(board_id, user):
    board = db.session.get(Board, board_id)
    if not board:
        return None, error_response("Board not found", 404)
    if not _is_board_member(board, user) and board.owner_id != user.id:
        return None, error_response("Board not found", 404)
    return board, None


@boards_bp.route("/", methods=["POST"])
@jwt_required
def create_board():
    """
    Create a new board.
    ---
    tags: [Boards]
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          required: [name]
          properties:
            name: {type: string}
            description: {type: string}
    responses:
      201:
        description: Board created
      400:
        description: Validation error
    """
    data = request.get_json(silent=True)
    if not data:
        return error_response("Invalid JSON body", 400)

    name = (data.get("name") or "").strip()
    if not name:
        return error_response("Board name is required", 400)
    if len(name) > 120:
        return error_response("Board name must be 120 characters or fewer", 400)

    board = Board(
        name=name,
        description=(data.get("description") or "").strip() or None,
        owner_id=g.current_user.id,
    )
    db.session.add(board)
    db.session.flush()

    # Owner is automatically an admin member
    membership = BoardMember(board_id=board.id, user_id=g.current_user.id, role="admin")
    db.session.add(membership)
    db.session.commit()
    return success_response(board.to_dict(include_members=True), 201)


@boards_bp.route("/", methods=["GET"])
@jwt_required
def list_boards():
    """
    List all boards the current user is a member of.
    ---
    tags: [Boards]
    security:
      - Bearer: []
    responses:
      200:
        description: List of boards
    """
    memberships = BoardMember.query.filter_by(user_id=g.current_user.id).all()
    board_ids = [m.board_id for m in memberships]
    boards = Board.query.filter(Board.id.in_(board_ids)).all()
    return success_response({
        "boards": [b.to_dict() for b in boards],
        "total": len(boards),
    })


@boards_bp.route("/<int:board_id>", methods=["GET"])
@jwt_required
def get_board(board_id):
    """
    Get board detail including members and cards per column.
    ---
    tags: [Boards]
    security:
      - Bearer: []
    responses:
      200:
        description: Board detail
      404:
        description: Board not found
    """
    board, err = _get_board_or_404(board_id, g.current_user)
    if err:
        return err

    cards_by_column = {}
    for card in board.cards:
        cards_by_column.setdefault(card.column, []).append(card.to_dict())

    data = board.to_dict(include_members=True)
    data["columns"] = {
        col: sorted(cards_by_column.get(col, []), key=lambda c: c["position"])
        for col in ["Backlog", "To Do", "In Progress", "In Review", "Done"]
    }
    return success_response(data)


@boards_bp.route("/<int:board_id>", methods=["PATCH"])
@jwt_required
def update_board(board_id):
    """
    Update board name or description. Admin only.
    ---
    tags: [Boards]
    security:
      - Bearer: []
    responses:
      200:
        description: Board updated
      403:
        description: Not an admin
      404:
        description: Board not found
    """
    board, err = _get_board_or_404(board_id, g.current_user)
    if err:
        return err
    if not _is_board_admin(board, g.current_user):
        return error_response("Only board admins can update the board", 403)

    data = request.get_json(silent=True) or {}
    if "name" in data:
        name = (data["name"] or "").strip()
        if not name:
            return error_response("Board name cannot be empty", 400)
        if len(name) > 120:
            return error_response("Board name must be 120 characters or fewer", 400)
        board.name = name
    if "description" in data:
        board.description = (data["description"] or "").strip() or None

    db.session.commit()
    return success_response(board.to_dict())


@boards_bp.route("/<int:board_id>", methods=["DELETE"])
@jwt_required
def delete_board(board_id):
    """
    Delete a board. Only the board owner can delete.
    ---
    tags: [Boards]
    security:
      - Bearer: []
    responses:
      200:
        description: Board deleted
      403:
        description: Not the owner
      404:
        description: Board not found
    """
    board, err = _get_board_or_404(board_id, g.current_user)
    if err:
        return err
    if board.owner_id != g.current_user.id:
        return error_response("Only the board owner can delete it", 403)

    db.session.delete(board)
    db.session.commit()
    return success_response({"message": "Board deleted"})


@boards_bp.route("/<int:board_id>/members", methods=["POST"])
@jwt_required
def add_member(board_id):
    """
    Add a member to a board. Admin only.
    ---
    tags: [Boards]
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          required: [user_id]
          properties:
            user_id: {type: integer}
            role: {type: string, enum: [admin, user]}
    responses:
      201:
        description: Member added
      400:
        description: Already a member or invalid
      403:
        description: Not an admin
      404:
        description: Board or user not found
    """
    board, err = _get_board_or_404(board_id, g.current_user)
    if err:
        return err
    if not _is_board_admin(board, g.current_user):
        return error_response("Only board admins can add members", 403)

    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    if not user_id:
        return error_response("user_id is required", 400)

    target = db.session.get(User, user_id)
    if not target:
        return error_response("User not found", 404)

    if any(m.user_id == user_id for m in board.members):
        return error_response("User is already a member of this board", 400)

    role = data.get("role", "user")
    if role not in ("admin", "user"):
        return error_response("Role must be 'admin' or 'user'", 400)

    membership = BoardMember(board_id=board.id, user_id=user_id, role=role)
    db.session.add(membership)
    db.session.commit()
    return success_response(membership.to_dict(), 201)


@boards_bp.route("/<int:board_id>/members/<int:user_id>", methods=["DELETE"])
@jwt_required
def remove_member(board_id, user_id):
    """
    Remove a member from a board. Admin only.
    ---
    tags: [Boards]
    security:
      - Bearer: []
    responses:
      200:
        description: Member removed
      403:
        description: Not an admin
      404:
        description: Board or member not found
    """
    board, err = _get_board_or_404(board_id, g.current_user)
    if err:
        return err
    if not _is_board_admin(board, g.current_user):
        return error_response("Only board admins can remove members", 403)
    if user_id == board.owner_id:
        return error_response("Cannot remove the board owner", 400)

    membership = BoardMember.query.filter_by(board_id=board_id, user_id=user_id).first()
    if not membership:
        return error_response("Member not found", 404)

    db.session.delete(membership)
    db.session.commit()
    return success_response({"message": "Member removed"})
