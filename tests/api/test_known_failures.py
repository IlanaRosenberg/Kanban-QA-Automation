"""
Intentional API test failures — 10 known bugs tracked for the Allure report.
Marked xfail(strict=True) so they appear as KNOWN FAILURES (orange) not blocking the suite.
"""
import pytest
import allure
from tests.conftest import attach_response

pytestmark = pytest.mark.api


@allure.feature("Boards")
@allure.story("Known Failures")
class TestBoardKnownFailures:

    @pytest.mark.xfail(strict=True, reason="BUG-001: GET /api/boards/ does not return total_pages for pagination")
    @allure.title("[BUG-001] Board list response lacks total_pages and total_count metadata")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("bug_id", "BUG-001")
    def test_board_list_missing_total_pages_metadata(self, client, auth_headers):
        """
        Expected: GET /api/boards/ returns 'total_pages' and 'page' in the response body.
        Actual:   Response only includes 'boards' list and 'total' count — no pagination metadata.
        """
        res = client.get("/api/boards/", headers=auth_headers)
        attach_response(res, "Board list response")
        data = res.get_json()["data"]
        assert "total_pages" in data and "page" in data, (
            "Pagination metadata (total_pages, page) not present in board list response"
        )

    @pytest.mark.xfail(strict=True, reason="BUG-002: GET /api/boards/ does not support pagination")
    @allure.title("[BUG-002] Board list has no pagination support")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("bug_id", "BUG-002")
    def test_board_list_pagination_not_implemented(self, client, auth_headers):
        """
        Expected: ?page and ?per_page query params to paginate results.
        Actual:   All boards returned at once — no pagination metadata.
        """
        res = client.get("/api/boards/?page=1&per_page=2", headers=auth_headers)
        data = res.get_json()["data"]
        assert "page" in data and "per_page" in data, (
            "Pagination metadata (page, per_page, total_pages) not present in response"
        )

    @pytest.mark.xfail(strict=True, reason="BUG-003: Board has no search/filter by name")
    @allure.title("[BUG-003] Board list has no search by name filter")
    @allure.severity(allure.severity_level.MINOR)
    @allure.label("bug_id", "BUG-003")
    def test_board_search_by_name_not_implemented(self, client, auth_headers):
        """
        Expected: GET /api/boards/?search=Sprint returns only matching boards.
        Actual:   ?search param is silently ignored.
        """
        client.post("/api/boards/", headers=auth_headers, json={"name": "Sprint Alpha"})
        client.post("/api/boards/", headers=auth_headers, json={"name": "Roadmap Q3"})
        res = client.get("/api/boards/?search=Sprint", headers=auth_headers)
        boards = res.get_json()["data"]["boards"]
        assert all("sprint" in b["name"].lower() for b in boards), (
            "Search filter not implemented — all boards returned regardless of name"
        )


@allure.feature("Cards")
@allure.story("Known Failures")
class TestCardKnownFailures:

    @pytest.mark.xfail(strict=True, reason="BUG-004: Card has no due_date field")
    @allure.title("[BUG-004] Cards do not support due_date field")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("bug_id", "BUG-004")
    def test_card_due_date_not_supported(self, client, auth_headers, board_id):
        """
        Expected: POST /api/boards/{id}/cards accepts due_date and returns it.
        Actual:   due_date field is silently ignored and not stored.
        """
        res = client.post(f"/api/boards/{board_id}/cards", headers=auth_headers,
                          json={"title": "Task with deadline", "due_date": "2026-12-31"})
        data = res.get_json()["data"]
        assert "due_date" in data and data["due_date"] == "2026-12-31", (
            "due_date field not supported — cards have no deadline tracking"
        )

    @pytest.mark.xfail(strict=True, reason="BUG-005: Card has no priority field")
    @allure.title("[BUG-005] Cards do not support priority field")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("bug_id", "BUG-005")
    def test_card_priority_not_supported(self, client, auth_headers, board_id):
        """
        Expected: Cards accept priority (low/medium/high) and return it in response.
        Actual:   priority field is ignored — all cards treated equally.
        """
        res = client.post(f"/api/boards/{board_id}/cards", headers=auth_headers,
                          json={"title": "Urgent task", "priority": "high"})
        data = res.get_json()["data"]
        assert "priority" in data and data["priority"] == "high", (
            "Priority field not supported — no way to distinguish urgent from normal tasks"
        )

    @pytest.mark.xfail(strict=True, reason="BUG-006: Card has no assignee field")
    @allure.title("[BUG-006] Cards cannot be assigned to a user")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("bug_id", "BUG-006")
    def test_card_assignee_not_supported(self, client, auth_headers, board_id):
        """
        Expected: Cards accept assignee_id and return assigned user info.
        Actual:   assignee_id is ignored — cards cannot be assigned.
        """
        owner_id = client.get("/api/auth/me", headers=auth_headers).get_json()["data"]["id"]
        res = client.post(f"/api/boards/{board_id}/cards", headers=auth_headers,
                          json={"title": "Assigned task", "assignee_id": owner_id})
        data = res.get_json()["data"]
        assert "assignee_id" in data and data["assignee_id"] == owner_id, (
            "Assignee field not supported — cannot assign cards to team members"
        )

    @pytest.mark.xfail(strict=True, reason="BUG-007: Card has no tag/label field")
    @allure.title("[BUG-007] Cards do not support tags or labels")
    @allure.severity(allure.severity_level.MINOR)
    @allure.label("bug_id", "BUG-007")
    def test_card_tags_not_supported(self, client, auth_headers, board_id):
        """
        Expected: POST /api/boards/{id}/cards accepts 'tags' (list of strings) and returns them.
        Actual:   'tags' field is silently ignored — no labeling system exists.
        """
        res = client.post(f"/api/boards/{board_id}/cards", headers=auth_headers,
                          json={"title": "Tagged task", "tags": ["bug", "urgent"]})
        data = res.get_json()["data"]
        assert "tags" in data and data["tags"] == ["bug", "urgent"], (
            "Tags/labels field not supported — cannot categorize cards"
        )


@allure.feature("Authentication")
@allure.story("Known Failures")
class TestAuthKnownFailures:

    @pytest.mark.xfail(strict=True, reason="BUG-008: Register does not enforce minimum username length")
    @allure.title("[BUG-008] Username accepts single-character values")
    @allure.severity(allure.severity_level.MINOR)
    @allure.label("bug_id", "BUG-008")
    def test_register_single_char_username_accepted(self, client):
        """
        Expected: 400 when username is shorter than 3 characters (minimum length policy).
        Actual:   201 — a 1-character username like 'x' is accepted without validation.
        """
        res = client.post("/api/auth/register", json={
            "username": "x", "email": "short@kanban.com", "password": "Pass123!"
        })
        assert res.status_code == 400, (
            "Expected 400 for single-character username but no minimum length is enforced"
        )

    @pytest.mark.xfail(strict=True, reason="BUG-009: No rate limiting on login endpoint")
    @allure.title("[BUG-009] Login endpoint has no rate limiting")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("bug_id", "BUG-009")
    def test_login_no_rate_limiting(self, client):
        """
        Expected: After N failed login attempts, endpoint returns 429 Too Many Requests.
        Actual:   Unlimited login attempts allowed — brute force not prevented.
        """
        for _ in range(10):
            client.post("/api/auth/login", json={
                "email": "testuser1@kanban.com", "password": "WrongPass!"
            })
        res = client.post("/api/auth/login", json={
            "email": "testuser1@kanban.com", "password": "WrongPass!"
        })
        assert res.status_code == 429, (
            "Expected 429 after repeated failed logins but rate limiting is not implemented"
        )

    @pytest.mark.xfail(strict=True, reason="BUG-010: No endpoint to change password")
    @allure.title("[BUG-010] No change password endpoint exists")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("bug_id", "BUG-010")
    def test_change_password_not_implemented(self, client, auth_headers):
        """
        Expected: PATCH /api/auth/password accepts current_password + new_password.
        Actual:   Endpoint does not exist — users cannot change their password.
        """
        res = client.patch("/api/auth/password", headers=auth_headers, json={
            "current_password": "Password123!", "new_password": "NewPass456!"
        })
        assert res.status_code == 200, (
            "Change password endpoint not implemented — returns 404 or 405"
        )
