import sys
import time
from datetime import timedelta

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from .base import BaseCasino, read_credentials, notify
from auth.gmail import get_verification_code

WALLET_RETRY_WAIT = 5
WALLET_MAX_RETRIES = 3


class StakeUS(BaseCasino):
    URL = 'https://stake.us/?tab=login&modal=auth'

    USERNAME         = (By.NAME, 'emailOrName')
    PASSWORD         = (By.NAME, 'password')
    EMAIL_CODE_INPUT = (By.CSS_SELECTOR, 'input[type="text"]')
    WALLET           = (By.CSS_SELECTOR, '#navigation-container-header > div.w-full.flex.justify-center > div > button')
    DAILY_BONUS      = (By.CSS_SELECTOR, '[data-testid="dailyBonus"]')
    CLAIM_BONUS      = (By.XPATH, '//button[normalize-space()="Claim Daily Bonus"]')
    ALREADY_CLAIMED  = (By.XPATH, '//*[contains(text(),"Come back tomorrow")]')
    WALLET_ERROR     = (By.XPATH, '//*[contains(text(),"something") and contains(text(),"wrong")]')
    # SC balance: 3rd currency card in the wallet overview, value span inside .value-ctainer
    SC_BALANCE       = (By.CSS_SELECTOR,
        'div.flex.flex-col.gap-4 > div > div:nth-child(3) > div > div.value-ctainer > span > span')
    # Countdown elements: number sits before its unit label
    TIMER_DAY        = (By.XPATH, '//*[normalize-space(text())="Day"]/preceding-sibling::*[1]')
    TIMER_HOUR       = (By.XPATH, '//*[normalize-space(text())="Hour"]/preceding-sibling::*[1]')
    TIMER_MIN        = (By.XPATH, '//*[normalize-space(text())="Min"]/preceding-sibling::*[1]')

    def login(self):
        username = read_credentials('stake_username')
        password = read_credentials('stake_password')

        notify('Navigating to Stake.us login')
        self.driver.get(self.URL)
        self.type_into(self.USERNAME, username)
        pass_el    = self.type_into(self.PASSWORD, password)
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

    def farm(self) -> timedelta:
        self.screenshot('farm_start')

        notify('Clicking wallet...')
        self._open_wallet_with_retry()
        self.screenshot('after_wallet')

        notify('Clicking daily bonus...')
        self.click(self.DAILY_BONUS)
        self.screenshot('after_daily_bonus')

        # Check already-claimed inside the wallet where the state is actually visible
        if self.driver.find_elements(*self.ALREADY_CLAIMED):
            notify('Daily bonus already claimed — nothing to do')
            self.screenshot('already_claimed')
            return self._read_next_claim_delta()

        notify('Clicking claim button...')
        self.click(self.CLAIM_BONUS)
        self.screenshot('after_claim')

        self.wait.until(EC.staleness_of(self.driver.find_element(*self.CLAIM_BONUS)))
        self.screenshot('claim_complete')
        balance = self._read_sc_balance()
        self.record_balance(balance)
        notify(f'Daily bonus claimed — balance: {balance}', 'SUCCESS')
        return self._read_next_claim_delta()

    def _open_wallet_with_retry(self):
        for attempt in range(1, WALLET_MAX_RETRIES + 1):
            self.click(self.WALLET)
            time.sleep(WALLET_RETRY_WAIT)
            if not self.driver.find_elements(*self.WALLET_ERROR):
                return
            notify(f'Wallet error dialog detected (attempt {attempt}) — closing and retrying', 'WARNING')
            self.driver.find_element(*self.WALLET).click()  # close the wallet
            time.sleep(2)
        raise RuntimeError('Wallet error persisted after retries — aborting')

    def _read_sc_balance(self) -> str:
        try:
            from selenium.webdriver.common.keys import Keys as _Keys
            # Close any open wallet/overlay before reopening to avoid toggle-close
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(_Keys.ESCAPE)
            time.sleep(1)
            self.click(self.WALLET)
            el = self.wait.until(EC.visibility_of_element_located(self.SC_BALANCE))
            return f'{el.text.strip()} SC'
        except Exception:
            return 'unavailable'

    def _read_next_claim_delta(self) -> timedelta:
        try:
            days  = int(self.driver.find_element(*self.TIMER_DAY).text.strip()  or 0)
            hours = int(self.driver.find_element(*self.TIMER_HOUR).text.strip() or 0)
            mins  = int(self.driver.find_element(*self.TIMER_MIN).text.strip()  or 0)
            notify(f'Next claim in {days}d {hours}h {mins}m')
            return timedelta(days=days, hours=hours, minutes=mins + 1)
        except Exception:
            notify('Could not read next claim timer — defaulting to 24h', 'WARNING')
            return timedelta(hours=24)


if __name__ == '__main__':
    notify('=== Stake.us harvest starting ===')
    try:
        StakeUS().run()
        notify('=== Harvest complete ===', 'SUCCESS')
    except Exception as e:
        notify(f'Harvest failed: {e}', 'ERROR')
        sys.exit(1)
