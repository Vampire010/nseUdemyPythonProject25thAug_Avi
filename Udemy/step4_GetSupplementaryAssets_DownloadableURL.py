import requests
import pandas as pd
import os
import json


class UdemySupplementaryDownloader:
    def __init__(self, base_folder, auth_file="Authentication.json"):
        self.base_folder = base_folder
        self.input_file = os.path.join(base_folder, "udemy_CourseOutlineTitles.xlsx")
        self.output_file = os.path.join(base_folder, "udemy_resources.xlsx")
        self.auth_file = auth_file
        self.access_token = self._load_auth_token()
        self.headers, self.cookies = self._set_headers()

    def _load_auth_token(self):
        """Load Udemy authentication token"""
        try:
            with open(self.auth_file, "r") as f:
                auth_data = json.load(f)
            token = auth_data.get("access_token")
            if not token:
                raise ValueError("Missing 'access_token' in Authentication.json")
            return token
        except Exception as e:
            raise Exception(f"Error loading authentication token: {e}")

    def _set_headers(self):
        """Prepare headers and cookies"""
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US",
            "x-requested-with": "XMLHttpRequest",
            "x-udemy-cache-brand": "INen_US",
            "x-udemy-cache-language": "en",
            "x-udemy-cache-logged-in": "1",
            "x-udemy-cache-marketplace-country": "IN",
            "x-udemy-cache-price-country": "IN",
            "x-udemy-cache-user": "256172910"
        }
        cookies = {"access_token": self.access_token}
        return headers, cookies

    def fetch_download_urls(self):
        """Fetch download URLs from Udemy API"""
        try:
            df_input = pd.read_excel(
                self.input_file,
                usecols="A:H",
                skiprows=0,
                names=[
                    "course_id", "course_name", "section_id", "section_name",
                    "lecture_id", "lecture_name", "supplementary_asset_id", "asset_title"
                ]
            )
        except Exception as e:
            raise Exception(f"Error reading input Excel: {e}")

        results = []

        for _, row in df_input.iterrows():
            try:
                course_id = int(row["course_id"])
                lecture_id = int(row["lecture_id"])
                supplementary_asset_id = int(row["supplementary_asset_id"])
            except Exception as e:
                results.append({
                    "course_name": row.get("course_name", "Unknown"),
                    "section_name": row.get("section_name", "Unknown"),
                    "lecture_name": row.get("lecture_name", "Unknown"),
                    "asset_title": row.get("asset_title", "Unknown"),
                    "download_url": "N/A",
                    "error_message": f"Invalid IDs: {e}"
                })
                continue

            url = (
                f"https://www.udemy.com/api-2.0/users/me/subscribed-courses/{course_id}/"
                f"lectures/{lecture_id}/supplementary-assets/{supplementary_asset_id}/"
                "?fields[asset]=download_urls"
            )

            try:
                response = requests.get(url, headers=self.headers, cookies=self.cookies)

                if response.status_code == 200:
                    try:
                        data = response.json()
                        file_url = None

                        # Try both possible response structures
                        if "download_urls" in data and "File" in data["download_urls"]:
                            file_url = data["download_urls"]["File"][0]["file"]
                        elif "asset" in data and "download_urls" in data["asset"]:
                            file_url = data["asset"]["download_urls"]["File"][0]["file"]

                        results.append({
                            "course_name": row["course_name"],
                            "section_name": row["section_name"],
                            "lecture_name": row["lecture_name"],
                            "asset_title": row["asset_title"],
                            "download_url": file_url if file_url else "N/A",
                            "error_message": "" if file_url else "No download URL found"
                        })

                        if file_url:
                            print(f"✅ Found URL for {row['course_name']} | {row['lecture_name']}")
                        else:
                            print(f"⚠️ No file URL for {row['course_name']} | {row['lecture_name']}")

                    except Exception as e:
                        results.append({
                            "course_name": row["course_name"],
                            "section_name": row["section_name"],
                            "lecture_name": row["lecture_name"],
                            "asset_title": row["asset_title"],
                            "download_url": "N/A",
                            "error_message": f"JSON parsing error: {e}"
                        })

                else:
                    results.append({
                        "course_name": row["course_name"],
                        "section_name": row["section_name"],
                        "lecture_name": row["lecture_name"],
                        "asset_title": row["asset_title"],
                        "download_url": "N/A",
                        "error_message": f"HTTP {response.status_code}"
                    })
                    print(f"❌ Failed {course_id}-{lecture_id}-{supplementary_asset_id}: {response.status_code}")

            except Exception as e:
                results.append({
                    "course_name": row.get("course_name", "Unknown"),
                    "section_name": row.get("section_name", "Unknown"),
                    "lecture_name": row.get("lecture_name", "Unknown"),
                    "asset_title": row.get("asset_title", "Unknown"),
                    "download_url": "N/A",
                    "error_message": f"Request error: {e}"
                })
                print(f"❌ Error fetching {course_id}-{lecture_id}-{supplementary_asset_id}: {e}")

        # === Export results ===
        if results:
            df_output = pd.DataFrame(results)
            df_output.to_excel(self.output_file, index=False)
            print(f"✅ Exported {len(results)} results to {self.output_file}")
        else:
            print("⚠️ No downloadable files found.")


# === Run Script ===
if __name__ == "__main__":
    base_folder = r"./udemyDownloads"
    downloader = UdemySupplementaryDownloader(base_folder)
    downloader.fetch_download_urls()
