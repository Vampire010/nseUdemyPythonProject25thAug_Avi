import requests
import pandas as pd
import json
import os
from getCookiesFromNSEIndia import NSECookieManager


class CorporateActionsFetcher:
    def __init__(self):
        # Step 1: Fetch cookies
        try:
            cm = NSECookieManager()
            self.cookies = cm.fetch_and_save_cookies()
        except Exception as e:
            print(f"[ERROR] Failed to fetch cookies: {e}")
            self.cookies = {}

        # Step 2: Load saved cookies
        cookie_file = "nseIndiaCookies_name_value.json"
        try:
            if os.path.exists(cookie_file):
                with open(cookie_file, "r") as f:
                    auth_data = json.load(f)
            else:
                print(f"[WARNING] Cookie file not found: {cookie_file}")
                auth_data = {}
        except Exception as e:
            print(f"[ERROR] Failed to load cookie JSON: {e}")
            auth_data = {}

        # Safe cookie get
        def safe_get(key):
            return auth_data.get(key, "")

        cookie_str = ";".join([f"{k}={v}" for k, v in auth_data.items()])
        self.url = "https://www.nseindia.com/api/corporates-corporateActions?index=equities"
        self.headers = self._make_headers(cookie_str)

        # Step 3: Output location
        export_dir = r"C:\Users\giris\source\repos\nseDemoUemyPythonProject\nseIndia\exportedData"
        os.makedirs(export_dir, exist_ok=True)
        self.output_file = os.path.join(export_dir, "CorporateActions.xlsx")

    def _make_headers(self, cookie_str):
        return {
            'accept': '*/*',
            'accept-language': 'en-GB,en-IN;q=0.9,en-US;q=0.8,en;q=0.7',
            'priority': 'u=1, i',
            'referer': 'https://www.nseindia.com/companies-listing/corporate-filings-actions',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Cookie': cookie_str
        }

    def fetch_data(self):
        try:
            response = requests.get(self.url, headers=self.headers, timeout=15)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return None

    def save_to_excel(self, data):
        if not data:
            print("⚠ No data to save.")
            return
        try:
            # Handles both list and dict API responses
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict) and "data" in data:
                df = pd.DataFrame(data["data"])
            else:
                print("⚠ Unexpected data format.")
                return

            df.to_excel(self.output_file, index=False)
            print(f"✅ Data saved to {self.output_file}")
        except Exception as e:
            print(f"❌ Error saving data: {e}")

    def run(self):
        data = self.fetch_data()
        self.save_to_excel(data)


if __name__ == "__main__":
    fetcher = CorporateActionsFetcher()
    fetcher.run()
