"""End-to-end integration tests — full user journeys through the API."""
import pytest
import allure

pytestmark = [pytest.mark.integration, pytest.mark.sanity, pytest.mark.regression]


@allure.feature("End-to-End Flows")
@allure.story("Full User Journey")
class TestFullUserJourney:
    @allure.title("Register → login → create board → add card → move card → delete card")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_full_kanban_workflow(self, client):
        # Register
        reg = client.post("/api/auth/register", json={
            "username": "e2euser", "email": "e2e@kanban.com", "password": "E2EPass123!"
        })
        assert reg.status_code == 201

        # Login
        login = client.post("/api/auth/login", json={
            "email": "e2e@kanban.com", "password": "E2EPass123!"
        })
        assert login.status_code == 200
        token = login.get_json()["data"]["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create board
        board = client.post("/api/boards/", headers=headers,
                            json={"name": "E2E Board", "description": "Full workflow test"})
        assert board.status_code == 201
        board_id = board.get_json()["data"]["id"]

        # Create card in Backlog
        card = client.post(f"/api/boards/{board_id}/cards", headers=headers,
                           json={"title": "E2E Task", "column": "Backlog"})
        assert card.status_code == 201
        card_id = card.get_json()["data"]["id"]
        assert card.get_json()["data"]["column"] == "Backlog"

        # Move card: Backlog → To Do
        move1 = client.patch(f"/api/boards/{board_id}/cards/{card_id}", headers=headers,
                             json={"column": "To Do"})
        assert move1.status_code == 200
        assert move1.get_json()["data"]["column"] == "To Do"

        # Move card: To Do → In Progress
        move2 = client.patch(f"/api/boards/{board_id}/cards/{card_id}", headers=headers,
                             json={"column": "In Progress"})
        assert move2.get_json()["data"]["column"] == "In Progress"

        # Move card: In Progress → In Review → Done
        client.patch(f"/api/boards/{board_id}/cards/{card_id}", headers=headers,
                     json={"column": "In Review"})
        move_done = client.patch(f"/api/boards/{board_id}/cards/{card_id}", headers=headers,
                                 json={"column": "Done"})
        assert move_done.get_json()["data"]["column"] == "Done"

        # Verify card appears in Done column via board detail
        board_detail = client.get(f"/api/boards/{board_id}", headers=headers)
        done_cards = board_detail.get_json()["data"]["columns"]["Done"]
        assert any(c["id"] == card_id for c in done_cards)

        # Delete card
        delete = client.delete(f"/api/boards/{board_id}/cards/{card_id}", headers=headers)
        assert delete.status_code == 200

        # Verify card is gone
        get_card = client.get(f"/api/boards/{board_id}/cards/{card_id}", headers=headers)
        assert get_card.status_code == 404

    def test_two_users_collaborate_on_board(self, client, auth_headers, auth_headers_user2):
        """User1 creates board, adds user2, user2 creates a card."""
        # User1 creates board
        board_id = client.post("/api/boards/", headers=auth_headers,
                               json={"name": "Collab Board"}).get_json()["data"]["id"]

        # User1 adds user2
        user2_id = client.get("/api/auth/me", headers=auth_headers_user2).get_json()["data"]["id"]
        add = client.post(f"/api/boards/{board_id}/members", headers=auth_headers,
                          json={"user_id": user2_id, "role": "user"})
        assert add.status_code == 201

        # User2 can see the board
        boards2 = client.get("/api/boards/", headers=auth_headers_user2).get_json()["data"]["boards"]
        assert any(b["id"] == board_id for b in boards2)

        # User2 creates a card
        card = client.post(f"/api/boards/{board_id}/cards", headers=auth_headers_user2,
                           json={"title": "User2 task", "column": "To Do"})
        assert card.status_code == 201
        assert card.get_json()["data"]["creator_username"] == "testuser2"

        # User1 can see user2's card
        cards = client.get(f"/api/boards/{board_id}/cards", headers=auth_headers)
        titles = [c["title"] for c in cards.get_json()["data"]["cards"]]
        assert "User2 task" in titles

    def test_delete_board_removes_all_cards(self, client, auth_headers, board_id):
        """Bug-catcher: deleting a board must cascade-delete all its cards."""
        client.post(f"/api/boards/{board_id}/cards", headers=auth_headers,
                    json={"title": "Card 1"})
        client.post(f"/api/boards/{board_id}/cards", headers=auth_headers,
                    json={"title": "Card 2"})
        client.delete(f"/api/boards/{board_id}", headers=auth_headers)
        # Board is gone — cards should be gone too (cascade)
        res = client.get(f"/api/boards/{board_id}", headers=auth_headers)
        assert res.status_code == 404

    def test_non_member_cannot_access_board_or_cards(self, client, auth_headers, auth_headers_user2):
        """Non-member gets 404 for both board and its cards."""
        board_id = client.post("/api/boards/", headers=auth_headers,
                               json={"name": "Private"}).get_json()["data"]["id"]
        assert client.get(f"/api/boards/{board_id}", headers=auth_headers_user2).status_code == 404
        assert client.get(f"/api/boards/{board_id}/cards", headers=auth_headers_user2).status_code == 404

    def test_removed_member_loses_access(self, client, auth_headers, auth_headers_user2, board_id):
        """After removal, former member gets 404 on the board."""
        user2_id = client.get("/api/auth/me", headers=auth_headers_user2).get_json()["data"]["id"]
        client.post(f"/api/boards/{board_id}/members", headers=auth_headers,
                    json={"user_id": user2_id, "role": "user"})
        assert client.get(f"/api/boards/{board_id}", headers=auth_headers_user2).status_code == 200
        client.delete(f"/api/boards/{board_id}/members/{user2_id}", headers=auth_headers)
        assert client.get(f"/api/boards/{board_id}", headers=auth_headers_user2).status_code == 404
