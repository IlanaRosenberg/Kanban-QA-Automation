from datetime import datetime, timezone
from flask import Blueprint, request, g
from app.database import db
from app.models import Board, BoardMember, Card, VALID_COLUMNS, COLUMN_ORDER
from app.utils import success_response, error_response
from app.auth.decorators import jwt_required

cards_bp = Blueprint("cards", __name__, url_prefix="/api/boards")


def _get_board_or_404(board_id, user):
    board = db.session.get(Board, board_id)
    if not board:
        return None, error_response("Board not found", 404)
    is_member = any(m.user_id == user.id for m in board.members)
    if not is_member and board.owner_id != user.id:
        return None, error_response("Board not found", 404)
    return board, None


def _is_board_admin(board, user):
    if board.owner_id == user.id:
        return True
    for m in board.members:
        if m.user_id == user.id and m.role == "admin":
            return True
    return False


@cards_bp.route("/<int:board_id>/cards", methods=["POST"])
@jwt_required
def create_card(board_id):
    """
    Create a card on a board.
    ---
    tags: [Cards]
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          required: [title]
          properties:
            title: {type: string}
            description: {type: string}
            column: {type: string}
    responses:
      201:
        description: Card created
      400:
        description: Validation error
      404:
        description: Board not found
    """
    board, err = _get_board_or_404(board_id, g.current_user)
    if err:
        return err

    data = request.get_json(silent=True)
    if not data:
        return error_response("Invalid JSON body", 400)

    title = (data.get("title") or "").strip()
    if not title:
        return error_response("Card title is required", 400)
    if len(title) > 200:
        return error_response("Title must be 200 characters or fewer", 400)

    column = data.get("column", "Backlog")
    if column not in VALID_COLUMNS:
        return error_response(f"Column must be one of: {', '.join(VALID_COLUMNS)}", 400)

    position = Card.query.filter_by(board_id=board_id, column=column).count()

    card = Card(
        title=title,
        description=(data.get("description") or "").strip() or None,
        column=column,
        position=position,
        board_id=board_id,
        creator_id=g.current_user.id,
    )
    db.session.add(card)
    db.session.commit()
    return success_response(card.to_dict(), 201)


@cards_bp.route("/<int:board_id>/cards", methods=["GET"])
@jwt_required
def list_cards(board_id):
    """
    List all cards on a board, optionally filtered by column.
    ---
    tags: [Cards]
    security:
      - Bearer: []
    parameters:
      - in: query
        name: column
        type: string
    responses:
      200:
        description: List of cards
      404:
        description: Board not found
    """
    board, err = _get_board_or_404(board_id, g.current_user)
    if err:
        return err

    column_filter = request.args.get("column")
    if column_filter and column_filter not in VALID_COLUMNS:
        return error_response(f"Invalid column. Must be one of: {', '.join(VALID_COLUMNS)}", 400)

    query = Card.query.filter_by(board_id=board_id)
    if column_filter:
        query = query.filter_by(column=column_filter)

    cards = query.order_by(Card.column, Card.position).all()
    return success_response({
        "cards": [c.to_dict() for c in cards],
        "total": len(cards),
    })


@cards_bp.route("/<int:board_id>/cards/<int:card_id>", methods=["GET"])
@jwt_required
def get_card(board_id, card_id):
    """
    Get a single card detail.
    ---
    tags: [Cards]
    security:
      - Bearer: []
    responses:
      200:
        description: Card detail
      404:
        description: Card or board not found
    """
    board, err = _get_board_or_404(board_id, g.current_user)
    if err:
        return err

    card = Card.query.filter_by(id=card_id, board_id=board_id).first()
    if not card:
        return error_response("Card not found", 404)
    return success_response(card.to_dict())


@cards_bp.route("/<int:board_id>/cards/<int:card_id>", methods=["PATCH"])
@jwt_required
def update_card(board_id, card_id):
    """
    Update a card title, description, or move to another column.
    ---
    tags: [Cards]
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          properties:
            title: {type: string}
            description: {type: string}
            column: {type: string}
    responses:
      200:
        description: Card updated
      400:
        description: Validation error
      403:
        description: Not authorized
      404:
        description: Card or board not found
    """
    board, err = _get_board_or_404(board_id, g.current_user)
    if err:
        return err

    card = Card.query.filter_by(id=card_id, board_id=board_id).first()
    if not card:
        return error_response("Card not found", 404)

    is_member = any(m.user_id == g.current_user.id for m in board.members)
    if not is_member and board.owner_id != g.current_user.id:
        return error_response("Only board members can edit cards", 403)

    data = request.get_json(silent=True) or {}

    if "title" in data:
        title = (data["title"] or "").strip()
        if not title:
            return error_response("Card title cannot be empty", 400)
        if len(title) > 200:
            return error_response("Title must be 200 characters or fewer", 400)
        card.title = title

    if "description" in data:
        card.description = (data["description"] or "").strip() or None

    if "column" in data:
        new_col = data["column"]
        if new_col not in VALID_COLUMNS:
            return error_response(f"Column must be one of: {', '.join(VALID_COLUMNS)}", 400)
        if new_col != card.column:
            card.column = new_col
            card.position = Card.query.filter_by(board_id=board_id, column=new_col).count() - 1

    card.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return success_response(card.to_dict())


@cards_bp.route("/<int:board_id>/cards/<int:card_id>", methods=["DELETE"])
@jwt_required
def delete_card(board_id, card_id):
    """
    Delete a card. Creator or board admin only.
    ---
    tags: [Cards]
    security:
      - Bearer: []
    responses:
      200:
        description: Card deleted
      403:
        description: Not authorized
      404:
        description: Card or board not found
    """
    board, err = _get_board_or_404(board_id, g.current_user)
    if err:
        return err

    card = Card.query.filter_by(id=card_id, board_id=board_id).first()
    if not card:
        return error_response("Card not found", 404)

    is_admin = _is_board_admin(board, g.current_user)
    is_creator = card.creator_id == g.current_user.id
    if not is_admin and not is_creator:
        return error_response("Only the card creator or board admin can delete this card", 403)

    db.session.delete(card)
    db.session.commit()
    return success_response({"message": "Card deleted"})
