import os
import json
import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import logging
from typing import Dict, Optional, List
from getCookiesFromNSEIndia import NSECookieManager  # Import the cookie manager

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class NSEDataFetcher:
    def __init__(self):
        self.export_dir = r"./exportedData"
        os.makedirs(self.export_dir, exist_ok=True)

        self.documents_dir = r"./exportedData/"
        os.makedirs(self.documents_dir, exist_ok=True)

        # --- Step 1: Get cookies dynamically using NSECookieManager ---
        try:
            cm = NSECookieManager()
            self.cookies = cm.fetch_and_save_cookies()
        except Exception as e:
            logging.error(f"Failed to fetch cookies dynamically: {e}")
            self.cookies = {}

        # --- Step 2: Load saved cookies from file ---
        cookie_file = "nseIndiaCookies_name_value.json"
        if os.path.exists(cookie_file):
            try:
                with open(cookie_file, "r") as f:
                    auth_data = json.load(f)
            except Exception as e:
                logging.error(f"Failed to load cookie JSON: {e}")
                auth_data = {}
        else:
            logging.warning(f"Cookie file not found: {cookie_file}")
            auth_data = {}

        # Extract cookies safely
        def safe_get(key): return auth_data.get(key, "")

        cookie_str = (
            f"_ga={safe_get('_ga')};_abck={safe_get('_abck')};AKA_A2={safe_get('AKA_A2')};"
            f"nsit={safe_get('nsit')};nseappid={safe_get('nseappid')};bm_mi={safe_get('bm_mi')};"
            f"bm_sz={safe_get('bm_sz')};ak_bmsc={safe_get('ak_bmsc')};"
            f"_ga_87M7PJ3R97={safe_get('_ga_87M7PJ3R97')};bm_sv={safe_get('bm_sv')};RT={safe_get('RT')}"
        )

        self.url_template = "https://www.nseindia.com/api/quote-equity?symbol={symbol}&section=trade_info"
        self.headers = self._make_headers(cookie_str)

        # Configure session with retries
        self.session = self._configure_session()

    def _configure_session(self) -> requests.Session:
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def _make_headers(self, cookie_str: str) -> Dict[str, str]:
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

    def fetch_data(self, symbol: str) -> Optional[Dict]:
        url = self.url_template.format(symbol=symbol)
        try:
            logging.info(f"Fetching data for symbol: {symbol}")
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            logging.info(f"Successfully fetched data for symbol: {symbol}")
            return response.json()
        except requests.Timeout:
            logging.error(f"Timeout occurred while fetching data for symbol: {symbol}")
            return None
        except requests.RequestException as e:
            logging.error(f"Failed to fetch data for symbol: {symbol}. Error: {e}")
            return None

    def extract_and_save_security_wise_dp(self, data: Dict) -> Optional[Dict]:
        security_wise_dp = data.get("securityWiseDP", {})
        symbol = data.get("info", {}).get("symbol", "Unknown")
        if not security_wise_dp:
            logging.warning(f"No data found for {symbol}")
            return None

        security_wise_dp["symbol"] = symbol
        return security_wise_dp


if __name__ == "__main__":
    csv_path = r"./exportedData/datFiles/sec_bhavdata_full_12092025.csv"
    try:
        df = pd.read_csv(csv_path, sep=None, engine="python")
        logging.info(f"CSV loaded successfully. Columns: {df.columns.tolist()}")
    except Exception as e:
        logging.error(f"Failed to load CSV file: {e}")
        raise

    # Normalize column names
    df.columns = df.columns.str.strip().str.upper()

    # Strip spaces from SERIES column values
    if "SERIES" in df.columns:
        df["SERIES"] = df["SERIES"].str.strip()
        logging.info(f"Unique SERIES values after stripping: {df['SERIES'].unique()}")
    else:
        logging.error("SERIES column not found in the CSV file.")

    # Check for EQ symbols
    if "SERIES" in df.columns and "SYMBOL" in df.columns:
        eq_symbols = df.loc[df["SERIES"] == "EQ", "SYMBOL"].unique()
        logging.info(f"Found {len(eq_symbols)} EQ symbols")
    else:
        logging.error(f"Expected columns not found. Got: {df.columns.tolist()}")

    fetcher = NSEDataFetcher()
    all_data: List[Dict] = []

    for sym in eq_symbols:
        try:
            logging.info(f"Processing symbol: {sym}")
            data = fetcher.fetch_data(sym)
            if data:
                extracted = fetcher.extract_and_save_security_wise_dp(data)
                if extracted:
                    all_data.append(extracted)
            else:
                logging.warning(f"No data returned for symbol: {sym}")
        except Exception as e:
            logging.error(f"Error occurred while processing symbol: {sym}. Error: {e}")

    if all_data:
        out_df = pd.DataFrame(all_data)
        output_file = os.path.join(fetcher.export_dir, "AllSecurityWiseDP.xlsx")
        out_df.to_excel(output_file, index=False)
        logging.info(f"All data saved to {output_file}")