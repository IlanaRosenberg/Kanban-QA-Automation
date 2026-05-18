from datetime import datetime, timezone
from app.database import db

VALID_COLUMNS = ["Backlog", "To Do", "In Progress", "In Review", "Done"]
COLUMN_ORDER = {col: i for i, col in enumerate(VALID_COLUMNS)}


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")  # admin | user
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    boards_owned = db.relationship("Board", back_populates="owner", cascade="all, delete-orphan")
    memberships = db.relationship("BoardMember", back_populates="user", cascade="all, delete-orphan")
    cards = db.relationship("Card", back_populates="creator", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
        }


class Board(db.Model):
    __tablename__ = "boards"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    owner = db.relationship("User", back_populates="boards_owned")
    members = db.relationship("BoardMember", back_populates="board", cascade="all, delete-orphan")
    cards = db.relationship("Card", back_populates="board", cascade="all, delete-orphan")

    def to_dict(self, include_members=False):
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat(),
            "member_count": len(self.members),
        }
        if include_members:
            data["members"] = [m.to_dict() for m in self.members]
        return data


class BoardMember(db.Model):
    __tablename__ = "board_members"

    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey("boards.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")  # admin | user

    board = db.relationship("Board", back_populates="members")
    user = db.relationship("User", back_populates="memberships")

    def to_dict(self):
        return {
            "id": self.id,
            "board_id": self.board_id,
            "user_id": self.user_id,
            "username": self.user.username,
            "role": self.role,
        }


class Card(db.Model):
    __tablename__ = "cards"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    column = db.Column(db.String(50), nullable=False, default="Backlog")
    position = db.Column(db.Integer, nullable=False, default=0)
    board_id = db.Column(db.Integer, db.ForeignKey("boards.id"), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    board = db.relationship("Board", back_populates="cards")
    creator = db.relationship("User", back_populates="cards")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "column": self.column,
            "position": self.position,
            "board_id": self.board_id,
            "creator_id": self.creator_id,
            "creator_username": self.creator.username,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
