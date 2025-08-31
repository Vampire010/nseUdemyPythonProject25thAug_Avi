import requests
import json
import pandas as pd
import logging
from tqdm import tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load authentication
auth_path = r"Authentication.json"
with open(auth_path, "r") as f:
    auth = json.load(f)

client_id = auth.get("client_id")
access_token = auth.get("access_token")
csrf_token = auth.get("csrf")

headers = {
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

cookies = {
    "client_id": client_id,
    "access_token": access_token,
    "csrftoken": csrf_token,
    "ud_cache_user": "161182582",
    "ud_cache_logged_in": "1",
    "ud_cache_language": "en",
    "ud_cache_brand": "INen_US",
    "ud_cache_marketplace_country": "IN",
    "ud_cache_price_country": "IN",
    "ud_cache_release": "7250e930798675e5f2ea",
    "ud_cache_version": "1"
}

# Read the Excel file
excel_path = r"./udemyDownloads/udemySubscriberCurriculumItems.xlsx"
df = pd.read_excel(excel_path)

results = []

logging.info(f"Processing {len(df)} items...")

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
    session.headers.update(headers)
    session.cookies.update(cookies)

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
            logging.info(f"Fetched caption for item_id {item_id}: {caption_url}")
        else:
            logging.warning(f"Failed to fetch for item_id {item_id}: Status {response.status_code}")
    except Exception as e:
        logging.error(f"Error for item_id {item_id}: {e}")
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

output_path = r"./udemyDownloads/udemyCaptionsWithUrl.xlsx"
result_df = pd.DataFrame(results)
result_df.to_excel(output_path, index=False)
logging.info(f"Saved results to {output_path}")