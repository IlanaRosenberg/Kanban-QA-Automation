"""UI tests — Board detail: add card, move card, delete card."""
import pytest
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.ui.pages.boards_page import BoardsPage
from tests.ui.pages.board_detail_page import BoardDetailPage

pytestmark = [pytest.mark.ui]


def _get_first_board_id(driver, base_url):
    page = BoardsPage(driver, base_url).open()
    cards = driver.find_elements(By.CSS_SELECTOR, '[data-testid^="board-card-"]')
    assert len(cards) >= 1, "No boards found — seed data issue"
    return int(cards[0].get_attribute("data-testid").replace("board-card-", ""))


@allure.feature("Cards UI")
@allure.story("Board Detail View")
class TestBoardDetailUI:
    @allure.title("Board detail page loads with title")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_board_detail_title_visible(self, logged_in_driver, base_url):
        board_id = _get_first_board_id(logged_in_driver, base_url)
        page = BoardDetailPage(logged_in_driver, base_url).open(board_id)
        assert page.get_board_title() != ""

    @allure.title("All 5 Kanban columns are rendered")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_all_five_columns_visible(self, logged_in_driver, base_url):
        board_id = _get_first_board_id(logged_in_driver, base_url)
        page = BoardDetailPage(logged_in_driver, base_url).open(board_id)
        columns = ["backlog", "to-do", "in-progress", "in-review", "done"]
        for col in columns:
            assert logged_in_driver.find_element(
                By.CSS_SELECTOR, f'[data-testid="column-{col}"]'
            ).is_displayed(), f"Column '{col}' not visible"

    @allure.title("Back button navigates to /boards")
    @allure.severity(allure.severity_level.MINOR)
    def test_back_button_navigates_to_boards(self, logged_in_driver, base_url):
        board_id = _get_first_board_id(logged_in_driver, base_url)
        page = BoardDetailPage(logged_in_driver, base_url).open(board_id)
        page.click_back_to_boards()
        WebDriverWait(logged_in_driver, 10).until(EC.url_contains("/boards"))
        assert logged_in_driver.current_url.rstrip("/").endswith("/boards")


@allure.feature("Cards UI")
@allure.story("Add Card")
class TestAddCardUI:
    @allure.title("Add card form appears on button click")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_card_form_appears(self, logged_in_driver, base_url):
        board_id = _get_first_board_id(logged_in_driver, base_url)
        page = BoardDetailPage(logged_in_driver, base_url).open(board_id)
        assert not page.is_add_card_form_visible()
        page.click_add_card()
        assert page.is_add_card_form_visible()

    @allure.title("Cancel hides the add card form")
    @allure.severity(allure.severity_level.MINOR)
    def test_add_card_cancel_hides_form(self, logged_in_driver, base_url):
        board_id = _get_first_board_id(logged_in_driver, base_url)
        page = BoardDetailPage(logged_in_driver, base_url).open(board_id)
        page.click_add_card()
        page.cancel_card_form()
        assert not page.is_add_card_form_visible()

    @allure.title("Add card to Backlog column successfully")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_add_card_to_backlog(self, logged_in_driver, base_url):
        board_id = _get_first_board_id(logged_in_driver, base_url)
        page = BoardDetailPage(logged_in_driver, base_url).open(board_id)
        before = page.get_column_card_count("backlog")
        page.click_add_card()
        page.fill_card_title("UI Test Card")
        page.select_card_column("Backlog")
        page.submit_card()
        WebDriverWait(logged_in_driver, 10).until(
            lambda d: BoardDetailPage(d, base_url).get_column_card_count("backlog") > before
        )
        titles = page.get_card_titles_in_column("backlog")
        assert "UI Test Card" in titles

    @allure.title("Add card to In Progress column")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_card_to_in_progress(self, logged_in_driver, base_url):
        board_id = _get_first_board_id(logged_in_driver, base_url)
        page = BoardDetailPage(logged_in_driver, base_url).open(board_id)
        before = page.get_column_card_count("in-progress")
        page.click_add_card()
        page.fill_card_title("In Progress Card")
        page.select_card_column("In Progress")
        page.submit_card()
        WebDriverWait(logged_in_driver, 10).until(
            lambda d: BoardDetailPage(d, base_url).get_column_card_count("in-progress") > before
        )
        titles = page.get_card_titles_in_column("in-progress")
        assert "In Progress Card" in titles

    @allure.title("Empty title shows error in form")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_card_empty_title_shows_error(self, logged_in_driver, base_url):
        board_id = _get_first_board_id(logged_in_driver, base_url)
        page = BoardDetailPage(logged_in_driver, base_url).open(board_id)
        page.click_add_card()
        page.submit_card()
        assert page.is_add_card_error_displayed()


@allure.feature("Cards UI")
@allure.story("Move Card")
class TestMoveCardUI:
    @allure.title("Move card from Backlog to To Do updates column counts")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_move_card_updates_columns(self, logged_in_driver, base_url):
        board_id = _get_first_board_id(logged_in_driver, base_url)
        page = BoardDetailPage(logged_in_driver, base_url).open(board_id)

        # Add a card to Backlog first
        page.click_add_card()
        page.fill_card_title("Card To Move")
        page.select_card_column("Backlog")
        page.submit_card()
        WebDriverWait(logged_in_driver, 10).until(
            lambda d: "Card To Move" in BoardDetailPage(d, base_url).get_card_titles_in_column("backlog")
        )

        backlog_before = page.get_column_card_count("backlog")
        todo_before = page.get_column_card_count("to-do")

        # Find the card id
        card_els = logged_in_driver.find_elements(By.CSS_SELECTOR, '[data-testid^="card-"]')
        card_id = None
        for el in card_els:
            tid = el.get_attribute("data-testid")
            if tid and tid.startswith("card-") and tid[5:].isdigit():
                title_el = logged_in_driver.find_elements(
                    By.CSS_SELECTOR, f'[data-testid="card-title-{tid[5:]}"]'
                )
                if title_el and title_el[0].text == "Card To Move":
                    card_id = int(tid[5:])
                    break

        assert card_id is not None, "Could not find 'Card To Move' card"
        page.move_card(card_id, "To Do")

        WebDriverWait(logged_in_driver, 10).until(
            lambda d: BoardDetailPage(d, base_url).get_column_card_count("backlog") < backlog_before
        )
        assert page.get_column_card_count("to-do") == todo_before + 1


@allure.feature("Cards UI")
@allure.story("Delete Card")
class TestDeleteCardUI:
    @allure.title("Deleting a card removes it from its column")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_card_removes_from_column(self, logged_in_driver, base_url):
        board_id = _get_first_board_id(logged_in_driver, base_url)
        page = BoardDetailPage(logged_in_driver, base_url).open(board_id)

        # Add a card to delete
        page.click_add_card()
        page.fill_card_title("Card To Delete")
        page.select_card_column("To Do")
        page.submit_card()
        WebDriverWait(logged_in_driver, 10).until(
            lambda d: "Card To Delete" in BoardDetailPage(d, base_url).get_card_titles_in_column("to-do")
        )

        todo_before = page.get_column_card_count("to-do")

        # Find the card id
        card_id = None
        card_els = logged_in_driver.find_elements(By.CSS_SELECTOR, '[data-testid^="card-title-"]')
        for el in card_els:
            if el.text == "Card To Delete":
                tid = el.get_attribute("data-testid").replace("card-title-", "")
                card_id = int(tid)
                break

        assert card_id is not None

        # Bypass confirm dialog
        logged_in_driver.execute_script("window.confirm = function() { return true; };")
        page.delete_card(card_id)

        WebDriverWait(logged_in_driver, 10).until(
            lambda d: BoardDetailPage(d, base_url).get_column_card_count("to-do") < todo_before
        )
        assert "Card To Delete" not in page.get_card_titles_in_column("to-do")
