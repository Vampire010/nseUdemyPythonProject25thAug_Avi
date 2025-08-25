import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common import service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

start_time = time.time()

driver= webdriver.Chrome(service = Service(ChromeDriverManager().install()))

driver.implicitly_wait(10)  # Set implicit wait for 10 seconds
# Navigate to URL
driver.get("https://www.nseindia.com/market-data/pre-open-market-cm-and-emerge-market")
time.sleep(5)  # Wait for the page to load completely
rows = driver.find_elements(By.XPATH, "//table[@id='livePreTable']/tbody/tr")
print(f"Total rows: {len(rows)}")

cell = driver.find_element(By.XPATH, "//table[@id='livePreTable']/tbody/tr[2]/td[1]")

for row in rows:
	cells = row.find_elements(By.TAG_NAME, "td")
	if len(cells) > 0:
		for cell in cells:
			print(cell.text, end=" | ")
		print()  # New line after each row
	else:
		print("No data in this row.")
		time.sleep(4)



end_time = time.time()
execution_time = end_time - start_time
print(f"\n⏱️ Execution Time: {execution_time:.2f} seconds")