import sys
import time
from datetime import timedelta

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from .base import BaseCasino, read_credentials, notify


class AceBetCC(BaseCasino):
    URL = 'https://acebet.cc/'

    # Login
    LOGIN_BTN  = (By.XPATH, '//button[contains(., "Sign In") or contains(., "Log In") or contains(., "Login")]')
    USERNAME   = (By.NAME,  'email')
    PASSWORD   = (By.NAME,  'password')
    # Anchor on the form containing the email field — avoids fragile radix IDs
    SIGNIN_BTN = (By.XPATH, '//form[.//input[@name="email"]]//button')

    # Harvest — promotion popup
    CLAIM_NOW_BTN     = (By.XPATH, '//button[normalize-space()="Claim Now"]')
    # First bonus card link on the selection page
    BONUS_LINK        = (By.XPATH, '(//div[contains(@class,"flex-col") or contains(@class,"flex-row")]'
                                   '//div[1]//a)[1]')
    CLAIM_FREE_SC_BTN = (By.XPATH, '//button[contains(., "Claim Free") and contains(., "SC")]')

    PROMO_POPUP_WAIT = 15

    # ── login ──────────────────────────────────────────────────────────────────

    def login(self):
        username = read_credentials('acebet_username')
        password = read_credentials('acebet_password')

        notify('Navigating to AceBet.cc')
        self.driver.get(self.URL)
        self.screenshot('login_start')

        notify('Clicking login button...')
        self.click(self.LOGIN_BTN)
        self.screenshot('after_login_btn')

        notify('Entering credentials...')
        self.type_into(self.USERNAME, username)
        self.type_into(self.PASSWORD, password)
        self.screenshot('credentials_entered')

        notify('Clicking sign in...')
        self.click(self.SIGNIN_BTN)
        time.sleep(5)
        self.screenshot('after_signin')
        notify('Login successful', 'SUCCESS')

    # ── farm ───────────────────────────────────────────────────────────────────

    def farm(self) -> timedelta:
        self.screenshot('farm_start')

        notify('Waiting for promotion popup...')
        try:
            w = WebDriverWait(self.driver, self.PROMO_POPUP_WAIT)
            btn = w.until(EC.element_to_be_clickable(self.CLAIM_NOW_BTN))
            self.driver.execute_script('arguments[0].click()', btn)
            self.screenshot('after_claim_now')
        except TimeoutException:
            notify('No promotion popup appeared — bonus may already be claimed', 'WARNING')
            return timedelta(hours=24)

        notify('Selecting bonus...')
        self.click(self.BONUS_LINK)
        self.screenshot('after_bonus_link')

        notify('Clicking Claim Free SC...')
        self.click(self.CLAIM_FREE_SC_BTN)
        self.screenshot('after_claim')

        time.sleep(5)
        self.screenshot('claim_complete')
        notify('Free SC claimed', 'SUCCESS')
        return timedelta(hours=24)


if __name__ == '__main__':
    notify('=== AceBet.cc harvest starting ===')
    try:
        AceBetCC().run()
        notify('=== Harvest complete ===', 'SUCCESS')
    except Exception as e:
        notify(f'Harvest failed: {e}', 'ERROR')
        sys.exit(1)
