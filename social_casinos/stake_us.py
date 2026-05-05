import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))          # casino_base
sys.path.insert(0, str(Path(__file__).parent.parent))   # GmailVerification

import time
from casino_base import BaseCasino, read_credentials
from GmailVerification.GmailVerificationCode import get_verification_code
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC


class StakeUS(BaseCasino):
    URL = 'https://stake.us/?tab=login&modal=auth'

    USERNAME         = (By.NAME, 'emailOrName')
    PASSWORD         = (By.NAME, 'password')
    EMAIL_CODE_INPUT = (By.CSS_SELECTOR, 'input[type="text"]')
    EMAIL_CODE_BTN   = (By.XPATH, '//button[normalize-space()="Sign In"]')
    WALLET           = (By.CSS_SELECTOR, '[data-testid="wallet"]')
    DAILY_BONUS      = (By.CSS_SELECTOR, '[data-testid="dailyBonus"]')
    CLAIM_BONUS      = (By.XPATH, '//button[normalize-space()="Claim Daily Bonus"]')

    def login(self):
        username = read_credentials('stake_username')
        password = read_credentials('stake_password')

        self.driver.get(self.URL)
        self.type_into(self.USERNAME, username)
        pass_el = self.type_into(self.PASSWORD, password)
        login_time = time.time()
        pass_el.send_keys(Keys.ENTER)

        # Wait for the login form to go stale (page transition to code screen)
        self.wait.until(EC.staleness_of(pass_el))

        # Now the email code input is on the new screen
        self.wait.until(EC.presence_of_element_located(self.EMAIL_CODE_INPUT))
        print('Waiting for verification email...')
        code = get_verification_code('stake.us', received_after=login_time)
        print(f'Got code: {code}')

        code_el = self.type_into(self.EMAIL_CODE_INPUT, code)
        code_el.send_keys(Keys.ENTER)

        # Wallet button appears once fully logged in
        self.wait.until(EC.element_to_be_clickable(self.WALLET))

    def farm(self):
        self.click(self.WALLET)
        self.click(self.DAILY_BONUS)
        self.click(self.CLAIM_BONUS)
        # TODO: replace with WebDriverWait once success element CSS is known
        time.sleep(10)


if __name__ == '__main__':
    StakeUS().run()
