import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common import service
from webdriver_manager.chrome import ChromeDriverManager

driver= webdriver.Chrome(service = Service(ChromeDriverManager().install()))

#1st Command - get(url)
driver.get("https://www.udemy.com/courses/search/?q=python&src=sac&kw=python")


#2nd Commad
print("Title:", driver.title)

#3rd Command -maximize_window
driver.maximize_window()
time.sleep(5)

getCurrent_url = driver.current_url
print("Current URL:", getCurrent_url)
#11th Command - close()
driver.close()