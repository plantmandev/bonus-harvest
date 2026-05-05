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
    WALLET           = (By.CSS_SELECTOR, (
        '#svelte > div.wrap.svelte-twylll > div.main-content.svelte-twylll > '
        'div.navigation.svelte-78xyui > div > div > div > '
        'div.balance-toggle.svelte-1rik8j6 > button'
    ))
    BONUS            = (By.CSS_SELECTOR, (
        '#svelte > div.modal.svelte-vepx8a > div.card.svelte-vepx8a > '
        'div.content.scrollY.scroll-contain.svelte-vepx8a > div > div > '
        'div.center-wrapper.svelte-fax2rm > div > div > div > button:nth-child(3) > span'
    ))

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
        self.click(self.BONUS)


if __name__ == '__main__':
    StakeUS().run()
