"""UI tests — Authentication: login, register, logout."""
import pytest
import allure
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.ui.pages.login_page import LoginPage
from tests.ui.pages.register_page import RegisterPage

pytestmark = [pytest.mark.ui]


@allure.feature("Auth UI")
@allure.story("Login")
class TestLoginUI:
    @allure.title("Valid credentials redirect to /boards")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_login_success_redirects_to_boards(self, driver, base_url):
        page = LoginPage(driver, base_url).open()
        page.login("testuser1@kanban.com", "Password123!")
        WebDriverWait(driver, 10).until(EC.url_contains("/boards"))
        assert "/boards" in driver.current_url

    @allure.title("Wrong password shows error message")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_login_wrong_password_shows_error(self, driver, base_url):
        page = LoginPage(driver, base_url).open()
        page.login("testuser1@kanban.com", "wrongpassword")
        assert page.is_error_displayed()

    @allure.title("Empty email shows error")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_empty_email_shows_error(self, driver, base_url):
        page = LoginPage(driver, base_url).open()
        page.login("", "Password123!")
        assert page.is_error_displayed()

    @allure.title("Empty password shows error")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_empty_password_shows_error(self, driver, base_url):
        page = LoginPage(driver, base_url).open()
        page.login("testuser1@kanban.com", "")
        assert page.is_error_displayed()

    @allure.title("Non-existent user shows error")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_unknown_user_shows_error(self, driver, base_url):
        page = LoginPage(driver, base_url).open()
        page.login("nobody@kanban.com", "Password123!")
        assert page.is_error_displayed()

    @allure.title("Register link navigates to /register")
    @allure.severity(allure.severity_level.MINOR)
    def test_login_register_link_navigates(self, driver, base_url):
        page = LoginPage(driver, base_url).open()
        page.click_register_link()
        WebDriverWait(driver, 10).until(EC.url_contains("/register"))
        assert "/register" in driver.current_url


@allure.feature("Auth UI")
@allure.story("Register")
class TestRegisterUI:
    @allure.title("Valid registration shows success message")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_register_success(self, driver, base_url):
        page = RegisterPage(driver, base_url).open()
        page.register("newuserui", "newuserui@kanban.com", "NewPass123!")
        assert page.is_success_displayed()

    @allure.title("Duplicate email shows error")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_register_duplicate_email_shows_error(self, driver, base_url):
        page = RegisterPage(driver, base_url).open()
        page.register("dupeuser", "testuser1@kanban.com", "Password123!")
        assert page.is_error_displayed()

    @allure.title("Missing username shows error")
    @allure.severity(allure.severity_level.NORMAL)
    def test_register_missing_username_shows_error(self, driver, base_url):
        page = RegisterPage(driver, base_url).open()
        page.register("", "valid@kanban.com", "Password123!")
        assert page.is_error_displayed()

    @allure.title("Invalid email format shows error")
    @allure.severity(allure.severity_level.NORMAL)
    def test_register_invalid_email_shows_error(self, driver, base_url):
        page = RegisterPage(driver, base_url).open()
        page.register("validuser", "notanemail", "Password123!")
        assert page.is_error_displayed()

    @allure.title("Login link navigates to /login")
    @allure.severity(allure.severity_level.MINOR)
    def test_register_login_link_navigates(self, driver, base_url):
        page = RegisterPage(driver, base_url).open()
        page.click_login_link()
        WebDriverWait(driver, 10).until(EC.url_contains("/login"))
        assert "/login" in driver.current_url


@allure.feature("Auth UI")
@allure.story("Logout")
class TestLogoutUI:
    @allure.title("Logout redirects to login page")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_logout_redirects_to_login(self, logged_in_driver, base_url):
        from tests.ui.pages.base_page import BasePage
        page = BasePage(logged_in_driver, base_url)
        page.click("link-logout")
        WebDriverWait(logged_in_driver, 10).until(EC.url_contains("/login"))
        assert "/login" in logged_in_driver.current_url

    @allure.title("Unauthenticated user redirected from /boards to /login")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_unauthenticated_redirected_from_boards(self, driver, base_url):
        from tests.ui.pages.base_page import BasePage
        BasePage(driver, base_url).navigate("/boards")
        WebDriverWait(driver, 10).until(EC.url_contains("/login"))
        assert "/login" in driver.current_url
