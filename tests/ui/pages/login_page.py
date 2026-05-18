from .base_page import BasePage


class LoginPage(BasePage):
    URL = "/login"

    def open(self):
        self.navigate(self.URL)
        self.wait_for_visible("login-form")
        return self

    def login(self, email: str, password: str):
        self.type_text("input-email", email)
        self.type_text("input-password", password)
        self.click("btn-login")

    def is_error_displayed(self) -> bool:
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: "d-none" not in d.find_element(By.CSS_SELECTOR, '[data-testid="login-error"]').get_attribute("class")
            )
            return True
        except Exception:
            return False

    def get_error_message(self) -> str:
        return self.get_text("login-error")

    def click_register_link(self):
        self.click("link-register")
