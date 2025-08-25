from concurrent.futures import thread
from sqlite3 import Time
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common import service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


driver= webdriver.Chrome(service = Service(ChromeDriverManager().install()))

# Navigate to URL
driver.get("https://parabank.parasoft.com/parabank/register.htm")

'''
#1st Command - find_element(By.ID, "element_id")
driver.find_element(By.ID,"customer.firstName").send_keys("John")
time.sleep(5)

driver.find_element(By.ID,"customer.firstName").clear()
time.sleep(5)

driver.find_element(By.ID,"customer.firstName").send_keys("Smith")
time.sleep(5)
'''

driver.find_element(By.NAME,"username").send_keys("John")
driver.find_element(By.NAME,"password").send_keys("John@1234")
driver.find_element(By.XPATH,"//input[@value='Log In']").click()
time.sleep(5)
loginFailure = driver.find_element(By.XPATH,"//*[text()='An internal error has occurred and has been logged.']")

if loginFailure.is_displayed():
    print("Login failed, error message displayed.")
else:
    print("Login successful, no error message displayed.")

Forgotlogininfo = driver.find_element(By.LINK_TEXT,"Forgot login info?")
if Forgotlogininfo.is_enabled():
    print("Forgot login info link is enabled.")
else:
    print("Forgot login info link is not enabled.")

AboutUs = driver.find_element(By.PARTIAL_LINK_TEXT,"About")
if AboutUs.is_enabled():
    print("AboutUs link is enabled.")
else:
    print("AboutUs link is not enabled.")

driver.find_element(By.CSS_SELECTOR,"#loginPanel > p:nth-child(3) > a").click()
time.sleep(5)
driver.find_element(By.XPATH,"//*[@id='rightPanel']/p/text()").send_keys("John")
