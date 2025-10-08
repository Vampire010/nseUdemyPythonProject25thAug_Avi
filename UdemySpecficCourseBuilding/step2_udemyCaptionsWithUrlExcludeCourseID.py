import requests
import json
import pandas as pd
import logging
from tqdm import tqdm

class UdemyCaptionFetcher:
    def __init__(self, auth_path="Authentication.json", excel_path="./udemyDownloads/udemySubscriberCurriculumItems.xlsx"):
        self.auth_path = auth_path
        self.excel_path = excel_path
        self._setup_logging()
        self._load_auth()
        self._setup_headers_and_cookies()

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

    def _load_auth(self):
        with open(self.auth_path, "r") as f:
            auth = json.load(f)
        self.client_id = auth.get("client_id")
        self.access_token = auth.get("access_token")
        self.csrf_token = auth.get("csrf")

    def _setup_headers_and_cookies(self):
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-IN",
            "x-requested-with": "XMLHttpRequest",
            "x-udemy-cache-user": "161182582",
            "x-udemy-cache-logged-in": "1",
            "x-udemy-cache-language": "en",
            "x-udemy-cache-brand": "INen_US",
            "x-udemy-cache-marketplace-country": "IN",
            "x-udemy-cache-price-country": "IN",
            "x-udemy-cache-release": "7250e930798675e5f2ea",
            "x-udemy-cache-version": "1"
        }
        self.cookies = {
            "client_id": self.client_id,
            "access_token": self.access_token,
            "csrftoken": self.csrf_token,
            "ud_cache_user": "161182582",
            "ud_cache_logged_in": "1",
            "ud_cache_language": "en",
            "ud_cache_brand": "INen_US",
            "ud_cache_marketplace_country": "IN",
            "ud_cache_price_country": "IN",
            "ud_cache_release": "7250e930798675e5f2ea",
            "ud_cache_version": "1"
        }

    def fetch_captions_for_courses(self, course_ids, output_path="./udemyDownloads/udemyCaptionsWithUrl.xlsx"):
        df = pd.read_excel(self.excel_path)
        df = df[df["course_id"].isin(course_ids)]
        results = []

        self.logger.info(f"Processing {len(df)} items...")

        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Fetching captions"):
            course_id = row.get("course_id")
            course_name = row.get("course_name")
            chapter_id = row.get("chapter_id")
            chapter_title = row.get("chapter_title")
            item__class = row.get("item__class")
            item_id = row.get("lecture_id")
            item_title = row.get("lecture_title")

            url = f"https://www.udemy.com/api-2.0/users/me/subscribed-courses/{course_id}/lectures/{item_id}/"
            params = {
                "fields[lecture]": "asset,description,download_url,is_free,last_watched_second",
                "fields[asset]": "asset_type,length,media_license_token,course_is_drmed,media_sources,captions,thumbnail_sprite,slides,slide_urls,download_urls,external_url"
            }

            session = requests.Session()
            session.headers.update(self.headers)
            session.cookies.update(self.cookies)

            try:
                response = session.get(url, params=params)
                caption_url = None
                if response.status_code == 200:
                    data = response.json()
                    asset = data.get("asset", {})
                    captions = asset.get("captions", [])
                    for caption in captions:
                        if caption.get("locale_id") == "en_US" and "url" in caption:
                            caption_url = caption["url"]
                            break
                    self.logger.info(f"Fetched caption for item_id {item_id}: {caption_url}")
                else:
                    self.logger.warning(f"Failed to fetch for item_id {item_id}: Status {response.status_code}")
            except Exception as e:
                self.logger.error(f"Error for item_id {item_id}: {e}")
                caption_url = None

            results.append({
                "course_id": course_id,
                "course_name": course_name,
                "chapter_id": chapter_id,
                "chapter_title": chapter_title,
                "item__class": item__class,
                "lecture_id": item_id,
                "lecture_title": item_title,
                "caption_url": caption_url
            })

        result_df = pd.DataFrame(results)
        result_df.to_excel(output_path, index=False)
        self.logger.info(f"Saved results to {output_path}")

if __name__ == "__main__":
    # Example usage
    COURSE_IDS_TO_PROCESS = [2942646]  # <-- Replace with your actual course IDs
    fetcher = UdemyCaptionFetcher()
    fetcher.fetch_captions_for_courses(COURSE_IDS_TO_PROCESS)