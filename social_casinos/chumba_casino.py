#                   # 
#   FORTUNE COINS   # 
#                   #  

#   INITIAL SET-UP   #
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
    
#   LOGIN   # 
def chumba_login(driver, read_credentials):
    # Input Timing Randomization (Anti-detection)
    input_time = random.uniform(0.01, 2)

    # Defines casino website URL
    casino_website = 'https://login.chumbacasino.com/'

    # Opens social casino website
    driver.get(casino_website)
    time.sleep(input_time)

    # Provides username + password credentials
    casino_username = read_credentials('chumba_username')
    casino_password = read_credentials('chumba_password')

    # Find username input + Add username
    username_element = driver.find_element(By.NAME, "email")
    username_element.click()
    username_element.send_keys(casino_username)
    time.sleep(input_time)

    # Find password input + Add password
    password_element = driver.find_element(By.NAME, "password")
    password_element.click()
    password_element.send_keys(casino_password)
    password_element.send_keys(Keys.ENTER)
    time.sleep(5)

#   FARMING   # 
def chumba_farming(driver):
    # Input Timing Randomization (Anti-detection)
    input_time = random.uniform(0.01, 2)

    # Find 'bonus_element' + Click 
    bonus_element = driver.find_element(By.CSS_SELECTOR, '#daily-bonus__claim-btn')
    bonus_element.click()
    time.sleep(input_time)

#   CLOSE POP-UPS   # 
def chumba_pop_up(driver):
    # Input Timing Randomization (Anti-detection)
    input_time = random.uniform(0.01, 2)

    # Find 'Pop-up closing' element + Click
    close_popup_element = driver.find_element(By.CSS_SELECTOR, '#offer__close')
    close_popup_element.click()
    time.sleep(input_time)

#   ANTI-DETECTION   # 

# Mask IP Address
options = webdriver.ChromeOptions()
options.add_argument('proxy-server = 138.234.226.100')

# Use 'Undetected Chrome Driver' + Define path
chrome_driver_path = '/Users/gabrielguzman/Documents/Visual Studio Code/Projects/bonus-harvest/chromedriver'
driver = UC.Chrome(options)

chumba_login(driver, read_credentials)

#TODO: Chumba requires email authenticaiton. Make gmail work only (for now)