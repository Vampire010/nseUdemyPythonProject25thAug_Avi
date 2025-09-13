import os
import json
import requests
import pandas as pd  # Ensure pandas is installed: pip install pandas

class NSEDataFetcher:
    def __init__(self):
        # Fixed export folder
        self.export_dir = r"./exportedData"
        os.makedirs(self.export_dir, exist_ok=True)

        # Directory for downloaded documents
        self.documents_dir = r"./exportedData/nse_announcements/DocumentsToAnalyze"
        os.makedirs(self.documents_dir, exist_ok=True)

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
        self.url = "https://www.nseindia.com/api/quote-equity?symbol=LODHA&section=trade_info"
        self.headers = self._make_headers(cookie_str)

    def _make_headers(self, cookie_str):
        return {
            'accept': '*/*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'priority': 'u=1, i',
            'referer': 'https://www.nseindia.com/get-quotes/equity?symbol=LODHA',
            'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Cookie': cookie_str
        }

    def fetch_data(self):
        response = requests.get(self.url, headers=self.headers)
        return response.json()  # Parse response as JSON

    def extract_and_save_security_wise_dp(self, data):
        # Extract securityWiseDP
        security_wise_dp = data.get("securityWiseDP", {})
        symbol = data.get("info", {}).get("symbol", "Unknown")  # Extract symbol name
        if not security_wise_dp:
            print("[WARNING] No securityWiseDP data found in the response.")
            return

        # Add symbol name to the data
        security_wise_dp["symbol"] = symbol

        # Convert to DataFrame
        df = pd.DataFrame([security_wise_dp])

        # Save to Excel
        output_file = os.path.join(self.export_dir, "SecurityWiseDP.xlsx")
        df.to_excel(output_file, index=False)
        print(f"[INFO] Data saved to {output_file}")


if __name__ == "__main__":
    fetcher = NSEDataFetcher()
    data = fetcher.fetch_data()
    fetcher.extract_and_save_security_wise_dp(data)