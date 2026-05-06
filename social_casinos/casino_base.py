import os
import time
import random
from pathlib import Path
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as UC

load_dotenv(Path(__file__).parent.parent / '.env')
WAIT_TIMEOUT = 30


def read_credentials(credential_type):
    value = os.getenv(credential_type.upper())
    if value is None:
        raise ValueError(f'Missing credential: {credential_type.upper()} not set in .env')
    return value


def create_driver():
    options = webdriver.ChromeOptions()
    if os.getenv('SERVER_MODE', '').lower() in ('1', 'true', 'yes'):
        # Required for running Chrome inside containers (no sandbox, shared memory workaround)
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
    proxy = os.getenv('PROXY_SERVER')
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')
    return UC.Chrome(options, version_main=147)


class BaseCasino:
    def __init__(self):
        self.driver = create_driver()
        self.wait = WebDriverWait(self.driver, WAIT_TIMEOUT)

    def login(self):
        raise NotImplementedError

    def farm(self):
        raise NotImplementedError

    def run(self):
        try:
            self.login()
            self.farm()
        finally:
            self.driver.quit()

    def click(self, locator):
        el = self.wait.until(EC.element_to_be_clickable(locator))
        time.sleep(random.uniform(0.3, 1.2))
        el.click()
        return el

    def type_into(self, locator, text):
        el = self.wait.until(EC.element_to_be_clickable(locator))
        time.sleep(random.uniform(0.3, 1.2))
        el.click()
        el.send_keys(text)
        return el
