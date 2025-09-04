import requests
import json
import os
from getCookiesFromNSEIndia import NSECookieManager

class OptionChainContractInfoFetcher:
    def __init__(self, symbol="NIFTY"):
        self.symbol = symbol
        self.url = f"https://www.nseindia.com/api/option-chain-contract-info?symbol={self.symbol}"

        # Fetch cookies
        cm = NSECookieManager()
        cm.fetch_and_save_cookies()

        # Load saved cookies
        cookie_file = "nseIndiaCookies_name_value.json"
        if os.path.exists(cookie_file):
            with open(cookie_file, "r") as f:
                auth_data = json.load(f)
        else:
            auth_data = {}

        cookie_str = ";".join([f"{k}={v}" for k, v in auth_data.items()])

        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'priority': 'u=1, i',
            'referer': 'https://www.nseindia.com/option-chain',
            'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Cookie': cookie_str
        }

    def fetch_and_print_first_expiry(self):
        response = requests.get(self.url, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        expiry_dates = data.get("expiryDates", [])
        if expiry_dates:
            print("First expiry date:", expiry_dates[0])
        else:
            print("No expiry dates found.")

    def get_first_expiry_date(self):
        response = requests.get(self.url, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        expiry_dates = data.get("expiryDates", [])
        if expiry_dates:
            return expiry_dates[0]
        else:
            return None

if __name__ == "__main__":
    fetcher = OptionChainContractInfoFetcher(symbol="NIFTY")
    fetcher.fetch_and_print_first_expiry()