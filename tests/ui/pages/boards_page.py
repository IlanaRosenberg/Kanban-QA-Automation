import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage


class BoardsPage(BasePage):
    URL = "/boards"

    def open(self):
        self.navigate(self.URL)
        self.wait_for_visible("page-boards")
        WebDriverWait(self.driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "boards-loading"))
        )
        time.sleep(0.3)
        return self

    def click_new_board(self):
        self.click("btn-create-board")
        time.sleep(0.2)

    def fill_board_name(self, name: str):
        self.type_text("input-board-name", name)

    def fill_board_description(self, desc: str):
        self.type_text("input-board-description", desc)

    def submit_board(self):
        self.click("btn-submit-board")
        time.sleep(0.5)

    def cancel_board_form(self):
        self.click("btn-cancel-board")

    def get_board_count(self) -> int:
        cards = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid^="board-card-"]')
        return len(cards)

    def get_board_names(self) -> list:
        els = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid^="board-name-"]')
        return [e.text for e in els]

    def is_board_visible(self, board_id: int) -> bool:
        return self.is_displayed(f"board-card-{board_id}")

    def open_board(self, board_id: int):
        self.click(f"btn-open-board-{board_id}")
        time.sleep(0.5)

    def delete_board(self, board_id: int):
        self.click(f"btn-delete-board-{board_id}")
        time.sleep(0.5)

    def is_no_boards_displayed(self) -> bool:
        try:
            el = self.find("no-boards")
            return "d-none" not in el.get_attribute("class")
        except Exception:
            return False

    def is_create_form_visible(self) -> bool:
        try:
            el = self.find("create-board-form")
            return "d-none" not in el.get_attribute("class")
        except Exception:
            return False

    def is_create_error_displayed(self) -> bool:
        try:
            el = self.find("create-board-error")
            return "d-none" not in el.get_attribute("class")
        except Exception:
            return False
