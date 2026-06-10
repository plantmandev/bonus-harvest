import sys
import time
from datetime import timedelta

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from .base import BaseCasino, read_credentials, notify


class FortuneWins(BaseCasino):
    URL = 'https://www.fortunewins.com/public-lobby'

    LOGIN_BUTTON    = (By.XPATH,        '//button[.//span[text()="Log In"]]')
    LOGIN_SUBMIT    = (By.CSS_SELECTOR, 'button.loginFormButtton')
    USERNAME        = (By.CSS_SELECTOR, '#emailAddress')
    PASSWORD        = (By.CSS_SELECTOR, '#password')

    BONUS_POPUP_WAIT = 10  # seconds to wait for first popup
    BONUS_POPUP_SELECTORS = [
        (By.CSS_SELECTOR, '.transparent-close-popup-button'),
        # "Daily bonus is ready" popup — .modal.show without .fade
        (By.CSS_SELECTOR, '.modal.show > div > div > button'),
        # "Connect with Google / Facebook" popups — button sibling of .modal-body
        (By.CSS_SELECTOR, 'div.modal-body ~ button'),
        (By.XPATH,        '//div[contains(@class,"modal-body")]/following-sibling::button'),
        (By.CSS_SELECTOR, '.modal.fade.show button.close'),
        (By.CSS_SELECTOR, '.modal.fade.show [data-dismiss="modal"]'),
        (By.XPATH,        '//div[contains(@class,"modal") and contains(@class,"show")]//button[contains(@class,"close")]'),
    ]

    COIN_STORE_BTN  = (By.CSS_SELECTOR, '.coin-store-button button')
    FREE_COINS_TAB  = (By.CSS_SELECTOR, 'div.coin-store-tabs > button:nth-child(2)')
    COLLECT_BONUS   = (By.CSS_SELECTOR, 'button.daily-bonus-collect-button')
    # Balance: click the FC coin button to expand it, then read the decimal value
    FC_BALANCE_BTN  = (By.CSS_SELECTOR, 'div.FCButtonItem.FCoins > button')
    FC_BALANCE_VAL  = (By.CSS_SELECTOR, 'div.FCButtonItem.active.FCoins > button > div.textDecimals.desktop')
    # TODO: add next-bonus countdown selector once confirmed
    BONUS_TIMER     = None

    TOS_SCROLL   = (By.CSS_SELECTOR, '.consent-page-update-dialog__body-scroll')
    TOS_CHECKBOX = (By.ID,           'terms-conditions-updated-dialog-checkbox')
    TOS_CONFIRM  = (By.CSS_SELECTOR, '.consent-page-update-dialog__btn')
    TOS_WAIT     = 10

    def login(self):
        username = read_credentials('fortune_username')
        password = read_credentials('fortune_password')

        self.driver.get(self.URL)
        self.click(self.LOGIN_BUTTON)
        # Use JS click to avoid ElementClickInterceptedException from the login modal overlay
        username_el = self.wait.until(EC.presence_of_element_located(self.USERNAME))
        self.driver.execute_script('arguments[0].click()', username_el)
        username_el.send_keys(username)
        pass_el = self.wait.until(EC.presence_of_element_located(self.PASSWORD))
        self.driver.execute_script('arguments[0].click()', pass_el)
        pass_el.send_keys(password)
        pass_el.send_keys(Keys.ENTER)
        time.sleep(3)
        self.click(self.LOGIN_SUBMIT)
        self._accept_tos()
        self._dismiss_bonus_popup()
        notify('Login successful', 'SUCCESS')

    def _accept_tos(self):
        w = WebDriverWait(self.driver, self.TOS_WAIT)
        try:
            w.until(EC.url_contains('fortunewins.com/lobby'))
            scroll = w.until(EC.presence_of_element_located(self.TOS_SCROLL))
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scroll)
            checkbox = w.until(EC.presence_of_element_located(self.TOS_CHECKBOX))
            self.driver.execute_script('arguments[0].click()', checkbox)
            confirm = w.until(EC.presence_of_element_located(self.TOS_CONFIRM))
            self.driver.execute_script('arguments[0].click()', confirm)
        except TimeoutException:
            pass

    _MODAL_PRESENT = (By.CSS_SELECTOR, '.modal.show, .modal.fade.show, div.modal-body')

    def _dismiss_bonus_popup(self, max_rounds: int = 5):
        """Dismiss all stacked post-login popups, one per round."""
        for round_num in range(max_rounds):
            # After the first round, do a free instant check before burning timeout per selector
            if round_num > 0:
                time.sleep(0.8)  # let close animation settle
                if not self.driver.find_elements(*self._MODAL_PRESENT):
                    notify(f'All popups cleared after {round_num} round(s)')
                    return

            w = WebDriverWait(self.driver, self.BONUS_POPUP_WAIT if round_num == 0 else 5)
            dismissed = False

            for locator in self.BONUS_POPUP_SELECTORS:
                try:
                    btn = w.until(EC.element_to_be_clickable(locator))
                    self.driver.execute_script('arguments[0].click()', btn)
                    notify(f'Popup dismissed (round {round_num + 1})')
                    dismissed = True
                    break
                except TimeoutException:
                    pass

            if not dismissed:
                # Fallback: Escape key
                try:
                    self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                    time.sleep(0.5)
                except Exception:
                    pass
                if round_num > 0:
                    notify(f'All popups cleared after {round_num} round(s)')
                return

        # Last-resort JS force-hide if we exhausted rounds
        try:
            self.driver.execute_script(
                "document.querySelectorAll('.modal.show,.modal.fade.show')"
                ".forEach(m => m.style.display='none')"
            )
            notify('Remaining popups force-hidden via JS', 'WARNING')
        except Exception:
            pass

    def farm(self) -> timedelta:
        self.screenshot('farm_start')

        notify('Clicking coin store...')
        self.click(self.COIN_STORE_BTN)
        self.screenshot('after_coin_store')

        notify('Clicking free coins tab...')
        self.click(self.FREE_COINS_TAB)
        self.screenshot('after_free_coins_tab')

        notify('Collecting daily bonus...')
        self.click(self.COLLECT_BONUS)
        self.screenshot('after_collect')

        # Close coin store popup before reading nav balance
        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
        time.sleep(1)
        balance = self._read_fc_balance()
        self.record_balance(balance)
        notify(f'Daily bonus claimed — balance: {balance}', 'SUCCESS')
        return timedelta(hours=24, minutes=1)

    def _read_fc_balance(self) -> str:
        try:
            notify('Reading FC balance...')
            self.click(self.FC_BALANCE_BTN)
            el = self.wait.until(EC.visibility_of_element_located(self.FC_BALANCE_VAL))
            raw   = el.text.strip().replace(',', '')
            value = float(raw) / 100
            return f'{value:.2f} FC'
        except Exception:
            return 'unavailable'


if __name__ == '__main__':
    notify('=== Fortune Wins harvest starting ===')
    try:
        FortuneWins().run()
        notify('=== Harvest complete ===', 'SUCCESS')
    except Exception as e:
        notify(f'Harvest failed: {e}', 'ERROR')
        sys.exit(1)
