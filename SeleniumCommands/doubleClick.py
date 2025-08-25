import time
from requests import get
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common import service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
driver= webdriver.Chrome(service = Service(ChromeDriverManager().install()))

driver.get("file:///C:/Users/giris/source/repos/nseDemoUemyPythonProject/htmlCode/doubleClick.html")
driver.implicitly_wait(10)  # Set implicit wait for 10 seconds
box = driver.find_element(By.ID, "buttondoubleclick")
actions=webdriver.ActionChains(driver)  

# Get original color
original_color = box.value_of_css_property("background-color")
print("Before double-click:", original_color)
time.sleep(4) 

# Perform double-click
actions.double_click(box).perform()

time.sleep(4) 

 # Get new color
new_color = box.value_of_css_property("background-color")
print("After double-click:", new_color)

