"""API tests for board endpoints."""
import pytest
import allure
from tests.conftest import attach_response

pytestmark = [pytest.mark.api, pytest.mark.regression]


@allure.feature("Boards")
@allure.story("Create Board")
class TestCreateBoard:
    @pytest.mark.smoke
    @pytest.mark.sanity
    @allure.title("Create board with valid data returns 201")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_create_board_success(self, client, auth_headers):
        res = client.post("/api/boards/", headers=auth_headers,
                          json={"name": "My Board", "description": "Test board"})
        attach_response(res, "Create board response")
        data = res.get_json()
        assert res.status_code == 201
        assert data["success"] is True
        assert data["data"]["name"] == "My Board"
        assert data["data"]["owner_id"] is not None

    @allure.title("Creator is automatically an admin member of the board")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_board_creator_is_admin_member(self, client, auth_headers):
        res = client.post("/api/boards/", headers=auth_headers, json={"name": "Board X"})
        data = res.get_json()["data"]
        assert data["member_count"] == 1
        members = data["members"]
        assert members[0]["role"] == "admin"

    @allure.title("Create board without name returns 400")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_board_missing_name(self, client, auth_headers):
        res = client.post("/api/boards/", headers=auth_headers, json={"description": "No name"})
        assert res.status_code == 400
        assert res.get_json()["success"] is False

    @allure.title("Create board without token returns 401")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_board_unauthenticated(self, client):
        res = client.post("/api/boards/", json={"name": "Sneaky"})
        assert res.status_code == 401

    @allure.title("Create board with empty name returns 400")
    @allure.severity(allure.severity_level.MINOR)
    def test_create_board_empty_name(self, client, auth_headers):
        res = client.post("/api/boards/", headers=auth_headers, json={"name": "   "})
        assert res.status_code == 400


@allure.feature("Boards")
@allure.story("List Boards")
class TestListBoards:
    @pytest.mark.smoke
    @pytest.mark.sanity
    @allure.title("List boards returns only boards user is a member of")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_list_boards_returns_own_boards(self, client, auth_headers):
        res = client.get("/api/boards/", headers=auth_headers)
        attach_response(res, "List boards response")
        data = res.get_json()
        assert res.status_code == 200
        assert data["success"] is True
        assert isinstance(data["data"]["boards"], list)
        assert data["data"]["total"] >= 1

    @allure.title("List boards without token returns 401")
    @allure.severity(allure.severity_level.NORMAL)
    def test_list_boards_unauthenticated(self, client):
        res = client.get("/api/boards/")
        assert res.status_code == 401

    @allure.title("User only sees boards they belong to")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_list_boards_isolation(self, client, auth_headers, auth_headers_user2):
        """Bug-catcher: user2 must not see boards they were not added to."""
        client.post("/api/boards/", headers=auth_headers,
                    json={"name": "Private Board of User1"})
        res = client.get("/api/boards/", headers=auth_headers_user2)
        board_names = [b["name"] for b in res.get_json()["data"]["boards"]]
        assert "Private Board of User1" not in board_names


@allure.feature("Boards")
@allure.story("Get Board Detail")
class TestGetBoard:
    @allure.title("Get board detail returns columns and cards")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_board_detail_success(self, client, auth_headers, board_id):
        res = client.get(f"/api/boards/{board_id}", headers=auth_headers)
        attach_response(res, "Get board response")
        data = res.get_json()["data"]
        assert res.status_code == 200
        assert "columns" in data
        assert set(data["columns"].keys()) == {"Backlog", "To Do", "In Progress", "In Review", "Done"}

    @allure.title("Get non-existent board returns 404")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_board_not_found(self, client, auth_headers):
        res = client.get("/api/boards/99999", headers=auth_headers)
        assert res.status_code == 404

    @allure.title("Non-member cannot access board")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_board_non_member_gets_404(self, client, auth_headers, auth_headers_user2):
        res = client.post("/api/boards/", headers=auth_headers, json={"name": "Secret"})
        bid = res.get_json()["data"]["id"]
        res2 = client.get(f"/api/boards/{bid}", headers=auth_headers_user2)
        assert res2.status_code == 404


@allure.feature("Boards")
@allure.story("Update Board")
class TestUpdateBoard:
    @allure.title("Admin can update board name")
    @allure.severity(allure.severity_level.NORMAL)
    def test_update_board_name_success(self, client, auth_headers, board_id):
        res = client.patch(f"/api/boards/{board_id}", headers=auth_headers,
                           json={"name": "Updated Name"})
        assert res.status_code == 200
        assert res.get_json()["data"]["name"] == "Updated Name"

    @allure.title("Non-admin member cannot update board")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_update_board_non_admin_forbidden(self, client, auth_headers, auth_headers_user2, board_id):
        # Add user2 as regular user
        user2_id = client.get("/api/auth/me", headers=auth_headers_user2).get_json()["data"]["id"]
        client.post(f"/api/boards/{board_id}/members", headers=auth_headers,
                    json={"user_id": user2_id, "role": "user"})
        res = client.patch(f"/api/boards/{board_id}", headers=auth_headers_user2,
                           json={"name": "Hacked"})
        assert res.status_code == 403

    @allure.title("Update board with empty name returns 400")
    @allure.severity(allure.severity_level.MINOR)
    def test_update_board_empty_name(self, client, auth_headers, board_id):
        res = client.patch(f"/api/boards/{board_id}", headers=auth_headers, json={"name": ""})
        assert res.status_code == 400


@allure.feature("Boards")
@allure.story("Delete Board")
class TestDeleteBoard:
    @allure.title("Owner can delete board")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_board_success(self, client, auth_headers, board_id):
        res = client.delete(f"/api/boards/{board_id}", headers=auth_headers)
        assert res.status_code == 200
        # Verify it's gone
        res2 = client.get(f"/api/boards/{board_id}", headers=auth_headers)
        assert res2.status_code == 404

    @allure.title("Non-owner cannot delete board")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_board_non_owner_forbidden(self, client, auth_headers, auth_headers_user2, board_id):
        user2_id = client.get("/api/auth/me", headers=auth_headers_user2).get_json()["data"]["id"]
        client.post(f"/api/boards/{board_id}/members", headers=auth_headers,
                    json={"user_id": user2_id, "role": "admin"})
        res = client.delete(f"/api/boards/{board_id}", headers=auth_headers_user2)
        assert res.status_code == 403

    @allure.title("Delete non-existent board returns 404")
    @allure.severity(allure.severity_level.MINOR)
    def test_delete_board_not_found(self, client, auth_headers):
        res = client.delete("/api/boards/99999", headers=auth_headers)
        assert res.status_code == 404


@allure.feature("Boards")
@allure.story("Board Members")
class TestBoardMembers:
    @allure.title("Admin can add a member to board")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_member_success(self, client, auth_headers, auth_headers_user2, board_id):
        user2_id = client.get("/api/auth/me", headers=auth_headers_user2).get_json()["data"]["id"]
        res = client.post(f"/api/boards/{board_id}/members", headers=auth_headers,
                          json={"user_id": user2_id, "role": "user"})
        assert res.status_code == 201
        assert res.get_json()["data"]["role"] == "user"

    @allure.title("Cannot add the same member twice")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_member_duplicate(self, client, auth_headers, auth_headers_user2, board_id):
        user2_id = client.get("/api/auth/me", headers=auth_headers_user2).get_json()["data"]["id"]
        client.post(f"/api/boards/{board_id}/members", headers=auth_headers,
                    json={"user_id": user2_id, "role": "user"})
        res = client.post(f"/api/boards/{board_id}/members", headers=auth_headers,
                          json={"user_id": user2_id, "role": "user"})
        assert res.status_code == 400

    @allure.title("Non-admin cannot add members")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_member_non_admin_forbidden(self, client, auth_headers, auth_headers_user2, board_id):
        user2_id = client.get("/api/auth/me", headers=auth_headers_user2).get_json()["data"]["id"]
        client.post(f"/api/boards/{board_id}/members", headers=auth_headers,
                    json={"user_id": user2_id, "role": "user"})
        # user2 (member) tries to add themselves as admin
        admin_id = client.get("/api/auth/me", headers=auth_headers).get_json()["data"]["id"]
        res = client.post(f"/api/boards/{board_id}/members", headers=auth_headers_user2,
                          json={"user_id": admin_id, "role": "admin"})
        assert res.status_code == 403

    @allure.title("Admin can remove a member")
    @allure.severity(allure.severity_level.NORMAL)
    def test_remove_member_success(self, client, auth_headers, auth_headers_user2, board_id):
        user2_id = client.get("/api/auth/me", headers=auth_headers_user2).get_json()["data"]["id"]
        client.post(f"/api/boards/{board_id}/members", headers=auth_headers,
                    json={"user_id": user2_id, "role": "user"})
        res = client.delete(f"/api/boards/{board_id}/members/{user2_id}", headers=auth_headers)
        assert res.status_code == 200

    @allure.title("Cannot remove the board owner")
    @allure.severity(allure.severity_level.NORMAL)
    def test_cannot_remove_owner(self, client, auth_headers, board_id):
        owner_id = client.get("/api/auth/me", headers=auth_headers).get_json()["data"]["id"]
        res = client.delete(f"/api/boards/{board_id}/members/{owner_id}", headers=auth_headers)
        assert res.status_code == 400
