##                ## 
## INITIAL SET-UP ##
##                ## 

from credentials import ReadCredentials
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

##        ## 
## LOG-IN ## 
##        ## 

# Opens social casino website
CasinoWesbite = 'https://www.fortunecoins.com/public-lobby'

driver.get(CasinoWesbite)
time.sleep(InputTime)

# Open Login page
LoginElement = driver.find_element(By.CSS_SELECTOR, '#root > div > div.header-lobby-not-login > div > div.header-lobby-not-login-content > button')
LoginElement.click()
time.sleep(InputTime)

# Defines path for credentials file (used for login)
CredentialsPath = 'credentials.JSON'

# Find username input + Add username
CredentialType = 'FortuneCoinUsername'

CasinoUsername = ReadCredentials(CredentialsPath, CredentialType)
UsernameElement = driver.find_element(By.CSS_SELECTOR, "#emailAddress")
UsernameElement.click()
UsernameElement.send_keys(CasinoUsername)
time.sleep(InputTime)

# Find password input + Add password + Sign-in
CredentialType = 'FortuneCoinPassword'

CasinoPassword = ReadCredentials(CredentialsPath, CredentialType)
PasswordElement = driver.find_element(By.CSS_SELECTOR, "#password")
PasswordElement.click()
PasswordElement.send_keys(CasinoPassword)
PasswordElement.send_keys(Keys.ENTER)
time.sleep(InputTime)