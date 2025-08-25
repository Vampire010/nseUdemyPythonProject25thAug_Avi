import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver= webdriver.Chrome(service = Service(ChromeDriverManager().install()))

# Navigate to URL
driver.get("https://www.nseindia.com/")

waitExplicit = WebDriverWait(driver, 10)
serchStockBynameSymbol= waitExplicit.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search by Company name, Index, Symbol or keyword... ']")))
serchStockBynameSymbol.send_keys("Reliance Industries Limited")
time.sleep(5)

#Below command will fail if the element is not present
#driver.find_element(By.XPATH,"//input[@placeholder='Search by Company name, Index, Symbol or keyword... ']").clear()

#Below command will wait for the element to be present and then clear it
serchStockBynameSymbol.clear()

time.sleep(10)