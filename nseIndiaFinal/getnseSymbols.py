import requests
import pandas as pd
from io import StringIO

class NSEApi:
    BASE_URL = "https://www.nseindia.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.nseindia.com",
        })
    
    def get_equity_symbols(self):
        """Fetch all equity symbols from NSE official CSV."""
        url = f"{self.BASE_URL}/content/equities/EQUITY_L.csv"
        resp = self.session.get(url)
        resp.raise_for_status()
        
        df = pd.read_csv(StringIO(resp.text))
        return df["SYMBOL"].tolist()
    
    def get_index_symbols(self):
        """Fetch index symbols (like NIFTY, BANKNIFTY)."""
        url = f"{self.BASE_URL}/api/allIndices"
        resp = self.session.get(url)
        resp.raise_for_status()
        data = resp.json()
        return [idx["index"] for idx in data["data"]]
    
    def get_fno_symbols(self):
        """Fetch F&O tradable securities."""
        url = f"{self.BASE_URL}/api/equity-stockIndices?index=SECURITIES_IN_F&O"
        resp = self.session.get(url)
        resp.raise_for_status()
        data = resp.json()
        return [s["symbol"] for s in data["data"]]

nse = NSEApi()

print("Equity Symbols:", nse.get_equity_symbols()[:10])
print("Index Symbols:", nse.get_index_symbols())
print("F&O Symbols:", nse.get_fno_symbols()[:10])