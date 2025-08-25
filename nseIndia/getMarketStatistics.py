import requests
import pandas as pd
import json
import os
from getCookiesFromNSEIndia import NSECookieManager


class NSEMarketStatisticsExporter:
    def __init__(self):
        # Export folder
        self.export_dir = r"C:\Users\giris\source\repos\nseDemoUemyPythonProject\nseIndia\exportedData"
        os.makedirs(self.export_dir, exist_ok=True)

        # Step 1: Get cookies
        try:
            cm = NSECookieManager()
            cm.fetch_and_save_cookies()
            print("✅ Cookies fetched and saved.")
        except Exception as e:
            print(f"❌ Failed to fetch cookies: {e}")

        # Step 2: Load cookies from JSON
        try:
            with open("nseIndiaCookies.json", "r") as f:
                auth_data = json.load(f)
            cookie_str = auth_data.get("Cookie", "")
            print("✅ Cookies loaded from file.")
        except Exception as e:
            print(f"❌ Failed to load cookie JSON: {e}")
            cookie_str = ""

        # Step 3: Headers
        self.url = "https://www.nseindia.com/api/NextApi/apiClient?functionName=getMarketStatistics"
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-GB,en-IN;q=0.9,en-US;q=0.8,en;q=0.7',
            'referer': 'https://www.nseindia.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'cookie': cookie_str
        }

    def fetch_statistics(self):
        """Fetch market statistics from NSE API."""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
        except ValueError:
            print("❌ Failed to parse JSON.")
            return None

    def export_to_excel(self, stats_data):
        """Export statistics to Excel in export folder."""
        try:
            snapshot = stats_data['data']['snapshotCapitalMarket']
            as_on_date = stats_data['data']['asOnDate']

            # Prepare DataFrame
            df = pd.DataFrame([{
                "Stock Traded": snapshot.get('total'),
                "Unchanged": snapshot.get('unchange'),
                "Advances": snapshot.get('advances'),
                "Declines": snapshot.get('declines'),
                "As On Date": as_on_date
            }])

            # Save file
            output_file = os.path.join(self.export_dir, "MarketStatistics.xlsx")
            df.to_excel(output_file, index=False)
            print(f"✅ Exported statistics to {output_file}")

        except KeyError as e:
            print(f"❌ Missing expected data in response: {e}")
        except Exception as e:
            print(f"❌ Failed to export Excel: {e}")

    def run(self):
        stats = self.fetch_statistics()
        if stats:
            self.export_to_excel(stats)


if __name__ == "__main__":
    exporter = NSEMarketStatisticsExporter()
    exporter.run()
