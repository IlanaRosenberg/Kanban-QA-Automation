from .base_page import BasePage


class RegisterPage(BasePage):
    URL = "/register"

    def open(self):
        self.navigate(self.URL)
        self.wait_for_visible("register-form")
        return self

    def register(self, username: str, email: str, password: str):
        self.type_text("input-username", username)
        self.type_text("input-email", email)
        self.type_text("input-password", password)
        self.click("btn-register")

    def is_error_displayed(self) -> bool:
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.common.by import By
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: "d-none" not in d.find_element(By.CSS_SELECTOR, '[data-testid="register-error"]').get_attribute("class")
            )
            return True
        except Exception:
            return False

    def get_error_message(self) -> str:
        return self.get_text("register-error")

    def is_success_displayed(self) -> bool:
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.common.by import By
        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: "d-none" not in d.find_element(By.CSS_SELECTOR, '[data-testid="register-success"]').get_attribute("class")
            )
            return True
        except Exception:
            return False

    def click_login_link(self):
        self.click("link-login")
