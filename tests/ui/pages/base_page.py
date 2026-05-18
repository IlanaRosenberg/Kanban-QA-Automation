from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    DEFAULT_TIMEOUT = 10

    def __init__(self, driver, base_url: str):
        self.driver = driver
        self.base_url = base_url.rstrip("/")

    @staticmethod
    def _by_testid(testid: str):
        return By.CSS_SELECTOR, f'[data-testid="{testid}"]'

    def find(self, testid: str):
        return self.driver.find_element(*self._by_testid(testid))

    def find_all(self, testid: str):
        return self.driver.find_elements(*self._by_testid(testid))

    def wait_for(self, testid: str, timeout=None):
        t = timeout or self.DEFAULT_TIMEOUT
        return WebDriverWait(self.driver, t).until(
            EC.presence_of_element_located(self._by_testid(testid))
        )

    def wait_for_visible(self, testid: str, timeout=None):
        t = timeout or self.DEFAULT_TIMEOUT
        return WebDriverWait(self.driver, t).until(
            EC.visibility_of_element_located(self._by_testid(testid))
        )

    def wait_for_clickable(self, testid: str, timeout=None):
        t = timeout or self.DEFAULT_TIMEOUT
        return WebDriverWait(self.driver, t).until(
            EC.element_to_be_clickable(self._by_testid(testid))
        )

    def click(self, testid: str):
        el = self.wait_for_clickable(testid)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        self.driver.execute_script("arguments[0].click();", el)

    def type_text(self, testid: str, text: str, clear=True):
        el = self.wait_for_visible(testid)
        if clear:
            el.clear()
        el.send_keys(text)

    def get_text(self, testid: str) -> str:
        return self.wait_for_visible(testid).text.strip()

    def is_displayed(self, testid: str) -> bool:
        try:
            return self.find(testid).is_displayed()
        except Exception:
            return False

    def navigate(self, path: str):
        self.driver.get(f"{self.base_url}{path}")

    def wait_for_url(self, fragment: str, timeout=None):
        t = timeout or self.DEFAULT_TIMEOUT
        WebDriverWait(self.driver, t).until(EC.url_contains(fragment))
