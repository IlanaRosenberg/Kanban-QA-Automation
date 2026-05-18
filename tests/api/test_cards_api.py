"""API tests for card endpoints."""
import pytest
import allure
from tests.conftest import attach_response

pytestmark = [pytest.mark.api, pytest.mark.regression]

VALID_COLUMNS = ["Backlog", "To Do", "In Progress", "In Review", "Done"]


@allure.feature("Cards")
@allure.story("Create Card")
class TestCreateCard:
    @pytest.mark.smoke
    @pytest.mark.sanity
    @allure.title("Create card with valid data returns 201")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_create_card_success(self, client, auth_headers, board_id):
        res = client.post(f"/api/boards/{board_id}/cards", headers=auth_headers,
                          json={"title": "Fix login bug", "description": "Error on login", "column": "To Do"})
        attach_response(res, "Create card response")
        data = res.get_json()
        assert res.status_code == 201
        assert data["success"] is True
        assert data["data"]["title"] == "Fix login bug"
        assert data["data"]["column"] == "To Do"
        assert data["data"]["board_id"] == board_id

    @allure.title("Card defaults to Backlog column when column not specified")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_card_defaults_to_backlog(self, client, auth_headers, board_id):
        res = client.post(f"/api/boards/{board_id}/cards", headers=auth_headers,
                          json={"title": "No column card"})
        assert res.status_code == 201
        assert res.get_json()["data"]["column"] == "Backlog"

    @allure.title("Create card without title returns 400")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_card_missing_title(self, client, auth_headers, board_id):
        res = client.post(f"/api/boards/{board_id}/cards", headers=auth_headers,
                          json={"description": "No title"})
        assert res.status_code == 400

    @allure.title("Create card with invalid column returns 400")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_card_invalid_column(self, client, auth_headers, board_id):
        res = client.post(f"/api/boards/{board_id}/cards", headers=auth_headers,
                          json={"title": "Bad column", "column": "Flying"})
        assert res.status_code == 400
        assert "column" in res.get_json()["error"].lower()

    @allure.title("Create card on non-existent board returns 404")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_card_board_not_found(self, client, auth_headers):
        res = client.post("/api/boards/99999/cards", headers=auth_headers,
                          json={"title": "Orphan card"})
        assert res.status_code == 404

    @allure.title("Create card without token returns 401")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_card_unauthenticated(self, client, board_id):
        res = client.post(f"/api/boards/{board_id}/cards", json={"title": "Sneaky"})
        assert res.status_code == 401

    @pytest.mark.parametrize("col", VALID_COLUMNS)
    @allure.title("Can create card in each valid column")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_card_in_each_valid_column(self, client, auth_headers, board_id, col):
        res = client.post(f"/api/boards/{board_id}/cards", headers=auth_headers,
                          json={"title": f"Card in {col}", "column": col})
        assert res.status_code == 201
        assert res.get_json()["data"]["column"] == col


@allure.feature("Cards")
@allure.story("List Cards")
class TestListCards:
    @allure.title("List all cards on a board")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_list_cards_success(self, client, auth_headers, board_id):
        client.post(f"/api/boards/{board_id}/cards", headers=auth_headers,
                    json={"title": "Card 1", "column": "To Do"})
        client.post(f"/api/boards/{board_id}/cards", headers=auth_headers,
                    json={"title": "Card 2", "column": "Done"})
        res = client.get(f"/api/boards/{board_id}/cards", headers=auth_headers)
        data = res.get_json()
        assert res.status_code == 200
        assert data["data"]["total"] == 2

    @allure.title("Filter cards by column")
    @allure.severity(allure.severity_level.NORMAL)
    def test_list_cards_filter_by_column(self, client, auth_headers, board_id):
        client.post(f"/api/boards/{board_id}/cards", headers=auth_headers,
                    json={"title": "Card A", "column": "To Do"})
        client.post(f"/api/boards/{board_id}/cards", headers=auth_headers,
                    json={"title": "Card B", "column": "Done"})
        res = client.get(f"/api/boards/{board_id}/cards?column=To Do", headers=auth_headers)
        cards = res.get_json()["data"]["cards"]
        assert all(c["column"] == "To Do" for c in cards)

    @allure.title("Filter cards with invalid column returns 400")
    @allure.severity(allure.severity_level.MINOR)
    def test_list_cards_invalid_column_filter(self, client, auth_headers, board_id):
        res = client.get(f"/api/boards/{board_id}/cards?column=Invalid", headers=auth_headers)
        assert res.status_code == 400


@allure.feature("Cards")
@allure.story("Update Card — Move Between Columns")
class TestMoveCard:
    @pytest.mark.smoke
    @pytest.mark.sanity
    @allure.title("Move card from Backlog to In Progress")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_move_card_success(self, client, auth_headers, board_id):
        card_id = client.post(f"/api/boards/{board_id}/cards", headers=auth_headers,
                              json={"title": "Move me", "column": "Backlog"}).get_json()["data"]["id"]
        res = client.patch(f"/api/boards/{board_id}/cards/{card_id}", headers=auth_headers,
                           json={"column": "In Progress"})
        attach_response(res, "Move card response")
        assert res.status_code == 200
        assert res.get_json()["data"]["column"] == "In Progress"

    @allure.title("Move card to invalid column returns 400")
    @allure.severity(allure.severity_level.NORMAL)
    def test_move_card_invalid_column(self, client, auth_headers, board_id):
        card_id = client.post(f"/api/boards/{board_id}/cards", headers=auth_headers,
                              json={"title": "Bad move", "column": "Backlog"}).get_json()["data"]["id"]
        res = client.patch(f"/api/boards/{board_id}/cards/{card_id}", headers=auth_headers,
                           json={"column": "Completed"})
        assert res.status_code == 400

    @allure.title("Update card title")
    @allure.severity(allure.severity_level.NORMAL)
    def test_update_card_title(self, client, auth_headers, board_id):
        card_id = client.post(f"/api/boards/{board_id}/cards", headers=auth_headers,
                              json={"title": "Old title"}).get_json()["data"]["id"]
        res = client.patch(f"/api/boards/{board_id}/cards/{card_id}", headers=auth_headers,
                           json={"title": "New title"})
        assert res.status_code == 200
        assert res.get_json()["data"]["title"] == "New title"

    @allure.title("Update card with empty title returns 400")
    @allure.severity(allure.severity_level.MINOR)
    def test_update_card_empty_title(self, client, auth_headers, board_id):
        card_id = client.post(f"/api/boards/{board_id}/cards", headers=auth_headers,
                              json={"title": "Title"}).get_json()["data"]["id"]
        res = client.patch(f"/api/boards/{board_id}/cards/{card_id}", headers=auth_headers,
                           json={"title": ""})
        assert res.status_code == 400

    @allure.title("Non-member cannot update card")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_update_card_unauthorized_user(self, client, auth_headers, auth_headers_user2, board_id):
        # user1 creates card (user2 is NOT a member)
        card_id = client.post(f"/api/boards/{board_id}/cards", headers=auth_headers,
                              json={"title": "Protected card"}).get_json()["data"]["id"]
        # user2 (non-member) tries to edit — gets 404 because board is invisible to non-members
        res = client.patch(f"/api/boards/{board_id}/cards/{card_id}", headers=auth_headers_user2,
                           json={"title": "Hacked"})
        assert res.status_code == 404


@allure.feature("Cards")
@allure.story("Delete Card")
class TestDeleteCard:
    @allure.title("Creator can delete their own card")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_card_success(self, client, auth_headers, board_id):
        card_id = client.post(f"/api/boards/{board_id}/cards", headers=auth_headers,
                              json={"title": "Delete me"}).get_json()["data"]["id"]
        res = client.delete(f"/api/boards/{board_id}/cards/{card_id}", headers=auth_headers)
        assert res.status_code == 200
        res2 = client.get(f"/api/boards/{board_id}/cards/{card_id}", headers=auth_headers)
        assert res2.status_code == 404

    @allure.title("Non-creator non-admin cannot delete card")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_card_unauthorized(self, client, auth_headers, auth_headers_user2, board_id):
        user2_id = client.get("/api/auth/me", headers=auth_headers_user2).get_json()["data"]["id"]
        client.post(f"/api/boards/{board_id}/members", headers=auth_headers,
                    json={"user_id": user2_id, "role": "user"})
        card_id = client.post(f"/api/boards/{board_id}/cards", headers=auth_headers,
                              json={"title": "Safe card"}).get_json()["data"]["id"]
        res = client.delete(f"/api/boards/{board_id}/cards/{card_id}", headers=auth_headers_user2)
        assert res.status_code == 403

    @allure.title("Delete non-existent card returns 404")
    @allure.severity(allure.severity_level.MINOR)
    def test_delete_card_not_found(self, client, auth_headers, board_id):
        res = client.delete(f"/api/boards/{board_id}/cards/99999", headers=auth_headers)
        assert res.status_code == 404
