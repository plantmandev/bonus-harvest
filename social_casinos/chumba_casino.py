import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'GmailVerification'))
sys.path.insert(0, str(Path(__file__).parent))

import time
from casino_base import BaseCasino, read_credentials
from GmailVerificationCode import get_verification_code
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class ChumbaCasino(BaseCasino):
    URL = 'https://login.chumbacasino.com/'

    USERNAME = (By.NAME, 'email')
    PASSWORD = (By.NAME, 'password')
    SEND_CODE_BTN = (By.ID, 'send-code-button')
    OTP_VERIFY_BTN = (By.ID, 'submit-otp-button')

    GET_COINS_BTN = (By.ID, 'hud__primary-buy-btn')
    DAILY_BONUS_TAB = (By.CSS_SELECTOR, 'label[for="DAILY_BONUS"]')
    CLAIM_BTN = (By.ID, 'streak-daily-bonus__claim-btn')

    OTP_SENDER = 'chumbacasino.com'
    POPUP_WAIT = 5  # seconds to wait for each popup close button

    # Close-button locators for any popup/modal that may appear
    POPUP_CLOSE_SELECTORS = [
        (By.CSS_SELECTOR, '.ab-close-button'),                      # Braze in-app messages
        (By.ID, 'daily-jackpots-info-modal-header-close-button'),   # Daily Jackpots info modal
        (By.CSS_SELECTOR, '#offer__close'),                         # Generic offer overlay
    ]

    def login(self):
        username = read_credentials('chumba_username')
        password = read_credentials('chumba_password')

        self.driver.get(self.URL)
        self.type_into(self.USERNAME, username)
        pass_el = self.type_into(self.PASSWORD, password)
        pass_el.send_keys(Keys.ENTER)

        sent_at = time.time()
        self.click(self.SEND_CODE_BTN)

        code = get_verification_code(self.OTP_SENDER, received_after=sent_at)
        for i, digit in enumerate(code):
            self.type_into((By.ID, f'otp-code-input-{i}'), digit)
        self.click(self.OTP_VERIFY_BTN)

    def dismiss_popups(self):
        popup_wait = WebDriverWait(self.driver, self.POPUP_WAIT)
        for locator in self.POPUP_CLOSE_SELECTORS:
            try:
                btn = popup_wait.until(EC.element_to_be_clickable(locator))
                btn.click()
            except TimeoutException:
                pass

    def safe_click(self, locator):
        try:
            self.click(locator)
        except TimeoutException:
            self.dismiss_popups()
            self.click(locator)

    def farm(self):
        self.dismiss_popups()
        self.safe_click(self.GET_COINS_BTN)
        self.safe_click(self.DAILY_BONUS_TAB)
        self.safe_click(self.CLAIM_BTN)
        time.sleep(10)


if __name__ == '__main__':
    ChumbaCasino().run()
