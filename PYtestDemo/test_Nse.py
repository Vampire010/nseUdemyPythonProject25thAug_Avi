import time
import openpyxl
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

url = "https://www.nseindia.com/market-data/top-gainers-losers"

# ✅ Initialize Excel Workbook
wb = openpyxl.Workbook()
gainers_sheet = wb.active
gainers_sheet.title = "Top Gainers"
losers_sheet = wb.create_sheet("Top Losers")

def fetch_table_with_headers(driver, table_id):
    table_data = []

    # Get headers
    headers = driver.find_elements(By.XPATH, f"//table[@id='{table_id}']/thead/tr/th")
    header_row = [header.text.strip() for header in headers]
    table_data.append(header_row)

    # Get rows
    rows = driver.find_elements(By.XPATH, f"//table[@id='{table_id}']/tbody/tr")
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        row_data = [cell.text.strip() for cell in cells]
        if row_data:
            table_data.append(row_data)

    return table_data

def save_to_sheet(sheet, data):
    for row in data:
        sheet.append(row)

def get_data(tab_id, table_id):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.implicitly_wait(10)
    driver.get(url)
    time.sleep(5)

    driver.find_element(By.ID, tab_id).click()
    time.sleep(2)

    data = fetch_table_with_headers(driver, table_id)
    driver.quit()
    return data

# ✅ Execution
start_time = time.time()

print("📈 Getting Gainers Data...")
gainers_data = get_data("GAINERS", "topgainer-Table")
save_to_sheet(gainers_sheet, gainers_data)

print("📉 Getting Losers Data...")
losers_data = get_data("LOSERS", "toplosers-Table")
save_to_sheet(losers_sheet, losers_data)

# ✅ Save Excel
filename = "nse_top_gainers_losers.xlsx"
wb.save(filename)
print(f"\n📁 Excel saved as: {filename}")

end_time = time.time()
print(f"⏱️ Execution Time: {end_time - start_time:.2f} seconds")
