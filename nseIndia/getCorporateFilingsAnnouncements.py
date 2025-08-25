import requests
import pandas as pd
import json
import os
from getCookiesFromNSEIndia import NSECookieManager


class CorporateAnnouncementsFetcher:
    def __init__(self):
        # Fixed export folder
        self.export_dir = r"C:\Users\giris\source\repos\nseDemoUemyPythonProject\nseIndia\exportedData"
        os.makedirs(self.export_dir, exist_ok=True)

        # Step 1: Get cookies safely
        try:
            cm = NSECookieManager()
            self.cookies = cm.fetch_and_save_cookies()
        except Exception as e:
            print(f"[ERROR] Failed to fetch cookies: {e}")
            self.cookies = {}

        # Step 2: Load saved cookies from file
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

        # Extract cookies safely
        def safe_get(key):
            return auth_data.get(key, "")

        _ga = safe_get("_ga")
        _abck = safe_get("_abck")
        AKA_A2 = safe_get("AKA_A2")
        nsit = safe_get("nsit")
        nseappid = safe_get("nseappid")
        bm_mi = safe_get("bm_mi")
        bm_sz = safe_get("bm_sz")
        ak_bmsc = safe_get("ak_bmsc")
        _ga_87M7PJ3R97 = safe_get("_ga_87M7PJ3R97")
        bm_sv = safe_get("bm_sv")
        RT = safe_get("RT")

        # Combine into cookie string
        cookie_str = (
            f"_ga={_ga};_abck={_abck};AKA_A2={AKA_A2};nsit={nsit};nseappid={nseappid};"
            f"bm_mi={bm_mi};bm_sz={bm_sz};ak_bmsc={ak_bmsc};_ga_87M7PJ3R97={_ga_87M7PJ3R97};"
            f"bm_sv={bm_sv};RT={RT}"
        )

        # API endpoint
        self.url = "https://www.nseindia.com/api/corporate-announcements?index=equities"
        self.headers = self._make_headers(cookie_str)

        # Output file path
        self.output_file = os.path.join(self.export_dir, "CorporateFilingsAnnouncements.xlsx")

    def _make_headers(self, cookie_str):
        return {
            'accept': '*/*',
            'accept-language': 'en-GB,en-IN;q=0.9,en-US;q=0.8,en;q=0.7',
            'priority': 'u=1, i',
            'referer': 'https://www.nseindia.com/companies-listing/corporate-filings-announcements',
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
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching data: {e}")
        except ValueError:
            print("❌ Failed to parse JSON.")
        return None

    def save_to_excel(self, data):
        if not data:
            print("⚠ No data to save.")
            return
        try:
            # If API returns a list directly
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict) and "data" in data:
                df = pd.DataFrame(data["data"])
            else:
                print("⚠ Unexpected data format from API.")
                return

            df.to_excel(self.output_file, index=False)
            print(f"✅ Data saved to {self.output_file}")
        except Exception as e:
            print(f"❌ Error saving data: {e}")


    def run(self):
        data = self.fetch_data()
        self.save_to_excel(data)


if __name__ == "__main__":
    fetcher = CorporateAnnouncementsFetcher()
    fetcher.run()
