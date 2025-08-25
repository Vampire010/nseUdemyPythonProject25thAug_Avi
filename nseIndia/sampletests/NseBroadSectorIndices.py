import requests
import pandas as pd
import time

class NseGainersExporter:
    def __init__(self):
        self.url_template = "https://www.nseindia.com/api/heatmap-symbols?type=Broad%20Market%20Indices&indices={indices}"
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
                  'Cookie': '_ga=GA1.1.1106664733.1754978687; _abck=346A27E6C086CA11FDB53173602C8D94~0~YAAQhNcLF4drsp+YAQAAMhyioQ7QI4qhyLaQh611X9AHUd5r5Qnyey6jjuIOKKUi3tV0FAM0IdGOEwmOXrvx9PZEQqLIfWubKzfHhukUsygUdLhCFjE8OdJHP6xRCg9ukoudkznij01xwZhNnRkV6efANwKZB+fUQCze9wRM2jbE0tVanuaX57e96OLPheyrDR4yCSwR6inf6svNo4n1nLAh7F71TQX1SFp8yJrm6fvPFbkL1RywcTxqaPe8JGEC+7AJEOrOldmTPyygFvZUUte6N9JA2PHcgYbdF/WIQxSwfAVw/DO7duMo7RX0gsMrFG8j+gcWPcfZXM8gewazLlB9EnYcNeT4qopzixdGD/YOzgj/dq5E2sHePVY5dJko31qMAsvGsZALwP83M6GgAJZzkWojgsBlROGTBstOUdBuuJ11FAEpwMzn+m0oGWSncKajIiqHyH+ovROk8+ASpqAYmsb6yjyhve146wxioamwf33fUF0iBfAkMZENx5E2YLPzjQj1EQyV7Y/VxBjmW2mJG2FIoNGPlY8LmqoQWaeWX/QwQJwh+q/dUEr8RIWuqlnMedDnSVIgha5b/UOQseWdjtCy0pHr+uDAqBDwZX0OYrH87q5V0hpKjZ3dUPE2Jmj3yGs=~-1~-1~-1; AKA_A2=A; nsit=PcSEnuIWYbvVrk1_qJbgLkUk; nseappid=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhcGkubnNlIiwiYXVkIjoiYXBpLm5zZSIsImlhdCI6MTc1NTA2NTkxMiwiZXhwIjoxNzU1MDczMTEyfQ.Aun5oMpwuyaZGIq8ftSON_H1cj3-A9gnGOX0NxDV9B4; bm_mi=DFDB12E28C9EB7BDA56B55D19657D370~YAAQhNcLFxZ9y5+YAQAA1owUohyuODbfWuROJsNckv6pyBz10JRyCnK+UENm94RtxtnfLI412WJV0zr5+wTZcEgDZk6iGFGanc6+6whvzy0DrZ5M8yqJuE6BoHkJEKjUGd+toibhGxiKewGB6w8pS1emlrlKaKRmK2UgNqkghV8XUc35X0zH77XhfNRXs90od2yj3aRZkJv/+rpcgHRgNcstuneE0sZ0fC+7fSVLnr7tHSGvCeVdb0LdUfbkKwwvQzQmFcSrNgmS5+TEpxoM6+6cstTpCQY+LLDQm0oPFNfG0CmDkpvpDJe+jHR7/T2UZ8MoFvay2gAgpF4UlpiOXxw42LMA2bkiEUhkptDis0PKkrI4kD8=~1; bm_sz=B75DBBB6399435276CD17D5077768F2F~YAAQhNcLFxh9y5+YAQAA1owUohw6x3lfzDNpB6j2uH8r9xmHelwUdnmNni8wRYe78OLFYJUFixqpRSS8qjqDAJLhgDJolExIw/eCDYUfu2EaMUBMYjatsRzAObqcnvuQjG+ipfX2fmc9WCLzflDH1ihc3PAOoJN71tUxJaz3DWpHg2dOu5B7XvxkdXOK9nSNbyGjGlGlprtAOo1de70uilDLebfeQLpBEsG+Jg9koA+U3fgSmigXcB4dzccXFy/G4wL5EslJCzYMvI2ilRj1yRDeDblP0EKNhycOhErHYDujld7CZZgjcYtEpj+7iiQa6VZKul76AAUtaqT7mMiQBbdm0YMkm/uanxaSTICiYTLlR+2+hF0ymLZrb14G6C90uUVR/rRfYGKLSfqHNuWQ5pqpnrof1QAL/3X1+FLKiMttCEEAvNTzgDBQ2kEPD6GCdXJZp55zsIDOS1Aowbd9dUK6UjocR6W1/jUGYNqisL1TbGYnYLEmVW5EcZ2FKAkHfdGrF4KCHD589bFE29KJhk3alqZoVTJBpmdNch0AfRBf4s+AhP0OF8Q=~4338480~3491395; ak_bmsc=4CBF9DBDB05560F364C30B925D636C56~000000000000000000000000000000~YAAQhNcLFxJ+y5+YAQAAUJIUohzPg2vQQJTE7NqRP18XneIfttpvu2PwvPfQIiv/59FrCRGqRmYMo6bxMPnD7m3s9m2krTmHvdA5YkMpNMIfGwhg+0P/x9+RaIdhOG9rPiLj33qg/Q3UbWFGyP0SBNfYV3jVLdc3j9E69H95PC+M4xATn2YH4pv+wwlYJY/tJzP/cObv3HRYV3DNOFP3ok0tz0xG1jkbnRAoZnkwONOGYiVbYOCeplNPjJuy44TJURq7aKTbfscJaln1YSwBTo/A3HBvYN58vV4RcuGflh77O7hyRQSBn9KpnOPvoWkCd79y+JUAk8T87LoHG1gm9LEFNIezDN8/TJT3Fv4uIiQbi3XLT/C+LdM0s5F7zZlGgIgdJmYEPjiwcP7SuZVnG+HmhJ0cmYeCSOxpcTmmsPNmQdnWOfU2xS8qz8CFv1C5h0CQKdtW/W4xHQzSr2SODOfN9ZGKXABQerL3DYyPnQoVP9PObRNI9OaHb3zoeZM4m8sQP13xd11lGKcK2lGZBdmwqBKoz2E7; _ga_87M7PJ3R97=GS2.1.s1755063208$o5$g1$t1755065914$j58$l0$h0; bm_sv=3EC17073B3B7A39FA5BE6F23C55F4856~YAAQhNcLF1d+y5+YAQAAk5MUohy0cXIr/8x0ZzgxuecgYfwIPj4rjnQMbuwDjg1VIUwsr8e87tLuO8L4GM1rrTsKZogAOVAoI0Z/49gGA4wiQldRQ3YzMa+1XCAZdjw8rURTsYTN28+WjKac+zYO8iAoGS3Y5RZjQOA9XBgDK3vlWSI3sL7Evgk+JzdaKNHdSQMGoEq/iom+fX/97PPjzDNwac/SFPZkvxi74SN2BLnUqZs3HjYdR8gLinpVFVAnAdxo~1; RT="z=1&dm=nseindia.com&si=694af66d-7f19-4a71-9338-8847e0932ec7&ss=me9kxh0m&sl=0&se=8c&tt=0&bcn=%2F%2F684d0d45.akstat.io%2F&ld=nxkn&nu=cvcpx2v&cl=7fz"; _abck=346A27E6C086CA11FDB53173602C8D94~-1~YAAQjdcLF5Y17p2YAQAAll0eog7/i3Wsrw7BgZZ1FGbQVUbNkgO2t1TkndsTVQxkDW5PduoSi4IXa1iTZXNS554AV3zB8MFv+A+h7NWRw3WmRUl5VLtqVz2xDnwAV9mXJbhJ0jRpQeUMt9SGn0C2BTtvQSilmhl8DuqS2IpFVc9TZBaKn7Wu5X2/7bf+8RfradR12to17yTLPKjYYEQ1tlTaiTm1UMAfGSSpmDnOMB4WCozx+cLH2xJLnLDZcOFZ8MIYcZODt9n6W2jvxQJh0i9U5LONPHyqLMafAQHSnXNrw+a81si+ZUFpUGxZ7pAXSvBTlN2XVkPGkZdaHNEWG/Lr8W6Gv+bxB2zstZ4HaY0+DkFToxK756yppJOXd41adMYFuVCyPQJBKfUhkHEBw2v9aaxdSFkuVKupQCHEnXoD5bsUpgh/K5pMbgYKz2ZJNnFZnlWOkcAK0KCiW4CgFvI+ZUOqQSJrwE03gL+sAZfFgYwNE/geH32ORDw2+3qJlvyS3UWy7IdlnEsEO4HLZdWC/AMd/n/f67l9WzOwILsAEsd4LReIctStmU/gFDK7GLAaWNTXhUK7UOPsSbHMLuxRoe6ZP5eSoYix7uLmh1SWYo4jQkDhk7K3gKSPEuoYrdh7bQE=~0~-1~-1; bm_sv=3EC17073B3B7A39FA5BE6F23C55F4856~YAAQjdcLF5c17p2YAQAAll0eohzR23PKG9dVlFi04VF01VWVr/x2ZDNl5k/xhMBDzh8DbiD1vpdy08EwepauPOv2qrMnG389KfZp+6fddRA4TrA7vTHHicCWtKIX3TN+tJ54i+eYndgySak3FjM2lCMh8rY3asuoyBEDvcONXPZbJHYw6hu/XyFE3T+U1pA1cjq7P4wxaLPKY1mNIdb36mxavMRTyZ24CEcqydya9JPEDVHPVpISARV1d1rHOhpXxVUk~1'
        }

    def get_indices_from_excel(self, filename="broad_market_indices.xlsx"):
        df = pd.read_excel(filename)
        # Get all values from column A, skipping the first row (header)
        indices_list = df.iloc[1:, 0].dropna().astype(str).tolist()
        return indices_list

    def fetch_data_for_indices(self, indices):
        url = self.url_template.format(indices=indices)
        response = requests.request("GET", url, headers=self.headers, data=self.payload)
        print(f"Requesting for Indices: {indices}")
        print("Status Code:", response.status_code)
        if response.status_code == 200:
            try:
                return response.json()
            except Exception as e:
                print("JSON decode error:", e)
                return None
        else:
            print("Failed to fetch data. Status code:", response.status_code)
            return None

    def loop_and_export(self, filename="broad_market_indices.xlsx", out_filename="nse_gainers_responses.xlsx"):
        indices_list = self.get_indices_from_excel(filename)
        all_data = []
        for idx in indices_list:
            data = self.fetch_data_for_indices(idx)
            if data and isinstance(data, list):
                # Add index info to each row for traceability
                for row in data:
                    row['Index'] = idx
                all_data.extend(data)
            time.sleep(2)  # polite delay
        if all_data:
            df = pd.DataFrame(all_data)
            df.to_excel(out_filename, index=False)
            print(f"Exported all responses to {out_filename}")
        else:
            print("No data to export.")

if __name__ == "__main__":
    exporter = NseGainersExporter()
    exporter.loop_and_export()





 