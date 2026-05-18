from werkzeug.security import generate_password_hash
from app.models import User, Board, BoardMember, Card
from app.database import db


def seed_db():
    # Users
    users_data = [
        {"username": "adminuser", "email": "admin@kanban.com", "password": "Admin123!", "role": "admin"},
        {"username": "testuser1", "email": "testuser1@kanban.com", "password": "Password123!", "role": "user"},
        {"username": "testuser2", "email": "testuser2@kanban.com", "password": "Password123!", "role": "user"},
    ]
    created_users = {}
    for u in users_data:
        existing = User.query.filter_by(email=u["email"]).first()
        if not existing:
            user = User(
                username=u["username"],
                email=u["email"],
                password_hash=generate_password_hash(u["password"]),
                role=u["role"],
            )
            db.session.add(user)
            db.session.flush()
            created_users[u["username"]] = user
        else:
            created_users[u["username"]] = existing

    # Boards
    boards_data = [
        {
            "name": "Sprint 1 — Backend",
            "description": "API development tasks for sprint 1",
            "owner": "adminuser",
            "members": [("testuser1", "user"), ("testuser2", "user")],
            "cards": [
                # Done (20)
                ("Set up Flask project", "Initialize repo and install deps", "Done"),
                ("Design database schema", "ERD for users, boards, cards", "Done"),
                ("Create virtual environment", "Set up venv and requirements.txt", "Done"),
                ("Configure SQLAlchemy", "Connect Flask to SQLite database", "Done"),
                ("Implement User model", "Fields: id, username, email, password_hash, role", "Done"),
                ("Implement Board model", "Fields: id, name, description, owner_id", "Done"),
                ("Implement Card model", "Fields: id, title, column, position, board_id", "Done"),
                ("Implement BoardMember model", "Pivot table for board membership", "Done"),
                ("Set up blueprints", "Auth, boards, cards, users blueprints", "Done"),
                ("Implement register endpoint", "POST /api/auth/register with validation", "Done"),
                ("Implement login endpoint", "POST /api/auth/login returning JWT", "Done"),
                ("Implement JWT decorator", "jwt_required and admin_required decorators", "Done"),
                ("Implement /me endpoint", "GET /api/auth/me returns current user", "Done"),
                ("Implement logout endpoint", "POST /api/auth/logout clears session", "Done"),
                ("Add password hashing", "Using werkzeug generate_password_hash", "Done"),
                ("Implement board list endpoint", "GET /api/boards/ filtered by membership", "Done"),
                ("Implement board create endpoint", "POST /api/boards/ with owner auto-admin", "Done"),
                ("Implement board delete endpoint", "DELETE /api/boards/:id owner only", "Done"),
                ("Add cascade delete for cards", "Deleting board removes all its cards", "Done"),
                ("Write seed data script", "Populate DB with users, boards and cards", "Done"),
                # In Review
                ("Implement auth endpoints", "Register, login, logout, /me", "In Review"),
                # In Progress
                ("Write board API", "CRUD for boards and members", "In Progress"),
                # To Do
                ("Write card API", "CRUD for cards with column logic", "To Do"),
                # Backlog (12)
                ("Add Swagger docs", "Document all endpoints with flasgger", "Backlog"),
                ("Implement card list endpoint", "GET /api/boards/:id/cards with column filter", "Backlog"),
                ("Implement card create endpoint", "POST /api/boards/:id/cards", "Backlog"),
                ("Implement card move endpoint", "PATCH /api/boards/:id/cards/:id", "Backlog"),
                ("Implement card delete endpoint", "DELETE /api/boards/:id/cards/:id", "Backlog"),
                ("Add member management endpoints", "POST/DELETE /api/boards/:id/members", "Backlog"),
                ("Add input validation layer", "Validate all request bodies", "Backlog"),
                ("Add error handling middleware", "Global error handlers for 404, 500", "Backlog"),
                ("Add CORS support", "Allow frontend requests from different origin", "Backlog"),
                ("Write integration tests", "End-to-end API flow tests", "Backlog"),
                ("Set up CI pipeline", "GitHub Actions for automated testing", "Backlog"),
                ("Add rate limiting to login", "Prevent brute-force attacks", "Backlog"),
            ],
        },
        {
            "name": "QA Automation Project",
            "description": "Test planning and automation tasks",
            "owner": "testuser1",
            "members": [("testuser2", "user")],
            "cards": [
                # Done (15)
                ("Write API test plan", "Define scope and test cases", "Done"),
                ("Implement auth tests", "pytest tests for login/register", "Done"),
                ("Implement board tests", "pytest tests for board CRUD", "Done"),
                ("Implement card tests", "pytest tests for card workflow", "Done"),
                ("Set up Allure reporting", "Configure allure-pytest plugin", "Done"),
                ("Set up Selenium POM", "Page objects for UI testing", "Done"),
                ("Write login UI tests", "Selenium tests for login page", "Done"),
                ("Write register UI tests", "Selenium tests for register page", "Done"),
                ("Write boards UI tests", "Selenium tests for boards list page", "Done"),
                ("Write cards UI tests", "Selenium tests for board detail page", "Done"),
                ("Write end-to-end tests", "Full workflow integration tests", "Done"),
                ("Document known bugs as xfail", "10 known limitations as xfail tests", "Done"),
                ("Set up test fixtures", "conftest.py with in-memory DB fixtures", "Done"),
                ("Add Allure severity levels", "BLOCKER, CRITICAL, NORMAL, MINOR labels", "Done"),
                ("Create Postman collection", "Export all API endpoints to Postman", "Done"),
                # In Progress
                ("Implement board tests", "pytest tests for board CRUD", "In Progress"),
                # To Do
                ("Implement card tests", "pytest tests for card workflow", "To Do"),
                # Backlog (15)
                ("Add visual regression tests", "Screenshot comparison tests", "Backlog"),
                ("Add performance tests", "Response time assertions on API", "Backlog"),
                ("Add security tests", "SQL injection and XSS basic checks", "Backlog"),
                ("Add accessibility tests", "WCAG compliance checks", "Backlog"),
                ("Add cross-browser tests", "Firefox and Edge compatibility", "Backlog"),
                ("Add mobile viewport tests", "Responsive layout testing", "Backlog"),
                ("Add load testing", "Simulate concurrent users with locust", "Backlog"),
                ("Set up test data factory", "Dynamic test data generation", "Backlog"),
                ("Add contract testing", "API schema validation tests", "Backlog"),
                ("Add mutation testing", "Verify test quality with mutmut", "Backlog"),
                ("Add code coverage report", "pytest-cov HTML report generation", "Backlog"),
                ("Integrate with CI/CD", "GitHub Actions test pipeline", "Backlog"),
                ("Add Slack notifications", "Notify team on test failures", "Backlog"),
                ("Write test strategy doc", "Document overall QA approach", "Backlog"),
                ("Add retry logic for flaky tests", "pytest-rerunfailures for unstable tests", "Backlog"),
            ],
        },
    ]

    for b_data in boards_data:
        owner = created_users[b_data["owner"]]
        existing_board = Board.query.filter_by(name=b_data["name"], owner_id=owner.id).first()
        if existing_board:
            continue

        board = Board(name=b_data["name"], description=b_data["description"], owner_id=owner.id)
        db.session.add(board)
        db.session.flush()

        # Owner membership
        db.session.add(BoardMember(board_id=board.id, user_id=owner.id, role="admin"))

        # Other members
        for (uname, role) in b_data["members"]:
            member = created_users.get(uname)
            if member:
                db.session.add(BoardMember(board_id=board.id, user_id=member.id, role=role))

        # Cards
        col_counts = {}
        for (title, desc, col) in b_data["cards"]:
            pos = col_counts.get(col, 0)
            col_counts[col] = pos + 1
            db.session.add(Card(
                title=title,
                description=desc,
                column=col,
                position=pos,
                board_id=board.id,
                creator_id=owner.id,
            ))

    db.session.commit()
