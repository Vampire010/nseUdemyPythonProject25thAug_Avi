
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common import service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


driver= webdriver.Chrome(service = Service(ChromeDriverManager().install()))

driver.implicitly_wait(10)  # Set implicit wait for 10 seconds
# Navigate to URL
driver.get("https://www.nseindia.com/")

driver.find_element(By.XPATH,"//input[@placeholder='Search by Company name, Index, Symbol or keyword... ']").send_keys("Reliance")

time.sleep(5)

driver.find_element(By.XPATH,"//input[@placeholder='Search by Company name, Index, Symbol or keyword... ']").clear()

time.sleep(5)