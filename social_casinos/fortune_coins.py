#                   # 
#   FORTUNE COINS   # 
#                   # 

# Fortune Coins is one of the best social casino websites used in this project. 

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

#   ANTI-DETECTION   # 

# Mask IP Address
options = webdriver.ChromeOptions()
options.add_argument('proxy-server = 138.234.226.100')

# Use 'Undetected Chrome Driver' + Define path
chrome_driver_path = '/Users/gabrielguzman/Documents/Visual Studio Code/Projects/bonus-harvest/chromedriver'
driver = UC.Chrome(options)

#   CREDENTIALS   # 

def read_credentials(credential_type):
    credential_path = 'credentials.JSON'
    with open(credential_path, 'r') as file:
        credential_data = json.load(file)
    
    return credential_data.get(credential_type)
    
#   LOGIN   # 

def fortune_login(driver, read_credentials):
    # Input Timing Randomization (Anti-detection)
    input_time = random.uniform(0.01, 2)

    # Defines casino website URL
    casino_website = 'https://www.fortunecoins.com/public-lobby'

    # Opens social casino website
    driver.get(casino_website)
    time.sleep(input_time)

    # Open Login page
    login_element = driver.find_element(By.CSS_SELECTOR, '#__next > div.header-lobby-not-login > div > div.header-lobby-not-login-content > button')
    login_element.click()
    time.sleep(input_time)

    # Provides username + password credentials
    casino_username = read_credentials('fortune_username')
    casino_password = read_credentials('fortune_password')

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
    
#  FARMING   # 

# FIXME: fix below code
def fortune_farming(driver): 
    # Input Timing Randomization (Anti-detection)
    input_time = random.uniform(0.01, 2)

    # Find 'bonus_notification' element + Click
    bonus_notification = driver.find_element(By.CLASS_NAME, 'proceedButtton sp_proceed-daily-bonus-dialog btn btn-secondary')
    bonus_notification.click
    time.sleep(input_time)

    # Find 'Daily Bonus' element + Click 
    bonus_element = driver.find_element(By.CSS_SELECTOR, 'body > div:nth-child(12) > div > div.modal.fade.show > div > div > div.modal-body > div:nth-child(1) > div.coinsRow > div > div > button')
    bonus_element.click()
    time.sleep(input_time)

    # Find 'CloseSuccessfulBonus' element + Click
    closed_successful_bonus = driver.find_element(By.CSS_SELECTOR, 'body > div:nth-child(13) > div > div.modal.show > div > div > button')
    closed_successful_bonus.click()
    time.sleep(input_time)

# #   POP-UP   # 
    
# def fortune_pop_up(driver):
#     pop_up_element = driver.find_element(By.CSS_SELECTOR, 'body > div:nth-child(19) > div > div.modal.show > div > div > div > div > div.pre-connect-info-dialog-wrapper-bottom > div')


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
# fortune_login(driver, read_credentials)
# fortune_farming(driver)
# fortune_farming(driver)