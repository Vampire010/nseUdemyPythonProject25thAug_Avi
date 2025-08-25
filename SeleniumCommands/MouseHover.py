import time
from requests import get
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common import service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
driver= webdriver.Chrome(service = Service(ChromeDriverManager().install()))

driver.get("file:///C:/Users/giris/source/repos/nseDemoUemyPythonProject/htmlCode/mouseHover.html")
driver.implicitly_wait(10)  # Set implicit wait for 10 seconds
time.sleep(5)  # Wait for a while to see the result
hoverable = driver.find_element(By.XPATH, "/html/body/div[17]")
webdriver.ActionChains(driver).move_to_element(hoverable).perform()
time.sleep(5)  # Wait for a while to see the result