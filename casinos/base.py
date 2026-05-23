import os
import sys
import time
import random
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as UC

load_dotenv(Path(__file__).parent.parent / '.env')

WAIT_TIMEOUT   = 30
SCREENSHOT_DIR = Path(__file__).parent.parent / 'logs' / 'screenshots'


def notify(message: str, level: str = 'INFO'):
    tag  = f'[{level}]'
    ts   = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'{ts} {tag:<9} {message}'
    print(line, flush=True)
    if level == 'ERROR':
        print(line, file=sys.stderr, flush=True)


def read_credentials(key: str) -> str:
    value = os.getenv(key.upper())
    if value is None:
        raise ValueError(f'Missing credential: {key.upper()} not set in .env')
    return value


def create_driver():
    options = webdriver.ChromeOptions()
    if os.getenv('SERVER_MODE', '').lower() in ('1', 'true', 'yes'):
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
    proxy = os.getenv('PROXY_SERVER')
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')
    return UC.Chrome(options, version_main=147)


class BaseCasino:
    def __init__(self):
        self.driver = create_driver()
        self.wait   = WebDriverWait(self.driver, WAIT_TIMEOUT)
        self._name  = self.__class__.__name__

    def screenshot(self, label: str):
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        ts   = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = SCREENSHOT_DIR / f'{self._name}_{ts}_{label}.png'
        self.driver.save_screenshot(str(path))
        return path

    # ── phases ────────────────────────────────────────────────────────────────

    def login(self):
        raise NotImplementedError

    def farm(self):
        raise NotImplementedError

    def glean(self):
        pass  # play through credits at highest RTP — not yet implemented

    def harvest(self):
        pass  # withdraw when balance threshold is met — not yet implemented

    def run(self):
        try:
            self.login()
            self.farm()
            self.glean()
            self.harvest()
        finally:
            self.driver.quit()

    def record_balance(self, raw_text: str):
        try:
            from data_analysis.tracker import record
            record(self._casino_key(), raw_text)
        except Exception as e:
            notify(f'Balance record failed: {e}', 'WARNING')

    def _casino_key(self) -> str:
        import re
        return re.sub(r'(?<!^)(?=[A-Z])', '_', self._name).lower()

    # ── helpers ───────────────────────────────────────────────────────────────

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
