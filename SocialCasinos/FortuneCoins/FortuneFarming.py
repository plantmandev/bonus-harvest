##                ## 
## INITIAL SET-UP ##
##                ## 

import undetected_chromedriver as UC
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
import time

# Change IP Address
options = webdriver.ChromeOptions()
options.add_argument('proxy-server=138.234.226.100')

# Set ChromeDriver as Selenium driver with 'undetected_chromedriver'
driver = UC.Chrome(options)
ChromeDriverPath = '/Users/gabrielguzman/Documents/Visual Studio Code/Projects/casino-farming/chromedriver'

# Input Timing Randomization (Anti-detection)
InputTime = random.uniform(0.01, 1)

##               ## 
## BONUS HARVEST ## 
##               ## 

# Find 'BonusNotification' element + Click
BonusNotification = driver.find_element(By.CSS_SELECTOR, 'body > div:nth-child(21) > div > div.modal.show > div > div > div.modal-body > div > button')
BonusNotification.click

# Find 'Daily Bonus' element + Click 
BonusElement = driver.find_element(By.CSS_SELECTOR, 'body > div:nth-child(12) > div > div.modal.fade.show > div > div > div.modal-body > div:nth-child(1) > div.coinsRow > div > div > button')
BonusElement.click()

# Find 'CloseSuccessfulBonus' element + Click
CloseSuccessfulBonus = driver.find_element(By.CSS_SELECTOR, 'body > div:nth-child(13) > div > div.modal.show > div > div > button')
CloseSuccessfulBonus.click()