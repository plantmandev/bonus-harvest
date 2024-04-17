import json
import time
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
import undetected_chromedriver as UC

#   CREDENTIALS   # 
def read_credentials(credential_type):
    credential_path = 'credentials.JSON'
    with open(credential_path, 'r') as file:
        credential_data = json.load(file)
    
    return credential_data.get(credential_type)
    

# Defines casino website URL
casino_website = 'https://www.fortunecoins.com/public-lobby'

# Mask IP Address
options = webdriver.ChromeOptions()
options.add_argument('proxy-server = 138.234.226.100')

# Use 'Undetected Chrome Driver' + Define path
chrome_driver_path = '/Users/gabrielguzman/Documents/Visual Studio Code/Projects/bonus-harvest/chromedriver'
driver = UC.Chrome(options)

# Input Timing Randomization (Anti-detection)
input_time = random.uniform(0.01, 2)

# Username + password credentials
casino_username = read_credentials('fortune_username')
casino_password = read_credentials('fortune_password')


#   LOGIN   # 
def fortune(driver, read_credentials):
    # Opens social casino website
    driver.get(casino_website)
    time.sleep(input_time)

    # Open Login page
    login_element = driver.find_element(By.CSS_SELECTOR, '#__next > div.logged-out-header > div.desktop-logged-out-header > div > nav > div.login-button-container > button')
    login_element.click()
    time.sleep(input_time)

    # Find username input + Add username
    username_element = driver.find_element(By.CSS_SELECTOR, "#emailAddress")
    username_element.click()
    username_element.send_keys(casino_username)
    time.sleep(input_time)

    # Find password input + Add password
    password_element = driver.find_element(By.CSS_SELECTOR, "#password")
    password_element.click()
    password_element.send_keys(casino_password)
    password_element.send_keys(Keys.ENTER)
    time.sleep(5) 

    # # popup 
    # pop_up_element = driver.find_element(By.CSS_SELECTOR, 'body > div:nth-child(19) > div > div.modal.show > div > div > div > div > div.pre-connect-info-dialog-wrapper-bottom > div')
    # pop_up_element.click()

    # Find 'ready_bonus_element' + Click
    ready_bonus_element = driver.find_element(By.XPATH, '/html/body/div[3]/div/div[1]/div/div/div[2]/div/button')

    #  # Find 'bonus_notification' element + Click
    # free_coin_element = driver.find_element(By.CLASS_NAME, '#__next > div.headerAuth > div > nav > div.headerButtons > div.coin-store-button > button')
    # free_coin_element.click
    # time.sleep(input_time)

    # Find 'collect_bonus_element' element + Click 
    collect_bonus_element = driver.find_element(By.CSS_SELECTOR, 'body > div:nth-child(22) > div > div.modal.fade.show > div > div > div.modal-body > div:nth-child(1) > div.coinsRow > div:nth-child(1) > div > div.daily-bonus-buttons-wrapper')
    collect_bonus_element.click()
    time.sleep(input_time)

    # Find 'close_successful_bonus_element' element + Click
    closed_successful_bonus_element = driver.find_element(By.CSS_SELECTOR, 'body > div:nth-child(22) > div > div.modal.fade.show > div > div > button')
    closed_successful_bonus_element.click()
    time.sleep(input_time)

    # Find total FC count + Click
    FC_element = driver.find_element(By.CSS_SELECTOR, '#__next > div.headerAuth > div > nav > div.headerAuthCenter > div > div > div.FCButtonItem.sp_fc-__SPPN__-header.FCoins > button > img')
    FC_element.click()

    # Find FC balance 
    FC_balance_element = driver.find_element( By.CSS_SELECTOR, '#__next > div.headerAuth > div.headerContainer > nav > div.headerAuthCenter > div > div > div.FCDropDown > div > div:nth-child(3) > h3')
    FC_balance_element.getText()



fortune(driver, read_credentials)