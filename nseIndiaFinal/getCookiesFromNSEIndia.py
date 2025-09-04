import time
import pickle
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class NSECookieManager:
    def __init__(self, url="https://www.nseindia.com/", pkl_file="nseIndiaCookies.pkl"):
        self.url = url
        self.pkl_file = pkl_file
        self.driver = None

    def _init_driver(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Uncomment for headless
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                                       options=chrome_options)

    def fetch_and_save_cookies(self):
        self._init_driver()

        # Always start fresh — visit the site
        self.driver.get(self.url)
        time.sleep(5)  # Wait for full load

        # Save cookies to PKL (overwrite if exists)
        with open(self.pkl_file, "wb") as file:
            pickle.dump(self.driver.get_cookies(), file)
        print(f"Cookies saved to {self.pkl_file}")

        # Read cookies back from PKL
        with open(self.pkl_file, "rb") as file:
            cookies = pickle.load(file)

        # Save full cookies to JSON (overwrite)
        with open("nseIndiaCookies.json", "w") as json_file:
            json.dump(cookies, json_file, indent=4)
        print("Cookies saved to nseIndiaCookies.json")

        # Save name-value cookies only (overwrite)
        cookies_name_value = {cookie["name"]: cookie["value"] for cookie in cookies}
        with open("nseIndiaCookies_name_value.json", "w") as json_file:
            json.dump(cookies_name_value, json_file, indent=4)
        print("Saved name-value cookies to nseIndiaCookies_name_value.json")

        self.driver.quit()
        return cookies_name_value


if __name__ == "__main__":
    cm = NSECookieManager()
    cm.fetch_and_save_cookies()
