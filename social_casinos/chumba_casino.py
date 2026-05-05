import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import time
from casino_base import BaseCasino, read_credentials
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class ChumbaCasino(BaseCasino):
    URL = 'https://login.chumbacasino.com/'

    USERNAME = (By.NAME, 'email')
    PASSWORD = (By.NAME, 'password')
    BONUS = (By.CSS_SELECTOR, '#daily-bonus__claim-btn')
    POPUP_CLOSE = (By.CSS_SELECTOR, '#offer__close')

    def login(self):
        username = read_credentials('chumba_username')
        password = read_credentials('chumba_password')

        self.driver.get(self.URL)
        self.type_into(self.USERNAME, username)
        pass_el = self.type_into(self.PASSWORD, password)
        pass_el.send_keys(Keys.ENTER)
        time.sleep(5)  # TODO: Replace with WebDriverWait once post-login element is known

    def farm(self):
        self.click(self.BONUS)

    # TODO: Chumba requires email authentication — wire up Gmail integration


if __name__ == '__main__':
    ChumbaCasino().run()
