import sys
import time
from datetime import timedelta

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from .base import BaseCasino, read_credentials, notify


class FortuneCoins(BaseCasino):
    URL = 'https://www.fortunecoins.com/public-lobby'

    LOGIN_BUTTON    = (By.XPATH,        '//button[.//span[text()="Log In"]]')
    LOGIN_SUBMIT    = (By.CSS_SELECTOR, 'button.loginFormButtton')
    USERNAME        = (By.CSS_SELECTOR, '#emailAddress')
    PASSWORD        = (By.CSS_SELECTOR, '#password')

    BONUS_POPUP_WAIT = 10
    BONUS_POPUP_SELECTORS = [
        (By.CSS_SELECTOR, '.transparent-close-popup-button'),
        (By.CSS_SELECTOR, '.modal.fade.show button.close'),
        (By.CSS_SELECTOR, '.modal.fade.show [data-dismiss="modal"]'),
        (By.XPATH,        '//div[contains(@class,"modal") and contains(@class,"show")]//button[contains(@class,"close")]'),
    ]

    # TODO: verify selectors against live site
    COIN_STORE_BTN = (By.CSS_SELECTOR, '.coin-store-button button')
    READY_BONUS    = (By.XPATH, '/html/body/div[3]/div/div[1]/div/div/div[2]/div/button')
    COLLECT_BONUS  = (By.CSS_SELECTOR, (
        'body > div:nth-child(22) > div > div.modal.fade.show > div > div > '
        'div.modal-body > div:nth-child(1) > div.coinsRow > div:nth-child(1) > '
        'div > div.daily-bonus-buttons-wrapper'
    ))
    CLOSE_BONUS    = (By.CSS_SELECTOR, (
        'body > div:nth-child(22) > div > div.modal.fade.show > div > div > button'
    ))
    FC_BALANCE     = (By.CSS_SELECTOR, (
        '#__next > div.headerAuth > div.headerContainer > nav > '
        'div.headerAuthCenter > div > div > div.FCDropDown > div > div:nth-child(3) > h3'
    ))

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

    def _dismiss_bonus_popup(self):
        w = WebDriverWait(self.driver, self.BONUS_POPUP_WAIT)
        for locator in self.BONUS_POPUP_SELECTORS:
            try:
                btn = w.until(EC.element_to_be_clickable(locator))
                self.driver.execute_script('arguments[0].click()', btn)
                return
            except TimeoutException:
                pass

    def farm(self) -> timedelta:
        self.screenshot('farm_start')

        notify('Clicking coin store...')
        self.click(self.COIN_STORE_BTN)
        self.screenshot('after_coin_store')

        notify('Clicking ready bonus...')
        self.click(self.READY_BONUS)
        self.screenshot('after_ready_bonus')

        notify('Collecting bonus...')
        self.click(self.COLLECT_BONUS)
        self.screenshot('after_collect')

        self.click(self.CLOSE_BONUS)
        balance_el = self.wait.until(lambda d: d.find_element(*self.FC_BALANCE))
        balance = balance_el.text.strip()
        self.record_balance(balance)
        notify(f'Daily bonus claimed — balance: {balance}', 'SUCCESS')
        return timedelta(hours=24)


if __name__ == '__main__':
    notify('=== Fortune Coins harvest starting ===')
    try:
        FortuneCoins().run()
        notify('=== Harvest complete ===', 'SUCCESS')
    except Exception as e:
        notify(f'Harvest failed: {e}', 'ERROR')
        sys.exit(1)
