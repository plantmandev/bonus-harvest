import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from .base import BaseCasino, read_credentials, notify
from auth.gmail import get_verification_code

SCHEDULE_BUFFER_MINUTES = 5  # run slightly after bonus resets to ensure availability


class ChumbaCasino(BaseCasino):
    URL = 'https://login.chumbacasino.com/'

    USERNAME       = (By.NAME, 'email')
    PASSWORD       = (By.NAME, 'password')
    SEND_CODE_BTN  = (By.ID,   'send-code-button')
    OTP_VERIFY_BTN = (By.ID,   'submit-otp-button')

    SC_TOGGLE       = (By.CSS_SELECTOR, 'span.switch__fixed-icon--right')
    SC_BALANCE      = (By.CSS_SELECTOR, 'span.counter__balance-toggle span.counter__value')
    GET_COINS_BTN   = (By.ID,           'hud__primary-buy-btn')
    DAILY_BONUS_TAB = (By.CSS_SELECTOR, 'label[for="DAILY_BONUS"]')
    CLAIM_BTN       = (By.ID,           'streak-daily-bonus__claim-btn')
    NEXT_BONUS_TIMER = (By.CSS_SELECTOR, (
        'body > div.modal-wrapper.STORE_MODAL_V2-modal.fs-unmask > div > div > div > '
        'div.store__contents_center > div.store__standard > div > '
        'div.streak-daily-bonus-reset-dialog > p'
    ))

    OTP_SENDER = 'chumbacasino.com'
    POPUP_WAIT = 5

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

    # ── login ──────────────────────────────────────────────────────────────────

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

        pass_el = self.type_into(self.PASSWORD, password)
        pass_el.send_keys(Keys.ENTER)

        sent_at = time.time()
        self.click(self.SEND_CODE_BTN)

        code = get_verification_code(self.OTP_SENDER, received_after=sent_at)
        for i, digit in enumerate(code):
            self.type_into((By.ID, f'otp-code-input-{i}'), digit)
        self.click(self.OTP_VERIFY_BTN)
        notify('Login successful', 'SUCCESS')

    # ── farm ───────────────────────────────────────────────────────────────────

    def farm(self) -> timedelta:
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

        delta = self._read_next_bonus_delta()
        if delta is None:
            notify('Could not read next bonus timer — defaulting to 24h', 'WARNING')
            return timedelta(hours=24)
        return delta + timedelta(minutes=SCHEDULE_BUFFER_MINUTES)

    # ── balance ────────────────────────────────────────────────────────────────

    def _read_balance(self) -> str:
        try:
            self.driver.execute_script(
                'arguments[0].click()',
                self.driver.find_element(*self.SC_TOGGLE)
            )
            time.sleep(0.5)
            el = self.wait.until(EC.presence_of_element_located(self.SC_BALANCE))
            return f'{el.text.strip()} SC'
        except Exception:
            return 'unavailable'

    # ── dynamic scheduling ─────────────────────────────────────────────────────

    def _read_next_bonus_delta(self) -> timedelta | None:
        try:
            w   = WebDriverWait(self.driver, 10)
            el  = w.until(EC.presence_of_element_located(self.NEXT_BONUS_TIMER))
            raw = el.text.strip()
            notify(f'Next bonus timer text: "{raw}"')
            return _parse_countdown(raw)
        except Exception as e:
            notify(f'Could not read next bonus timer: {e}', 'WARNING')
            return None


def _parse_countdown(text: str) -> timedelta | None:
    """Parse countdown strings like '11 hours 32 minutes', '11h 32m', '23:45:00'."""
    text = text.lower()

    # HH:MM:SS or H:MM:SS
    m = re.search(r'(\d+):(\d{2})(?::(\d{2}))?', text)
    if m:
        h, mins, secs = int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)
        return timedelta(hours=h, minutes=mins, seconds=secs)

    # "X hours Y minutes" / "Xh Ym"
    hours = re.search(r'(\d+)\s*h(?:our)?s?', text)
    mins  = re.search(r'(\d+)\s*m(?:in(?:ute)?)?s?', text)
    h = int(hours.group(1)) if hours else 0
    m = int(mins.group(1))  if mins  else 0
    if h or m:
        return timedelta(hours=h, minutes=m)

    return None


if __name__ == '__main__':
    notify('=== Chumba Casino harvest starting ===')
    try:
        ChumbaCasino().run()
        notify('=== Harvest complete ===', 'SUCCESS')
    except Exception as e:
        notify(f'Harvest failed: {e}', 'ERROR')
        sys.exit(1)
