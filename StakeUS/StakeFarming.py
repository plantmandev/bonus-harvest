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

##         ## 
## FARMING ## 
##         ## 

# Find 'Wallet' element + Click
WalletElement = driver.find_element('#svelte > div.wrap.svelte-twylll > div.main-content.svelte-twylll > div.navigation.svelte-78xyui > div > div > div > div.balance-toggle.svelte-1rik8j6 > button')
WalletElement.click()
time.sleep(InputTime)

# Find 'Daily Bonus' element + Click 
BonusElement = driver.find_element(By.CSS_SELECTOR, '#svelte > div.modal.svelte-vepx8a > div.card.svelte-vepx8a > div.content.scrollY.scroll-contain.svelte-vepx8a > div > div > div.center-wrapper.svelte-fax2rm > div > div > div > button:nth-child(3) > span')
BonusElement.click()
time.sleep(InputTime)