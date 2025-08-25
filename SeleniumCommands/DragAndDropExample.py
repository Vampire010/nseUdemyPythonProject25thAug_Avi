import time
from requests import get
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common import service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


driver= webdriver.Chrome(service = Service(ChromeDriverManager().install()))


driver.get("file:///C:/Users/giris/source/repos/nseDemoUemyPythonProject/dragDrop.html")

source = driver.find_element(By.ID, "drag1")
target = driver.find_element(By.ID, "div2")

actionDriver = webdriver.ActionChains(driver)

# Perform drag and drop action
webdriver.ActionChains(driver).drag_and_drop(source, target).perform()

