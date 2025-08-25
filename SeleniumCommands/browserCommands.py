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
driver.get("https://www.nseindia.com/")

getTotalRegisteredInvestors= driver.find_element(By.XPATH,"//a[@href='/registered-investors' and @title='To view all, click here']")
if getTotalRegisteredInvestors.is_displayed():
    print("Total Registered Investors :" , getTotalRegisteredInvestors.text)
else:
    print("Total Registered Investors link is not displayed.")

#1st Command - get(url)
driver.get("https://www.udemy.com/courses/search/?q=python&src=sac&kw=python")


#2nd Commad
print("Title:", driver.title)

#3rd Command -maximize_window
driver.maximize_window()
time.sleep(5)

#4th Command minimize_window
driver.minimize_window()
time.sleep(5)

#5th Command - fullscreen_window()
driver.fullscreen_window()
time.sleep(5)

#6th Command - refresh()
driver.refresh()

driver.get("https://www.udemy.com/courses/search/?q=Java&src=sac&kw=Java")

#7th Command - page_source()
print("Page Source :", driver.page_source)

#8th Command - back
driver.back()

time.sleep(5)

#9th Command - forward
driver.forward()

#10th Command - quit()
#driver.quit();

# Get the current URL
getCurrent_url = driver.current_url
print("Current URL:", getCurrent_url)

#11th Command - close()
driver.close()