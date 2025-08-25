import requests
import pandas as pd
import json
import os
from datetime import datetime
from getCookiesFromNSEIndia import NSECookieManager


class OptionChainFetcher:
    def __init__(self, symbol="NIFTY", expiry="21-Aug-2025"):
        self.symbol = symbol
        self.expiry = expiry
        self.today_str = datetime.now().strftime("%d-%m-%Y")

        print(f"📅 Fetching Option Chain for {self.symbol} expiry {self.expiry} on {self.today_str}")

        # Fetch cookies
        cm = NSECookieManager()
        self.cookies = cm.fetch_and_save_cookies()

        # Load saved cookies
        cookie_file = "nseIndiaCookies_name_value.json"
        if os.path.exists(cookie_file):
            with open(cookie_file, "r") as f:
                auth_data = json.load(f)
        else:
            auth_data = {}

        cookie_str = ";".join([f"{k}={v}" for k, v in auth_data.items()])

        self.url = f"https://www.nseindia.com/api/option-chain-v3?type=Indices&symbol={self.symbol}&expiry={self.expiry}"
        self.headers = self._make_headers(cookie_str)

        export_dir = r"C:\Users\giris\source\repos\nseDemoUemyPythonProject\nseIndia\exportedData"
        os.makedirs(export_dir, exist_ok=True)
        self.output_file = os.path.join(
            export_dir, f"OptionChain_{self.symbol}_{self.expiry}_{self.today_str}.xlsx"
        )

    def _make_headers(self, cookie_str):
        return {
            'accept': '*/*',
            'accept-language': 'en-GB,en-IN;q=0.9,en-US;q=0.8,en;q=0.7',
            'referer': 'https://www.nseindia.com/option-chain',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Cookie': cookie_str
        }

    def fetch_data(self):
        response = requests.get(self.url, headers=self.headers, timeout=20)
        response.raise_for_status()
        return response.json()

    def save_to_excel(self, data):
        if not data or "records" not in data or "data" not in data["records"]:
            print("⚠ Unexpected data format")
            return

        rows = []
        for item in data["records"]["data"]:
            strike = item.get("strikePrice", None)

            ce = item.get("CE", {})
            pe = item.get("PE", {})

            row = {
                # CALLS
                "CALL_OI": ce.get("openInterest"),
                "CALL_CHNG_OI": ce.get("changeinOpenInterest"),
                "CALL_VOLUME": ce.get("totalTradedVolume"),
                "CALL_IV": ce.get("impliedVolatility"),
                "CALL_LTP": ce.get("lastPrice"),
                "CALL_CHNG": ce.get("change"),
                "CALL_BID_QTY": ce.get("buyQuantity1"),
                "CALL_BID": ce.get("buyPrice1"),
                "CALL_ASK": ce.get("sellPrice1"),
                "CALL_ASK_QTY": ce.get("sellQuantity1"),

                # STRIKE
                "STRIKE": strike,

                # PUTS
                "PUT_BID_QTY": pe.get("buyQuantity1"),
                "PUT_BID": pe.get("buyPrice1"),
                "PUT_ASK": pe.get("sellPrice1"),
                "PUT_ASK_QTY": pe.get("sellQuantity1"),
                "PUT_CHNG": pe.get("change"),
                "PUT_LTP": pe.get("lastPrice"),
                "PUT_IV": pe.get("impliedVolatility"),
                "PUT_VOLUME": pe.get("totalTradedVolume"),
                "PUT_CHNG_OI": pe.get("changeinOpenInterest"),
                "PUT_OI": pe.get("openInterest"),
            }
            rows.append(row)

        df = pd.DataFrame(rows)

        # Arrange columns like NSE website
        column_order = [
            "CALL_OI", "CALL_CHNG_OI", "CALL_VOLUME", "CALL_IV", "CALL_LTP", "CALL_CHNG",
            "CALL_BID_QTY", "CALL_BID", "CALL_ASK", "CALL_ASK_QTY",
            "STRIKE",
            "PUT_BID_QTY", "PUT_BID", "PUT_ASK", "PUT_ASK_QTY", "PUT_CHNG", "PUT_LTP",
            "PUT_IV", "PUT_VOLUME", "PUT_CHNG_OI", "PUT_OI"
        ]

        df = df[column_order]

        df.to_excel(self.output_file, index=False)
        print(f"✅ Option Chain table saved: {self.output_file}")

    def run(self):
        try:
            data = self.fetch_data()
            self.save_to_excel(data)
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    fetcher = OptionChainFetcher(symbol="NIFTY", expiry="21-Aug-2025")
    fetcher.run()
