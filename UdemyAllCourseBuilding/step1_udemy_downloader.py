import os
import json
import time
import logging
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from helpers import safe_name, get_filename_from_url

class UdemyAssetDownloader:
    def __init__(self, base_folder, auth_file="Authentication.json", user_id_hint="256172910", sleep_between_calls=0.05, max_workers=16):
        self.base_folder = os.path.abspath(base_folder)
        self.auth_file = auth_file
        self.user_id_hint = user_id_hint
        self.sleep = sleep_between_calls
        self.max_workers = max_workers

        os.makedirs(self.base_folder, exist_ok=True)
        self.downloads_dir = os.path.join(self.base_folder, "downloads")
        os.makedirs(self.downloads_dir, exist_ok=True)

        self._load_auth()
        self._init_headers()
        self.session = self._init_session()

    def _load_auth(self):
        with open(self.auth_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.ACCESS_TOKEN = data.get("access_token")
        if not self.ACCESS_TOKEN:
            raise ValueError("Missing 'access_token' in Authentication.json")

    def _init_headers(self):
        self.auth_header = {"Authorization": f"Bearer {self.ACCESS_TOKEN}", "Accept": "application/json"}
        self.cookie_headers = {
            "accept": "application/json",
            "x-requested-with": "XMLHttpRequest",
            "x-udemy-cache-user": str(self.user_id_hint)
        }
        self.cookies = {"access_token": self.ACCESS_TOKEN}

    def _init_session(self):
        session = requests.Session()
        from requests.adapters import HTTPAdapter, Retry
        retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        return session

    def fetch_courses(self):
        url = "https://www.udemy.com/api-2.0/users/me/subscribed-courses?page_size=50"
        out = []
        while url:
            print(f"Fetching courses page {url}...")
            r = self.session.get(url, headers=self.auth_header, timeout=30)
            r.raise_for_status()
            data = r.json()
            for c in data.get("results", []):
                out.append({"id": c.get("id"), "title": c.get("title")})
            url = data.get("next")
            time.sleep(self.sleep)
        print(f"Total courses fetched: {len(out)}")
        return out

    def get_course_name(self, course_id):
        url = f"https://www.udemy.com/api-2.0/courses/{course_id}/?fields[course]=title"
        r = self.session.get(url, headers=self.cookie_headers, cookies=self.cookies, timeout=30)
        return r.json().get("title", f"Course {course_id}") if r.status_code == 200 else f"Course {course_id}"

    def fetch_curriculum_map(self, course_id):
        url = (
            f"https://www.udemy.com/api-2.0/courses/{course_id}/subscriber-curriculum-items/"
            f"?curriculum_types=chapter,lecture"
            f"&fields[lecture]=title,time_estimation,object_index,supplementary_assets"
            f"&fields[chapter]=title,object_index&page_size=200"
        )
        r = self.session.get(url, headers=self.cookie_headers, cookies=self.cookies, timeout=30)
        r.raise_for_status()
        section_map, lecture_map = {}, {}
        current_section_id, current_section_title, current_section_idx = None, None, 0
        for item in r.json().get("results", []):
            if item.get("_class") == "chapter":
                current_section_id = item.get("id")
                current_section_title = item.get("title")
                current_section_idx = item.get("object_index", 0)
                section_map[current_section_id] = {"title": current_section_title, "index": current_section_idx}
            elif item.get("_class") == "lecture":
                lecture_map[item["id"]] = {
                    "lecture_title": item.get("title"),
                    "section_id": current_section_id,
                    "section_title": current_section_title,
                    "section_index": current_section_idx,
                    "lecture_index": item.get("object_index", 0),
                    "time_estimation": item.get("time_estimation"),
                    "supplementary_assets": item.get("supplementary_assets", [])
                }
        return section_map, lecture_map

    def _resolve_asset_url(self, course_id, lecture_id, sup_asset_id):
        url = (
            f"https://www.udemy.com/api-2.0/users/me/subscribed-courses/{course_id}"
            f"/lectures/{lecture_id}/supplementary-assets/{sup_asset_id}/"
            f"?fields[asset]=download_urls,time_estimation"
        )
        try:
            rr = self.session.get(url, headers=self.cookie_headers, cookies=self.cookies, timeout=30)
            rr.raise_for_status()
            data = rr.json()
            if "download_urls" in data and "File" in data["download_urls"]:
                return data["download_urls"]["File"][0]["file"], data.get("time_estimation")
            elif "asset" in data and "download_urls" in data["asset"]:
                return data["asset"]["download_urls"]["File"][0]["file"], data["asset"].get("time_estimation")
        except Exception as e:
            print(f"Failed fetching asset URL: {e}")
        return None, None

    def _enumerate_supplementary_assets(self, course_id, course_name):
        print(f"Building asset list for course {course_name} ({course_id})...")
        _, lecture_map = self.fetch_curriculum_map(course_id)
        rows = []
        for lecture_id, lec in lecture_map.items():
            supp = lec.get("supplementary_assets") or []
            if not supp:
                rows.append({
                    "course_id": course_id,
                    "course_name": course_name,
                    "section_id": lec.get("section_id"),
                    "section_name": lec.get("section_title"),
                    "section_index": lec.get("section_index", 0),
                    "lecture_id": lecture_id,
                    "lecture_name": lec.get("lecture_title"),
                    "lecture_index": lec.get("lecture_index", 0),
                    "asset_id": None,
                    "asset_title": None,
                    "download_url": None,
                    "time_estimation": lec.get("time_estimation"),
                    "is_stub": True
                })
                continue

            for asset in supp:
                sup_id = asset.get("id")
                asset_title = asset.get("title") or f"asset_{sup_id}"
                url, time_est = self._resolve_asset_url(course_id, lecture_id, sup_id)
                time.sleep(self.sleep)
                rows.append({
                    "course_id": course_id,
                    "course_name": course_name,
                    "section_id": lec.get("section_id"),
                    "section_name": lec.get("section_title"),
                    "section_index": lec.get("section_index", 0),
                    "lecture_id": lecture_id,
                    "lecture_name": lec.get("lecture_title"),
                    "lecture_index": lec.get("lecture_index", 0),
                    "asset_id": sup_id,
                    "asset_title": asset_title,
                    "download_url": url,
                    "time_estimation": time_est or lec.get("time_estimation"),
                    "is_stub": False
                })
        rows.sort(key=lambda r: (r.get("section_index", 0), r.get("lecture_index", 0), safe_name((r.get("asset_title") or "") or "")))
        print(f"Planned {len(rows)} rows (including stubs) for {course_name}")
        return rows

    def _target_folder_for(self, course, section_idx, section, lecture_idx, lecture):
        folder_name = f"{section_idx:02d}_{safe_name(section or 'No Section')}"
        lecture_folder = f"{lecture_idx:02d}_{safe_name(lecture or 'Untitled')}"
        return os.path.join(self.downloads_dir, safe_name(course), folder_name, lecture_folder)

    def download_assets(self, course_name, assets: list):
        out = []

        def download_one(row):
            if row.get("is_stub"):
                row["local_path"] = None
                return row

            url = row.get("download_url")
            course, section, lecture = row.get("course_name"), row.get("section_name"), row.get("lecture_name")
            section_idx, lecture_idx = row.get("section_index", 0), row.get("lecture_index", 0)
            save_dir = self._target_folder_for(course, section_idx, section, lecture_idx, lecture)
            os.makedirs(save_dir, exist_ok=True)

            candidate = row.get("asset_title") or "asset"
            if url:
                candidate = get_filename_from_url(url, candidate)
            filename = safe_name(candidate)
            filepath = os.path.join(save_dir, filename)

            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                row["local_path"] = filepath
                row["already_downloaded"] = True
                print(f"Skipped download (exists): {filepath}")
                return row

            if not url:
                row["local_path"] = None
                row["download_error"] = row.get("download_error") or "No download URL"
                print(f"No download URL for asset: {row.get('asset_title')}")
                return row

            try:
                with self.session.get(url, stream=True, timeout=120) as resp:
                    resp.raise_for_status()
                    total_size = int(resp.headers.get('content-length', 0))
                    desc = f"{section} | {lecture} | {filename} ({total_size/1024:.1f} KB)"
                    with open(filepath, "wb") as f, tqdm(
                        total=total_size, unit='B', unit_scale=True, unit_divisor=1024, desc=desc, leave=False, position=1
                    ) as pbar:
                        for chunk in resp.iter_content(65536):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
                row["local_path"] = filepath
                row["already_downloaded"] = False
                print(f"Downloaded: {filepath} ({total_size/1024:.1f} KB)")
            except Exception as e:
                row["local_path"] = None
                row["download_error"] = str(e)[:200]
                print(f"Download failed for {filepath}: {e}")
            return row

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(download_one, a) for a in assets]
            for future in tqdm(as_completed(futures), total=len(futures), desc=f"Downloading assets for {course_name}", position=0):
                out.append(future.result())
        return out

if __name__ == "__main__":
    BASE = "./udemyDownloads"
    AUTH_FILE = "Authentication.json"
    downloader = UdemyAssetDownloader(base_folder=BASE, auth_file=AUTH_FILE)
    courses = downloader.fetch_courses()
    for course in courses:
        course_id = course["id"]
        course_name = course["title"]
        print(f"Processing course: {course_name} ({course_id})")
        assets = downloader._enumerate_supplementary_assets(course_id, course_name)
        results = downloader.download_assets(course_name, assets)
        print(f"Downloaded {sum(1 for r in results if r.get('local_path'))} assets for {course_name}")