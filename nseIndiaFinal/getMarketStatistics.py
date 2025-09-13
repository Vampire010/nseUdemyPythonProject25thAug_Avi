import requests
import pandas as pd
import json
import os
import time
import logging
from datetime import datetime
from openpyxl import load_workbook
from getCookiesFromNSEIndia import NSECookieManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the default log level
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    datefmt="%Y-%m-%d %H:%M:%S"  # Date format
)

class NSEMarketStatisticsExporter:
    def __init__(self):
        # Export folder
        self.export_dir = r"./exportedData"
        os.makedirs(self.export_dir, exist_ok=True)

        # Step 1: Get cookies
        try:
            cm = NSECookieManager()
            cm.fetch_and_save_cookies()
            logging.info("Cookies fetched and saved.")
        except Exception as e:
            logging.error(f"Failed to fetch cookies: {e}")

        # Step 2: Load cookies from JSON
        try:
            with open("nseIndiaCookies.json", "r") as f:
                auth_data = json.load(f)
            if isinstance(auth_data, list):
                # Build cookie string from list of dicts
                self.cookie_str = "; ".join(
                    [f"{c['name']}={c['value']}" for c in auth_data if 'name' in c and 'value' in c]
                )
            elif isinstance(auth_data, dict):
                self.cookie_str = auth_data.get("Cookie", "")
            else:
                self.cookie_str = ""
            logging.info("Cookies loaded from file.")
        except Exception as e:
            logging.error(f"Failed to load cookie JSON: {e}")
            self.cookie_str = ""

        # Step 3: Headers
        self.url = "https://www.nseindia.com/api/NextApi/apiClient?functionName=getMarketStatistics"
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-GB,en-IN;q=0.9,en-US;q=0.8,en;q=0.7',
            'referer': 'https://www.nseindia.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'cookie': self.cookie_str
        }

        # Use a session for faster requests
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def fetch_statistics(self):
        """Fetch market statistics from NSE API."""
        try:
            response = self.session.get(self.url, timeout=10)
            response.raise_for_status()
            logging.info("Successfully fetched market statistics.")
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            return None
        except ValueError:
            logging.error("Failed to parse JSON.")
            return None

    def append_to_excel(self, stats_data):
        """Append statistics to an existing Excel file."""
        try:
            snapshot = stats_data['data']['snapshotCapitalMarket']
            as_on_date = stats_data['data']['asOnDate']

            # Prepare DataFrame
            new_data = {
                "Stock Traded": snapshot.get('total'),
                "Unchanged": snapshot.get('unchange'),
                "Advances": snapshot.get('advances'),
                "Declines": snapshot.get('declines'),
                "As On Date": as_on_date
            }

            # File path
            output_file = os.path.join(self.export_dir, "MarketStatistics.xlsx")

            # Check if file exists
            if os.path.exists(output_file):
                # Load existing workbook and append data
                workbook = load_workbook(output_file)
                sheet = workbook.active
                sheet.append(list(new_data.values()))
                workbook.save(output_file)
                logging.info(f"Appended statistics to {output_file}")
            else:
                # Create new file if it doesn't exist
                df = pd.DataFrame([new_data])
                df.to_excel(output_file, index=False)
                logging.info(f"Created new file and added statistics to {output_file}")

        except KeyError as e:
            logging.error(f"Missing expected data in response: {e}")
        except Exception as e:
            logging.error(f"Failed to append to Excel: {e}")

    def run(self):
        while True:
            start_time = time.time()  # Start timing
            next_execution_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Log the current interval timestamp

            stats = self.fetch_statistics()
            if stats:
                self.append_to_excel(stats)

            end_time = time.time()  # End timing
            execution_time = end_time - start_time

            logging.info(f"Execution time: {execution_time:.2f} seconds | Interval: {next_execution_time}")

            time.sleep(30)  # Wait for 30 seconds before the next execution


if __name__ == "__main__":
    exporter = NSEMarketStatisticsExporter()
    exporter.run()