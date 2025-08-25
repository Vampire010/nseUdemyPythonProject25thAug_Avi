import requests
import pandas as pd
import os
from getCookiesFromNSEIndia import NSECookieManager


class NSEMarketSnapshotFetcher:
    def __init__(self):
        """Initialize with cookies from NSECookieManager and set output path."""
        self.export_dir = r"C:\Users\giris\source\repos\nseDemoUemyPythonProject\nseIndia\exportedData"
        os.makedirs(self.export_dir, exist_ok=True)  # Create folder if it doesn't exist
        self.output_file = os.path.join(self.export_dir, "MarketSnapshotTopGainers.xlsx")

        self.headers = {}
        try:
            cm = NSECookieManager()
            cookies = cm.fetch_and_save_cookies()

            # Build cookie string
            cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            self.headers = {
                'accept': '*/*',
                'accept-language': 'en-GB,en-IN;q=0.9,en-US;q=0.8,en;q=0.7',
                'priority': 'u=1, i',
                'referer': 'https://www.nseindia.com/',
                'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                'cookie': cookie_str
            }
            print("✅ Cookies initialized successfully.")

        except Exception as e:
            print(f"❌ [ERROR] Failed to initialize cookies: {e}")

        self.url = "https://www.nseindia.com/api/NextApi/apiClient?functionName=getMarketSnapshot&&type=G"

    def fetch_market_snapshot(self):
        """Fetch and save top gainers from NSE market snapshot."""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ [Request Error] Failed to fetch data: {e}")
            return
        except ValueError:
            print("❌ [JSON Error] Failed to parse JSON response.")
            return
        except Exception as e:
            print(f"❌ [Unexpected Error] {e}")
            return

        try:
            top_gainers = data.get("data", {}).get("topGainers", [])
            if not top_gainers:
                print("⚠ No data found for top gainers.")
                return

            # Select and format columns
            df = pd.DataFrame(top_gainers, columns=[
                "symbol", "series", "openPrice", "highPrice", "lowPrice", "lastPrice",
                "previousClose", "change", "pchange", "totalTradedVolume"
            ])
            for col in ["openPrice", "highPrice", "lowPrice", "lastPrice", "previousClose", "change", "pchange"]:
                df[col] = df[col].round(2)

            # Save to Excel
            try:
                df.to_excel(self.output_file, index=False)
                print(f"✅ Top Gainers saved to {self.output_file}")
            except Exception as e:
                print(f"❌ [File Save Error] Could not save Excel file: {e}")

        except Exception as e:
            print(f"❌ [Processing Error] {e}")


if __name__ == "__main__":
    try:
        fetcher = NSEMarketSnapshotFetcher()
        fetcher.fetch_market_snapshot()
    except Exception as e:
        print(f"❌ [Fatal Error] Script failed: {e}")
