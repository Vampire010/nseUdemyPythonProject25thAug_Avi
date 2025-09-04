import requests
import pandas as pd

class BroadMarketIndicesExporter:
    def __init__(self):
        self.url = "https://www.nseindia.com/api/heatmap-index?type=Broad%20Market%20Indices"
        self.payload = {}
        self.headers = {
            'accept': '*/*',
            'accept-language': 'en-GB,en-IN;q=0.9,en-US;q=0.8,en;q=0.7',
            'priority': 'u=1, i',
            'referer': 'https://www.nseindia.com/market-data/live-market-indices/heatmap',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Cookie': '_ga=GA1.1.1106664733.1754978687; AKA_A2=A; ...'  # Truncated for brevity
        }

        self.data = None
        self.indices_list = []

    def fetch_data(self):
        response = requests.request("GET", self.url, headers=self.headers, data=self.payload)
        try:
            self.data = response.json()
        except Exception as e:
            print("JSON decode error:", e)
            self.data = None
        return self.data

    def process_indices(self):
        if isinstance(self.data, dict):
            for value in self.data.values():
                if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                    self.indices_list = value
                    break
            else:
                self.indices_list = []
        else:
            self.indices_list = self.data if isinstance(self.data, list) else []
        return self.indices_list

    def export_to_excel(self, filename="broad_market_indices.xlsx"):
        if self.indices_list:
            df = pd.DataFrame(self.indices_list)
            df.to_excel(filename, index=False)
            print(f"Exported to {filename}")
        else:
            print("No tabular data found in response.")

if __name__ == "__main__":
    exporter = BroadMarketIndicesExporter()
    exporter.fetch_data()
    exporter.process_indices()
    exporter.export_to_excel()