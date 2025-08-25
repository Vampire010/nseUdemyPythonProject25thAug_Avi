import requests
import pandas as pd
import json
import os
from getCookiesFromNSEIndia import NSECookieManager


class NseDataFetcher:
    """Class to fetch and process Nifty indices data from NSE API."""

    def __init__(self):
        # Export folder path
        self.export_dir = r"C:\Users\giris\source\repos\nseDemoUemyPythonProject\nseIndia\exportedData"
        os.makedirs(self.export_dir, exist_ok=True)  # Create if doesn't exist

        # --- Step 1: Get cookies safely ---
        try:
            cm = NSECookieManager()
            self.cookies = cm.fetch_and_save_cookies()
        except Exception as e:
            print(f"[ERROR] Failed to fetch cookies: {e}")
            self.cookies = {}

        self.marketIndices = [
            "Broad Market Indices",
            "Sectoral Indices"
        ]

        # --- Step 2: Load saved cookies from file ---
        cookie_file = "nseIndiaCookies_name_value.json"
        if os.path.exists(cookie_file):
            try:
                with open(cookie_file, "r") as f:
                    auth_data = json.load(f)
            except Exception as e:
                print(f"[ERROR] Failed to load cookie JSON: {e}")
                auth_data = {}
        else:
            print(f"[WARNING] Cookie file not found: {cookie_file}")
            auth_data = {}

        # Extract cookies safely
        def safe_get(key):
            return auth_data.get(key, "")

        _ga = safe_get("_ga")
        abck = safe_get("_abck")
        AKA_A2 = safe_get("AKA_A2")
        nsit = safe_get("nsit")
        nseappid = safe_get("nseappid")
        bm_mi = safe_get("bm_mi")
        bm_sz = safe_get("bm_sz")
        ak_bmsc = safe_get("ak_bmsc")
        _ga_87M7PJ3R97 = safe_get("_ga_87M7PJ3R97")
        bm_sv = safe_get("bm_sv")
        RT = safe_get("RT")

        cookie_str = (
            f'_ga={_ga};_abck={abck};AKA_A2={AKA_A2};nsit={nsit};nseappid={nseappid};'
            f'bm_mi={bm_mi};bm_sz={bm_sz};ak_bmsc={ak_bmsc};_ga_87M7PJ3R97={_ga_87M7PJ3R97};'
            f'bm_sv={bm_sv};RT={RT}'
        )

        self.url = "https://www.nseindia.com/api/live-analysis-variations?index=gainers"
        self.headers = self._make_headers(cookie_str)
        self.output_file = os.path.join(self.export_dir, "LiveAnalysisVariationsGainersData.xlsx")

    def _make_headers(self, cookie_str):
        return {
            'accept': '*/*',
            'accept-language': 'en-GB,en-IN;q=0.9,en-US;q=0.8,en;q=0.7',
            'priority': 'u=1, i',
            'referer': 'https://www.nseindia.com/market-data/top-gainers-losers',
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
        """Fetch JSON data from NSE API."""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching data: {e}")
            return None
        except ValueError:
            print("❌ Failed to parse JSON from response.")
            return None

    def process_and_save(self, data):
        """Extract required indices and save to Excel."""
        if not data:
            print("⚠ No data to process.")
            return

        try:
            indices = {
                "NIFTY 50": data.get("NIFTY", {}).get("data", []),
                "BANK NIFTY": data.get("BANKNIFTY", {}).get("data", []),
                "NIFTY NEXT 50": data.get("NIFTYNEXT50", {}).get("data", []),
                "F&O Securities": data.get("FOSec", {}).get("data", [])
            }

            with pd.ExcelWriter(self.output_file) as writer:
                for sheet_name, records in indices.items():
                    df = pd.DataFrame(records)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

            print(f"✅ Data saved to {self.output_file}")
        except Exception as e:
            print(f"❌ Error processing/saving data: {e}")

    def run(self):
        """Main execution method."""
        data = self.fetch_data()
        self.process_and_save(data)


if __name__ == "__main__":
    nse_fetcher = NseDataFetcher()
    nse_fetcher.run()
