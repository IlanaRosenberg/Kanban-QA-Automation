import json
import pytest
import allure
from app import create_app
from app.database import db as _db
from seed_data.seed import seed_db


@pytest.fixture(scope="function")
def app():
    flask_app = create_app("testing")
    with flask_app.app_context():
        _db.create_all()
        seed_db()
        yield flask_app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def jwt_token(client):
    res = client.post("/api/auth/login",
                      json={"email": "testuser1@kanban.com", "password": "Password123!"})
    data = res.get_json()
    token = data["data"]["token"]
    allure.attach(token, name="JWT Token — testuser1",
                  attachment_type=allure.attachment_type.TEXT)
    return token


@pytest.fixture(scope="function")
def auth_headers(jwt_token):
    return {"Authorization": f"Bearer {jwt_token}"}


@pytest.fixture(scope="function")
def admin_token(client):
    res = client.post("/api/auth/login",
                      json={"email": "admin@kanban.com", "password": "Admin123!"})
    return res.get_json()["data"]["token"]


@pytest.fixture(scope="function")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="function")
def jwt_token_user2(client):
    res = client.post("/api/auth/login",
                      json={"email": "testuser2@kanban.com", "password": "Password123!"})
    return res.get_json()["data"]["token"]


@pytest.fixture(scope="function")
def auth_headers_user2(jwt_token_user2):
    return {"Authorization": f"Bearer {jwt_token_user2}"}


@pytest.fixture(scope="function")
def board_id(client, auth_headers):
    """Create a fresh board and return its ID."""
    res = client.post("/api/boards/", headers=auth_headers,
                      json={"name": "Test Board", "description": "For testing"})
    return res.get_json()["data"]["id"]


def attach_response(res, name="API Response"):
    try:
        body = json.dumps(res.get_json(), indent=2, ensure_ascii=False)
    except Exception:
        body = res.data.decode("utf-8", errors="replace")
    allure.attach(
        f"Status: {res.status_code}\n\n{body}",
        name=name,
        attachment_type=allure.attachment_type.JSON,
    )
