import sys
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from .base import BaseCasino, read_credentials, notify
from auth.gmail import get_verification_code


class ChumbaCasino(BaseCasino):
    URL = 'https://login.chumbacasino.com/'

    USERNAME       = (By.NAME, 'email')
    PASSWORD       = (By.NAME, 'password')
    SEND_CODE_BTN  = (By.ID,   'send-code-button')
    OTP_VERIFY_BTN = (By.ID,   'submit-otp-button')

    SC_BALANCE       = (By.CSS_SELECTOR, '[data-testid="sc-balance"], .sc-balance, #sc-balance-amount')
    GET_COINS_BTN    = (By.ID,         'hud__primary-buy-btn')
    DAILY_BONUS_TAB  = (By.CSS_SELECTOR, 'label[for="DAILY_BONUS"]')
    CLAIM_BTN        = (By.ID,          'streak-daily-bonus__claim-btn')

    OTP_SENDER  = 'chumbacasino.com'
    POPUP_WAIT  = 5

    POPUP_CLOSE_SELECTORS = [
        (By.CSS_SELECTOR, '.ab-close-button'),
        (By.ID,           'daily-jackpots-info-modal-header-close-button'),
        (By.CSS_SELECTOR, '#offer__close'),
    ]

    TRACKING_CONSENT_SELECTORS = [
        (By.CSS_SELECTOR, '[data-testid="tracking-preference-content"] button'),
        (By.XPATH,        '//*[@data-testid="tracking-preference-content"]//button'),
        (By.XPATH,        '//button[contains(translate(., "ACCEPT", "accept"), "accept")]'),
        (By.XPATH,        '//button[contains(translate(., "AGREE", "agree"), "agree")]'),
    ]

    def dismiss_tracking_consent(self):
        w = WebDriverWait(self.driver, self.POPUP_WAIT)
        for locator in self.TRACKING_CONSENT_SELECTORS:
            try:
                btn = w.until(EC.element_to_be_clickable(locator))
                self.driver.execute_script('arguments[0].click()', btn)
                return
            except TimeoutException:
                pass

    def dismiss_popups(self):
        w = WebDriverWait(self.driver, self.POPUP_WAIT)
        for locator in self.POPUP_CLOSE_SELECTORS:
            try:
                btn = w.until(EC.element_to_be_clickable(locator))
                btn.click()
            except TimeoutException:
                pass

    def safe_click(self, locator):
        try:
            self.click(locator)
        except TimeoutException:
            self.dismiss_popups()
            self.click(locator)

    def login(self):
        username = read_credentials('chumba_username')
        password = read_credentials('chumba_password')

        self.driver.get(self.URL)
        self.screenshot('login_start')
        self.type_into(self.USERNAME, username)
        self.dismiss_tracking_consent()
        self.screenshot('after_consent_dismiss')

        pass_el  = self.type_into(self.PASSWORD, password)
        pass_el.send_keys(Keys.ENTER)

        sent_at = time.time()
        self.click(self.SEND_CODE_BTN)

        code = get_verification_code(self.OTP_SENDER, received_after=sent_at)
        for i, digit in enumerate(code):
            self.type_into((By.ID, f'otp-code-input-{i}'), digit)
        self.click(self.OTP_VERIFY_BTN)
        notify('Login successful', 'SUCCESS')

    def farm(self):
        self.screenshot('farm_start')
        self.dismiss_popups()

        notify('Clicking get coins...')
        self.safe_click(self.GET_COINS_BTN)
        self.screenshot('after_get_coins')

        notify('Clicking daily bonus tab...')
        self.safe_click(self.DAILY_BONUS_TAB)
        self.screenshot('after_daily_bonus_tab')

        notify('Clicking claim button...')
        self.safe_click(self.CLAIM_BTN)
        self.screenshot('after_claim')

        time.sleep(10)
        self.screenshot('claim_complete')
        balance = self._read_balance()
        self.record_balance(balance)
        notify(f'Daily bonus claimed — balance: {balance}', 'SUCCESS')

    def _read_balance(self) -> str:
        try:
            el = self.wait.until(EC.presence_of_element_located(self.SC_BALANCE))
            return el.text.strip() or 'unknown'
        except Exception:
            return 'unavailable'


if __name__ == '__main__':
    notify('=== Chumba Casino harvest starting ===')
    try:
        ChumbaCasino().run()
        notify('=== Harvest complete ===', 'SUCCESS')
    except Exception as e:
        notify(f'Harvest failed: {e}', 'ERROR')
        sys.exit(1)
