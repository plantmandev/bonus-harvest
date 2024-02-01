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

# Anti-detection Input Randomization
InputTime = random.uniform(0.01, 1)

#          #
# GLEANING # 
#          #

# Helps determine which Slot to play based on availability
index = 0 
Slot = []

# List of top most profitable slots
ProfitableSlotList = ['Spooky Stories', 'Home of the Brave', 'Pyramids of Giza']

# Open 'SearchBar'
SearchBar = driver.find_element(By. CSS_SELECTOR, '#root > div > div.main.container-fluid > div.lobbyWrapper > div.advanced-search-bar > span > div > input')
SearchBar.click()

# Search for 'Slot' in 'ProfitableSlotList' 
for slot in ProfitableSlotList[index]:
    Slot.append(slot[index])

SearchBar.send_keys(str(Slot))

time.sleep(InputTime)

# Open 'SearchResult'
SearchResult = driver.find_element(By. CSS_SELECTOR, '#react-autowhatever-1--item-0')

# Open most profitable slot
OpenSlot = driver.find_element(By.CSS_SELECTOR, '')
OpenSlot.click()
time.sleep(5) # Change 