"""UI tests — Boards page: create, list, delete."""
import pytest
import allure
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.ui.pages.boards_page import BoardsPage

pytestmark = [pytest.mark.ui]


@allure.feature("Boards UI")
@allure.story("View Boards")
class TestBoardsListUI:
    @allure.title("Boards page loads and shows seeded boards")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_boards_page_loads(self, logged_in_driver, base_url):
        page = BoardsPage(logged_in_driver, base_url).open()
        assert page.get_board_count() >= 1

    @allure.title("Board names are visible on the page")
    @allure.severity(allure.severity_level.NORMAL)
    def test_board_names_visible(self, logged_in_driver, base_url):
        page = BoardsPage(logged_in_driver, base_url).open()
        names = page.get_board_names()
        assert len(names) >= 1
        assert all(n.strip() != "" for n in names)


@allure.feature("Boards UI")
@allure.story("Create Board")
class TestCreateBoardUI:
    @allure.title("Create board form appears on button click")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_form_appears(self, logged_in_driver, base_url):
        page = BoardsPage(logged_in_driver, base_url).open()
        assert not page.is_create_form_visible()
        page.click_new_board()
        assert page.is_create_form_visible()

    @allure.title("Cancel button hides the form")
    @allure.severity(allure.severity_level.MINOR)
    def test_cancel_hides_form(self, logged_in_driver, base_url):
        page = BoardsPage(logged_in_driver, base_url).open()
        page.click_new_board()
        page.cancel_board_form()
        assert not page.is_create_form_visible()

    @allure.title("Creating a valid board adds it to the list")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_create_board_success(self, logged_in_driver, base_url):
        page = BoardsPage(logged_in_driver, base_url).open()
        before = page.get_board_count()
        page.click_new_board()
        page.fill_board_name("UI New Board")
        page.fill_board_description("Created via UI test")
        page.submit_board()
        WebDriverWait(logged_in_driver, 10).until(
            lambda d: BoardsPage(d, base_url).get_board_count() > before
        )
        assert page.get_board_count() == before + 1
        assert "UI New Board" in page.get_board_names()

    @allure.title("Submitting empty name shows error")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_board_empty_name_shows_error(self, logged_in_driver, base_url):
        page = BoardsPage(logged_in_driver, base_url).open()
        page.click_new_board()
        page.submit_board()
        assert page.is_create_error_displayed()

    @allure.title("Board count does not increase after error")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_board_error_no_new_board(self, logged_in_driver, base_url):
        page = BoardsPage(logged_in_driver, base_url).open()
        before = page.get_board_count()
        page.click_new_board()
        page.submit_board()
        assert page.get_board_count() == before


@allure.feature("Boards UI")
@allure.story("Delete Board")
class TestDeleteBoardUI:
    @allure.title("Deleting a board removes it from the list")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_board_removes_from_list(self, logged_in_driver, base_url):
        page = BoardsPage(logged_in_driver, base_url).open()

        # Create a board to delete
        page.click_new_board()
        page.fill_board_name("Board To Delete")
        page.submit_board()
        WebDriverWait(logged_in_driver, 10).until(
            lambda d: "Board To Delete" in BoardsPage(d, base_url).get_board_names()
        )
        before = page.get_board_count()

        # Find the newly created board's id by looking at cards
        cards = logged_in_driver.find_elements(
            __import__("selenium.webdriver.common.by", fromlist=["By"]).By.CSS_SELECTOR,
            '[data-testid^="board-card-"]'
        )
        # Get the last board id
        last_card = cards[-1]
        board_id = int(last_card.get_attribute("data-testid").replace("board-card-", ""))

        # Accept the confirm dialog
        logged_in_driver.execute_script(
            "window.confirm = function() { return true; };"
        )
        page.delete_board(board_id)

        WebDriverWait(logged_in_driver, 10).until(
            lambda d: BoardsPage(d, base_url).get_board_count() < before
        )
        assert page.get_board_count() == before - 1


@allure.feature("Boards UI")
@allure.story("Navigate to Board")
class TestOpenBoardUI:
    @allure.title("Clicking Open navigates to board detail page")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_open_board_navigates(self, logged_in_driver, base_url):
        page = BoardsPage(logged_in_driver, base_url).open()
        cards = logged_in_driver.find_elements(
            __import__("selenium.webdriver.common.by", fromlist=["By"]).By.CSS_SELECTOR,
            '[data-testid^="board-card-"]'
        )
        assert len(cards) >= 1
        board_id = int(cards[0].get_attribute("data-testid").replace("board-card-", ""))
        page.open_board(board_id)
        WebDriverWait(logged_in_driver, 10).until(
            EC.url_contains(f"/boards/{board_id}")
        )
        assert f"/boards/{board_id}" in logged_in_driver.current_url
