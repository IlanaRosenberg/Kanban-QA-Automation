"""API tests for authentication endpoints."""
import pytest
import allure
from tests.conftest import attach_response

pytestmark = [pytest.mark.api, pytest.mark.regression]


@allure.feature("Authentication")
@allure.story("Register")
class TestRegister:
    @pytest.mark.smoke
    @pytest.mark.sanity
    @allure.title("Register new user successfully")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_register_success(self, client):
        res = client.post("/api/auth/register", json={
            "username": "newuser", "email": "new@kanban.com", "password": "Pass123!"
        })
        attach_response(res, "Register response")
        data = res.get_json()
        assert res.status_code == 201
        assert data["success"] is True
        assert data["data"]["username"] == "newuser"
        assert "password" not in data["data"]
        assert "password_hash" not in data["data"]

    @allure.title("Register with duplicate username returns 400")
    @allure.severity(allure.severity_level.NORMAL)
    def test_register_duplicate_username(self, client):
        res = client.post("/api/auth/register", json={
            "username": "testuser1", "email": "unique@kanban.com", "password": "Pass123!"
        })
        attach_response(res, "Duplicate username response")
        assert res.status_code == 400
        assert "username" in res.get_json()["error"].lower()

    @allure.title("Register with duplicate email returns 400")
    @allure.severity(allure.severity_level.NORMAL)
    def test_register_duplicate_email(self, client):
        res = client.post("/api/auth/register", json={
            "username": "uniqueuser", "email": "testuser1@kanban.com", "password": "Pass123!"
        })
        assert res.status_code == 400
        assert "email" in res.get_json()["error"].lower()

    @allure.title("Register without username returns 400")
    @allure.severity(allure.severity_level.MINOR)
    def test_register_missing_username(self, client):
        res = client.post("/api/auth/register", json={"email": "a@b.com", "password": "Pass123!"})
        assert res.status_code == 400

    @allure.title("Register without email returns 400")
    @allure.severity(allure.severity_level.MINOR)
    def test_register_missing_email(self, client):
        res = client.post("/api/auth/register", json={"username": "someone", "password": "Pass123!"})
        assert res.status_code == 400

    @allure.title("Register without password returns 400")
    @allure.severity(allure.severity_level.MINOR)
    def test_register_missing_password(self, client):
        res = client.post("/api/auth/register", json={"username": "someone", "email": "s@b.com"})
        assert res.status_code == 400

    @allure.title("Register with short password returns 400")
    @allure.severity(allure.severity_level.MINOR)
    def test_register_short_password(self, client):
        res = client.post("/api/auth/register", json={
            "username": "someone", "email": "s@b.com", "password": "abc"
        })
        assert res.status_code == 400

    @allure.title("Register with invalid email format returns 400")
    @allure.severity(allure.severity_level.MINOR)
    def test_register_invalid_email(self, client):
        res = client.post("/api/auth/register", json={
            "username": "someone", "email": "not-an-email", "password": "Pass123!"
        })
        assert res.status_code == 400


@allure.feature("Authentication")
@allure.story("Login")
class TestLogin:
    @pytest.mark.smoke
    @pytest.mark.sanity
    @allure.title("Login with valid credentials returns JWT token")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_login_success(self, client):
        res = client.post("/api/auth/login", json={
            "email": "testuser1@kanban.com", "password": "Password123!"
        })
        attach_response(res, "Login response")
        data = res.get_json()
        assert res.status_code == 200
        assert data["success"] is True
        assert "token" in data["data"]
        assert data["data"]["username"] == "testuser1"
        assert data["data"]["role"] == "user"

    @allure.title("Login with wrong password returns 401")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_wrong_password(self, client):
        res = client.post("/api/auth/login", json={
            "email": "testuser1@kanban.com", "password": "WrongPass!"
        })
        assert res.status_code == 401
        assert res.get_json()["success"] is False

    @allure.title("Login with non-existent email returns 401")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_nonexistent_user(self, client):
        res = client.post("/api/auth/login", json={
            "email": "ghost@kanban.com", "password": "Password123!"
        })
        assert res.status_code == 401

    @allure.title("Login without email returns 400")
    @allure.severity(allure.severity_level.MINOR)
    def test_login_missing_email(self, client):
        res = client.post("/api/auth/login", json={"password": "Password123!"})
        assert res.status_code == 400

    @allure.title("Login without password returns 400")
    @allure.severity(allure.severity_level.MINOR)
    def test_login_missing_password(self, client):
        res = client.post("/api/auth/login", json={"email": "testuser1@kanban.com"})
        assert res.status_code == 400

    @allure.title("Admin login returns role=admin")
    @allure.severity(allure.severity_level.NORMAL)
    def test_admin_login_returns_admin_role(self, client):
        res = client.post("/api/auth/login", json={
            "email": "admin@kanban.com", "password": "Admin123!"
        })
        data = res.get_json()
        assert res.status_code == 200
        assert data["data"]["role"] == "admin"


@allure.feature("Authentication")
@allure.story("Current User")
class TestGetMe:
    @pytest.mark.smoke
    @pytest.mark.sanity
    @allure.title("GET /me returns authenticated user profile")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_me_success(self, client, auth_headers):
        res = client.get("/api/auth/me", headers=auth_headers)
        attach_response(res, "GET /me response")
        data = res.get_json()
        assert res.status_code == 200
        assert data["data"]["username"] == "testuser1"
        assert data["data"]["email"] == "testuser1@kanban.com"

    @allure.title("GET /me without token returns 401")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_me_unauthenticated(self, client):
        res = client.get("/api/auth/me")
        assert res.status_code == 401


@allure.feature("Authentication")
@allure.story("Logout")
class TestLogout:
    @allure.title("Logout with valid token returns 200")
    @allure.severity(allure.severity_level.NORMAL)
    def test_logout_success(self, client, auth_headers):
        res = client.post("/api/auth/logout", headers=auth_headers)
        assert res.status_code == 200
        assert res.get_json()["success"] is True

    @allure.title("Logout without token returns 401")
    @allure.severity(allure.severity_level.NORMAL)
    def test_logout_no_token(self, client):
        res = client.post("/api/auth/logout")
        assert res.status_code == 401
