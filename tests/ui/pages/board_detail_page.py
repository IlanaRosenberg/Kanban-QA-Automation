import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage


class BoardDetailPage(BasePage):
    def open(self, board_id: int):
        self.navigate(f"/boards/{board_id}")
        self.wait_for_visible("page-board-detail")
        WebDriverWait(self.driver, 10).until(
            lambda d: d.find_element(
                By.CSS_SELECTOR, '[data-testid="board-title"]'
            ).text.strip() not in ("", "Loading...")
        )
        time.sleep(0.3)
        return self

    def get_board_title(self) -> str:
        return self.get_text("board-title")

    def click_add_card(self):
        self.click("btn-add-card")
        time.sleep(0.2)

    def fill_card_title(self, title: str):
        self.type_text("input-card-title", title)

    def fill_card_description(self, desc: str):
        self.type_text("input-card-description", desc)

    def select_card_column(self, column: str):
        el = self.wait_for_visible("select-card-column")
        Select(el).select_by_visible_text(column)

    def submit_card(self):
        self.click("btn-submit-card")
        time.sleep(0.6)

    def cancel_card_form(self):
        self.click("btn-cancel-card")

    def is_add_card_form_visible(self) -> bool:
        try:
            el = self.find("add-card-form")
            return "d-none" not in el.get_attribute("class")
        except Exception:
            return False

    def is_add_card_error_displayed(self) -> bool:
        try:
            el = self.find("add-card-error")
            return "d-none" not in el.get_attribute("class")
        except Exception:
            return False

    def get_card_titles_in_column(self, column: str) -> list:
        col_id = column.replace(" ", "-").lower()
        els = self.driver.find_elements(
            By.CSS_SELECTOR, f'[data-testid="column-{col_id}"] [data-testid^="card-title-"]'
        )
        return [e.text for e in els]

    def get_column_card_count(self, column: str) -> int:
        col_id = column.replace(" ", "-").lower()
        return int(self.get_text(f"column-count-{col_id}"))

    def is_card_visible(self, card_id: int) -> bool:
        return self.is_displayed(f"card-{card_id}")

    def move_card(self, card_id: int, new_column: str):
        el = self.wait_for_visible(f"select-move-card-{card_id}")
        Select(el).select_by_visible_text(new_column)
        time.sleep(0.8)

    def delete_card(self, card_id: int):
        self.driver.execute_script(
            "arguments[0].click();",
            self.wait_for_clickable(f"btn-delete-card-{card_id}")
        )
        try:
            WebDriverWait(self.driver, 3).until(EC.alert_is_present())
            self.driver.switch_to.alert.accept()
        except Exception:
            pass
        time.sleep(0.6)

    def click_back_to_boards(self):
        self.click("link-back-to-boards")
        time.sleep(0.3)

    def is_column_empty(self, column: str) -> bool:
        col_id = column.replace(" ", "-").lower()
        return self.is_displayed(f"col-empty-{col_id}")
