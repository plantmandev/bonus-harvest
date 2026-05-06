import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
from casino_base import BaseCasino, read_credentials
from notify import notify
from GmailVerification.GmailVerificationCode import get_verification_code
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC


class StakeUS(BaseCasino):
    URL = 'https://stake.us/?tab=login&modal=auth'

    USERNAME         = (By.NAME, 'emailOrName')
    PASSWORD         = (By.NAME, 'password')
    EMAIL_CODE_INPUT = (By.CSS_SELECTOR, 'input[type="text"]')
    WALLET           = (By.CSS_SELECTOR, '[data-testid="wallet"]')
    DAILY_BONUS      = (By.CSS_SELECTOR, '[data-testid="dailyBonus"]')
    CLAIM_BONUS      = (By.XPATH, '//button[normalize-space()="Claim Daily Bonus"]')
    ALREADY_CLAIMED  = (By.XPATH, '//*[contains(text(),"Come back tomorrow")]')
    # TODO: verify this selector against the live post-claim screen
    BALANCE          = (By.CSS_SELECTOR, '[data-testid="wallet"] [data-testid="balance"]')

    def login(self):
        username = read_credentials('stake_username')
        password = read_credentials('stake_password')

        notify('Navigating to Stake.us login')
        self.driver.get(self.URL)
        self.type_into(self.USERNAME, username)
        pass_el = self.type_into(self.PASSWORD, password)
        login_time = time.time()
        pass_el.send_keys(Keys.ENTER)

        self.wait.until(EC.staleness_of(pass_el))
        self.wait.until(EC.presence_of_element_located(self.EMAIL_CODE_INPUT))

        notify('Waiting for verification email...')
        code = get_verification_code('stake.us', received_after=login_time)
        notify(f'Verification code received: {code}')

        code_el = self.type_into(self.EMAIL_CODE_INPUT, code)
        code_el.send_keys(Keys.ENTER)

        self.wait.until(EC.element_to_be_clickable(self.WALLET))
        notify('Login successful', 'SUCCESS')

    def farm(self):
        already_claimed = self.driver.find_elements(*self.ALREADY_CLAIMED)
        if already_claimed:
            notify('Daily bonus already claimed — nothing to do', 'INFO')
            return

        self.click(self.WALLET)
        self.click(self.DAILY_BONUS)
        self.click(self.CLAIM_BONUS)

        self.wait.until(EC.staleness_of(
            self.driver.find_element(*self.CLAIM_BONUS)
        ))

        balance = self._read_balance()
        notify(f'Daily bonus claimed — balance: {balance}', 'SUCCESS')

    def _read_balance(self):
        try:
            el = self.wait.until(EC.presence_of_element_located(self.BALANCE))
            return el.text.strip() or 'unknown'
        except Exception:
            return 'unavailable (verify BALANCE selector)'


if __name__ == '__main__':
    notify('=== Stake.us harvest starting ===')
    try:
        StakeUS().run()
        notify('=== Harvest complete ===', 'SUCCESS')
    except Exception as e:
        notify(f'Harvest failed: {e}', 'ERROR')
        sys.exit(1)
