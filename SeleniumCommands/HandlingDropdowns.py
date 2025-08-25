import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

driver= webdriver.Chrome(service = Service(ChromeDriverManager().install()))

driver.implicitly_wait(10)  # Set implicit wait for 10 seconds
# Navigate to URL
driver.get("file:///C:/Users/giris/OneDrive/Desktop/dropdowns.html")

dropdownSelection= Select(driver.find_element(By.ID,"language"))

# Select by visible text
dropdownSelection.select_by_visible_text("JavaScript")

time.sleep(5)
# Select by index
dropdownSelection.select_by_index(2)

time.sleep(5)
# Select by value
dropdownSelection.select_by_value("py")
time.sleep(5)