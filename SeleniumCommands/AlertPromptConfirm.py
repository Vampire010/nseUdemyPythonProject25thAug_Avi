from ssl import AlertDescription
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common import service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


driver= webdriver.Chrome(service = Service(ChromeDriverManager().install()))

driver.implicitly_wait(10)  # Set implicit wait for 10 seconds
# Navigate to URL
driver.get("https://www.selenium.dev/documentation/webdriver/interactions/alerts/")

#Handling Browser Alerts
'''
elementAlert=driver.find_element(By.XPATH, "//*[contains(@onclick,'window.alert')]")
elementAlert.click()
AlertDescription = driver.switch_to.alert
print(AlertDescription.text)
AlertDescription.accept()
'''

# Handling Browser Confirm
'''
elementConfirm=driver.find_element(By.XPATH, "//*[contains(@onclick,'window.confirm')]")
driver.execute_script("arguments[0].click();", elementConfirm)
confirmDescription = driver.switch_to.alert
print(confirmDescription.text)
confirmDescription.dismiss()  # Dismiss the confirm alert
time.sleep(2)  
'''
# Handling Browser Prompts
elementPrompt = driver.find_element(By.XPATH, "//*[contains(@onclick,'window.prompt')]")
driver.execute_script("arguments[0].click();", elementPrompt)
time.sleep(2)
promptDescription = driver.switch_to.alert
print(promptDescription.text)
promptDescription.send_keys("Hello, this is a prompt test!")

promptDescription.accept()  # Accept the prompt alert
time.sleep(2)  # Wait for a while to see the result
