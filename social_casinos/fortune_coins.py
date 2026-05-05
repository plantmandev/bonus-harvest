import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from casino_base import BaseCasino, read_credentials
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class FortuneCoins(BaseCasino):
    URL = 'https://www.fortunecoins.com/public-lobby'

    LOGIN_BUTTON = (By.CSS_SELECTOR, (
        '#__next > div.logged-out-header > div.desktop-logged-out-header > '
        'div > nav > div.login-button-container > button'
    ))
    USERNAME = (By.CSS_SELECTOR, '#emailAddress')
    PASSWORD = (By.CSS_SELECTOR, '#password')
    POPUP = (By.CSS_SELECTOR, (
        'body > div:nth-child(19) > div > div.modal.show > div > div > div > '
        'div > div.pre-connect-info-dialog-wrapper-bottom > div'
    ))
    # TODO: remaining farming selectors need verification against the live site
    READY_BONUS = (By.XPATH, '/html/body/div[3]/div/div[1]/div/div/div[2]/div/button')
    COLLECT_BONUS = (By.CSS_SELECTOR, (
        'body > div:nth-child(22) > div > div.modal.fade.show > div > div > '
        'div.modal-body > div:nth-child(1) > div.coinsRow > div:nth-child(1) > '
        'div > div.daily-bonus-buttons-wrapper'
    ))
    CLOSE_BONUS = (By.CSS_SELECTOR, (
        'body > div:nth-child(22) > div > div.modal.fade.show > div > div > button'
    ))
    FC_BALANCE = (By.CSS_SELECTOR, (
        '#__next > div.headerAuth > div.headerContainer > nav > '
        'div.headerAuthCenter > div > div > div.FCDropDown > div > div:nth-child(3) > h3'
    ))

    def login(self):
        username = read_credentials('fortune_username')
        password = read_credentials('fortune_password')

        self.driver.get(self.URL)
        self.click(self.LOGIN_BUTTON)
        self.type_into(self.USERNAME, username)
        pass_el = self.type_into(self.PASSWORD, password)
        pass_el.send_keys(Keys.ENTER)
        self.click(self.POPUP)

    def farm(self):
        self.click(self.READY_BONUS)
        self.click(self.COLLECT_BONUS)
        self.click(self.CLOSE_BONUS)

        balance_el = self.wait.until(
            lambda d: d.find_element(*self.FC_BALANCE)
        )
        print(f'FC Balance: {balance_el.text}')


if __name__ == '__main__':
    FortuneCoins().run()
