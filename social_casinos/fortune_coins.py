#                   # 
#   FORTUNE COINS   # 
#                   # 

# Fortune Coins is one of the best social casino websites used in this project. 

#   INITIAL SET-UP   #
# Imports needed package 

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

#   ANTI-DETECTION   # 
# 

# Mask IP Address
options = webdriver.ChromeOptions()
options.add_argument('proxy-server=138.234.226.100')

# Use 'Undetected Chrome Driver' + Define path
driver = UC.Chrome(options)
chrome_driver_path = '/Users/gabrielguzman/Documents/Visual Studio Code/Projects/casino-farming/chromedriver'

# Input Timing Randomization (Anti-detection)
input_time = random.uniform(0.01, 1)

#   CREDENTIALS   # 
# Finds credentials based on CredentialType for different social casinos and returns value from 'credentials.JSON' file containing all login credentials

def read_credentials():
    # Define paths + credential type
    credential_path = 'credentials.JSON'
    credential_type = 'fortune_'

    # Read credentials.JSON file
    with open(credential_path, 'r') as file:
        CredentialsData = json.load(file) 
    
    # Look for CredentialType
    if credential_path in CredentialsData:
        return CredentialsData[credential_type]
    else:
        return None 
    
#   LOGIN   # 
# Uses selenium drivers and credentials.json to access casino website account

def fortune_login(driver, input_time, read_credentials):
    # Defines casino website URL
    casino_website = 'https://www.fortunecoins.com/public-lobby'

    # Opens social casino website
    driver.get(casino_website)
    time.sleep(input_time)

    # Open Login page
    login_element = driver.find_element(By.CSS_SELECTOR, '#__next > div.header-lobby-not-login > div > div.header-lobby-not-login-content > button')
    login_element.click()
    time.sleep(input_time)

    # Defines path for credentials file (used for login)
    credentials_path = 'credentials.JSON'

    # Find username input + Add username
    credentials_type = 'fortune_username'

    casino_username = ReadCredentials(credentials_path, credentials_type)
    username_element = driver.find_element(By.CSS_SELECTOR, "#emailAddress")
    username_element.click()
    username_element.send_keys(casino_username)
    time.sleep(input_time)

    # Find password input + Add password + Sign-in
    credentials_type = 'fortune_password'

    casino_password = ReadCredentials(credentials_path, credentials_type)
    password_element = driver.find_element(By.CSS_SELECTOR, "#password")
    password_element.click()
    password_element.send_keys(casino_password)
    password_element.send_keys(Keys.ENTER)
    time.sleep(100)
    
#   FARMING   # 
# Uses selenium driver to aquire daily bonus on casino website (Fortune Coins)

def fortune_farming(driver, input_time): 
    # Find 'BonusNotification' element + Click
    BonusNotification = driver.find_element(By.CSS_SELECTOR, 'body > div:nth-child(21) > div > div.modal.show > div > div > div.modal-body > div > button')
    BonusNotification.click
    time.sleep(input_time)

    # Find 'Daily Bonus' element + Click 
    BonusElement = driver.find_element(By.CSS_SELECTOR, 'body > div:nth-child(12) > div > div.modal.fade.show > div > div > div.modal-body > div:nth-child(1) > div.coinsRow > div > div > button')
    BonusElement.click()
    time.sleep(input_time)

    # Find 'CloseSuccessfulBonus' element + Click
    CloseSuccessfulBonus = driver.find_element(By.CSS_SELECTOR, 'body > div:nth-child(13) > div > div.modal.show > div > div > button')
    CloseSuccessfulBonus.click()
    time.sleep(input_time)

#   POP-UP   # 
# Function in charge of closing any pop-ups in 
    
def fortune_pop_up(driver):
    pop_up_element = driver.find_element(By.CSS_SELECTOR'body > div:nth-child(19) > div > div.modal.show > div > div > div > div > div.pre-connect-info-dialog-wrapper-bottom > div')


#   GLEANING   # 
# Helps determine which Slot to play based on availability
# index = 0 
# Slot = []

# # List of top most profitable slots
# ProfitableSlotList = ['Spooky Stories', 'Home of the Brave', 'Pyramids of Giza']

# # Open 'SearchBar'
# SearchBar = driver.find_element(By. CSS_SELECTOR, '#root > div > div.main.container-fluid > div.lobbyWrapper > div.advanced-search-bar > span > div > input')
# SearchBar.click()

# # Search for 'Slot' in 'ProfitableSlotList' 
# for slot in ProfitableSlotList[index]:
#     Slot.append(slot[index])

# SearchBar.send_keys(str(Slot))

# time.sleep(InputTime)

# # Open 'SearchResult'
# SearchResult = driver.find_element(By. CSS_SELECTOR, '#react-autowhatever-1--item-0')

# # Open most profitable slot
# OpenSlot = driver.find_element(By.CSS_SELECTOR, '')
# OpenSlot.click()
# time.sleep(5) # Change 

## ----------------------

# Uncomment + Run file 
fortune_login(driver, casino_website)
# fortune_farming(driver)