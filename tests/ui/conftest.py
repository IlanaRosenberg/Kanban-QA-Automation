import threading
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from app import create_app
from app.database import db as _db
from seed_data.seed import seed_db


BASE_URL = "http://localhost:5002"
TEST_USER_EMAIL = "testuser1@kanban.com"
TEST_USER_PASSWORD = "Password123!"


def _run_server(flask_app):
    flask_app.run(host="127.0.0.1", port=5002, use_reloader=False, threaded=True)


@pytest.fixture(scope="session")
def live_app():
    flask_app = create_app("testing")
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test_ui_kanban.db"
    flask_app.config["TESTING"] = False

    with flask_app.app_context():
        _db.create_all()
        seed_db()

    t = threading.Thread(target=_run_server, args=(flask_app,), daemon=True)
    t.start()
    time.sleep(1.5)

    yield flask_app

    with flask_app.app_context():
        _db.drop_all()


@pytest.fixture(scope="function")
def driver(live_app):
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1280,900")
    d = webdriver.Chrome(options=opts)
    d.implicitly_wait(0)
    yield d
    d.quit()


@pytest.fixture(scope="function")
def base_url():
    return BASE_URL


@pytest.fixture(scope="function")
def logged_in_driver(driver, base_url):
    """Driver with testuser1 already logged in via UI."""
    from tests.ui.pages.login_page import LoginPage
    LoginPage(driver, base_url).open().login(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    WebDriverWait(driver, 10).until(EC.url_contains("/boards"))
    return driver
