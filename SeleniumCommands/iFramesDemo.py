import time
from requests import get
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common import service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
driver= webdriver.Chrome(service = Service(ChromeDriverManager().install()))

driver.get("file:///C:/Users/giris/source/repos/nseDemoUemyPythonProject/htmlCode/iframecode.html")
time.sleep(5)  # Wait for a while to see the result

# ✅ Switch to iframe by name and get title or element
driver.switch_to.frame("wikipediaFrame")
print("Inside wikipediaFrame")
driver.find_element(By.ID, "searchInput").send_keys("Python (programming language)")
driver.find_element(By.XPATH, "//*[@id='search-form']/fieldset/button").click()

time.sleep(5)  # Wait for a while to see the result

 # Switch back to the main content
driver.switch_to.default_content() 

#✅ Switch to another iframe
driver.switch_to.frame(driver.find_element(By.ID, "iframe2"))
print("Inside wikibooksFrame")
driver.find_element(By.ID, "searchInput").send_keys("Python (programming language)")
driver.find_element(By.XPATH, "//*[@id='search-form']/fieldset/button").click()
time.sleep(5)  # Wait for a while to see the result
