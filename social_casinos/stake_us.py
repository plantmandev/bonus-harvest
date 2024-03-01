#              # 
#   STAKE US   # 
#              # 

#  

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

def stake_login(driver, read_credentials):
    # Input Timing Randomization (Anti-detection)
    input_time = random.uniform(0.01, 2)

    # Defines casino website URL
    casino_website = 'https://stake.us/?tab=login&modal=auth'

    # Opens social casino website
    driver.get(casino_website)
    time.sleep(input_time)

    # Provides username + password credentials
    casino_username = read_credentials('stake_username')
    casino_password = read_credentials('stake_password')

    # Find username input + Add username
    username_element = driver.find_element(By.NAME, "emailOrName")
    username_element.click()
    username_element.send_keys(casino_username)
    time.sleep(input_time)

    # Find password input + Add password
    password_element = driver.find_element(By.NAME, "password")
    password_element.click()
    password_element.send_keys(casino_password)
    password_element.send_keys(Keys.ENTER)
    time.sleep(25)

def stake_farming(driver): 
    # Input Timing Randomization (Anti-detection)
    input_time = random.uniform(0.01, 2)

    # Find 'wallet_element' + Click
    wallet_element = driver.find_element(By.CSS_SELECTOR, '#svelte > div.wrap.svelte-twylll > div.main-content.svelte-twylll > div.navigation.svelte-78xyui > div > div > div > div.balance-toggle.svelte-1rik8j6 > button')
    wallet_element.click()
    time.sleep(input_time)

    # Find 'Daily Bonus' element + Click 
    bonus_element = driver.find_element(By.CSS_SELECTOR, '#svelte > div.modal.svelte-vepx8a > div.card.svelte-vepx8a > div.content.scrollY.  scroll-contain.svelte-vepx8a > div > div > div.center-wrapper.svelte-fax2rm > div > div > div > button:nth-child(3) > span')
    bonus_element.click()
    time.sleep(input_time)

stake_login(driver, read_credentials)
stake_farming(driver)