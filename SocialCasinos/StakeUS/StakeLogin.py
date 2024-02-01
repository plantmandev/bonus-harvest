##                ## 
## INITIAL SET-UP ##
##                ## 

from SocialCasinos.ChumbaCasino.credentials import ReadCredentials
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
CasinoWesbite = 'https://stake.us/?tab=login&modal=auth'

driver.get(CasinoWesbite)
time.sleep(InputTime)

# Defines path for credentials file (used for login)
CredentialsPath = 'credentials.JSON'

# Find username input + Add username
CredentialType = 'StakeUsername'

CasinoUsername = ReadCredentials(CredentialsPath, CredentialType)
UsernameElement = driver.find_element(By.NAME, "emailOrName")
UsernameElement.click()
UsernameElement.send_keys(CasinoUsername)
time.sleep(InputTime)

# Find password input + Add password + Sign-in
CredentialType = 'StakePassword'

CasinoPassword = ReadCredentials(CredentialsPath, CredentialType)
PasswordElement = driver.find_element(By.NAME, "password")
PasswordElement.click()
PasswordElement.send_keys(CasinoPassword)
PasswordElement.send_keys(Keys.ENTER)
# time.sleep(InputTime)
time.sleep(10)