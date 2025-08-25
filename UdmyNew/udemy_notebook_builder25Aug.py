import os
import re
import json
import time
import zipfile
import logging
import requests
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell
from urllib.parse import urlparse, parse_qs, unquote
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# =========================
# Logging setup
# =========================
logger = logging.getLogger("UdemyDownloader")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S"))
logger.addHandler(ch)

fh = logging.FileHandler("udemy_downloader.log", mode="w", encoding="utf-8")
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(fh)

# =========================
# Helpers
# =========================
def safe_name(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*\n\r\t]', "_", str(name)).strip()

def normalize_name(name: str) -> str:
    return re.sub(r'[\s_\-]+', '', str(name)).lower()

def get_filename_from_url(url: str, asset_title: str) -> str:
    try:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        if "response-content-disposition" in qs:
            disp = unquote(qs["response-content-disposition"][0])
            if "filename=" in disp:
                return disp.split("filename=")[-1].strip('"').replace("+", " ")
    except Exception:
        pass
    return asset_title

def is_texty(filename: str) -> bool:
    return not re.search(r"\.(png|jpg|jpeg|gif|bmp|exe|dll|pdf|mp4|avi|mkv|mov|pptx?|docx?|xlsx?)$", filename, re.I)

# =========================
# Main Class
# =========================
class UdemyCourseNotebookBuilder:
    def __init__(self, base_folder: str,
                 auth_file: str = "Authentication.json",
                 user_id_hint: str = "256172910",
                 sleep_between_calls: float = 0.1,
                 max_workers: int = 5):
        self.base_folder = os.path.abspath(base_folder)
        self.auth_file = auth_file
        self.user_id_hint = user_id_hint
        self.sleep = sleep_between_calls
        self.max_workers = max_workers

        os.makedirs(self.base_folder, exist_ok=True)
        self.downloads_dir = os.path.join(self.base_folder, "downloads")
        self.notebooks_dir = os.path.join(self.base_folder, "notebooks")
        os.makedirs(self.downloads_dir, exist_ok=True)
        os.makedirs(self.notebooks_dir, exist_ok=True)

        self._load_auth()
        self._init_headers()

    # ---------- Auth / Headers ----------
    def _load_auth(self):
        with open(self.auth_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.ACCESS_TOKEN = data.get("access_token")
        self.CLIENT_ID = data.get("client_id")
        self.CSRF = data.get("csrf")
        if not self.ACCESS_TOKEN:
            raise ValueError("Missing 'access_token' in Authentication.json")

    def _init_headers(self):
        self.auth_header = {
            "Authorization": f"Bearer {self.ACCESS_TOKEN}",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
        }
        self.cookie_headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US",
            "x-requested-with": "XMLHttpRequest",
            "x-udemy-cache-brand": "INen_US",
            "x-udemy-cache-language": "en",
            "x-udemy-cache-logged-in": "1",
            "x-udemy-cache-marketplace-country": "IN",
            "x-udemy-cache-price-country": "IN",
            "x-udemy-cache-user": str(self.user_id_hint),
        }
        self.cookies = {"access_token": self.ACCESS_TOKEN}

    # ---------- API calls ----------
    def fetch_courses(self):
        url = "https://www.udemy.com/api-2.0/users/me/subscribed-courses?page_size=50"
        page = 1
        out = []
        while url:
            logger.info(f"Fetching courses page {page}...")
            resp = requests.get(url, headers=self.auth_header)
            resp.raise_for_status()
            data = resp.json()
            for c in data.get("results", []):
                out.append({
                    "id": c.get("id"),
                    "title": c.get("title"),
                    "completion_ratio": c.get("completion_ratio", 0),
                    "last_accessed_time": c.get("last_accessed_time"),
                })
            url = data.get("next")
            page += 1
            time.sleep(self.sleep)
        logger.info(f"Total courses fetched: {len(out)}")
        return out

    def get_course_name(self, course_id: int) -> str:
        url = f"https://www.udemy.com/api-2.0/courses/{course_id}/?fields[course]=id,title"
        r = requests.get(url, headers=self.cookie_headers, cookies=self.cookies)
        if r.status_code == 200:
            return r.json().get("title", f"Course {course_id}")
        return f"Course {course_id}"

    def fetch_curriculum_map(self, course_id: int):
        url = f"https://www.udemy.com/api-2.0/courses/{course_id}/public-curriculum-items/?page_size=1000"
        r = requests.get(url, headers=self.cookie_headers, cookies=self.cookies)
        section_map, lecture_map = {}, {}
        if r.status_code == 200:
            current_section_id, current_section_title = None, None
            for item in r.json().get("results", []):
                if item.get("_class") == "chapter":
                    current_section_id = item.get("id")
                    current_section_title = item.get("title")
                    section_map[current_section_id] = current_section_title
                elif item.get("_class") == "lecture":
                    lecture_map[item["id"]] = {
                        "lecture_title": item.get("title"),
                        "section_id": current_section_id,
                        "section_title": current_section_title,
                    }
        return section_map, lecture_map

    def fetch_assets_for_course(self, course_id: int):
        logger.info(f"Fetching assets for course {course_id}...")
        course_name = self.get_course_name(course_id)
        _, lecture_map = self.fetch_curriculum_map(course_id)

        base_lectures_url = (
            f"https://www.udemy.com/api-2.0/users/me/subscribed-courses/{course_id}/lectures/"
            "?page_size=1000&fields[lecture]=id,title,asset,supplementary_assets"
        )
        r = requests.get(base_lectures_url, headers=self.cookie_headers, cookies=self.cookies)
        r.raise_for_status()
        results = []

        def fetch_asset_url(lecture_id, sup_asset_id):
            url = (
                f"https://www.udemy.com/api-2.0/users/me/subscribed-courses/{course_id}/"
                f"lectures/{lecture_id}/supplementary-assets/{sup_asset_id}/"
                "?fields[asset]=download_urls"
            )
            try:
                rr = requests.get(url, headers=self.cookie_headers, cookies=self.cookies)
                rr.raise_for_status()
                data = rr.json()
                if "download_urls" in data and "File" in data["download_urls"]:
                    return data["download_urls"]["File"][0]["file"]
                elif "asset" in data and "download_urls" in data["asset"]:
                    return data["asset"]["download_urls"]["File"][0]["file"]
            except Exception as e:
                logger.debug(f"Failed fetching asset URL: {e}")
            return None

        future_to_asset = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for lecture in r.json().get("results", []):
                lecture_id = lecture.get("id")
                lecture_info = lecture_map.get(lecture_id, {})
                for asset in (lecture.get("supplementary_assets") or []):
                    if asset.get("asset_type") != "File":
                        continue
                    sup_asset_id = asset.get("id")
                    asset_title = asset.get("title")
                    future = executor.submit(fetch_asset_url, lecture_id, sup_asset_id)
                    future_to_asset[future] = (lecture_id, lecture_info, sup_asset_id, asset_title)

            for future in tqdm(as_completed(future_to_asset), total=len(future_to_asset), desc="Resolving asset URLs"):
                lecture_id, lecture_info, sup_asset_id, asset_title = future_to_asset[future]
                file_url = future.result()
                results.append({
                    "course_id": course_id,
                    "course_name": course_name,
                    "section_name": lecture_info.get("section_title", ""),
                    "lecture_name": lecture_info.get("lecture_title", ""),
                    "lecture_id": lecture_id,
                    "supplementary_asset_id": sup_asset_id,
                    "asset_title": asset_title,
                    "download_url": file_url,
                })

        logger.info(f"Assets fetched for course {course_id}: {len(results)}")
        return results

    # ---------- Downloading ----------
    def _target_folder_for(self, course: str, section: str, lecture: str):
        return os.path.join(self.downloads_dir, safe_name(course), safe_name(section or "No Section"), safe_name(lecture or "Untitled"))

    def download_assets(self, assets: list):
        logger.info("Starting asset downloads...")

        def download_one(row):
            url = row.get("download_url")
            course = row.get("course_name") or f"Course {row.get('course_id')}"
            section = row.get("section_name") or "Section"
            lecture = row.get("lecture_name") or "Lecture"
            asset_title = row.get("asset_title") or "asset"

            save_dir = self._target_folder_for(course, section, lecture)
            os.makedirs(save_dir, exist_ok=True)

            if not url:
                row["local_path"] = None
                return row

            filename = safe_name(get_filename_from_url(url, asset_title))
            filepath = os.path.join(save_dir, filename)
            try:
                with requests.get(url, stream=True) as resp:
                    resp.raise_for_status()
                    with open(filepath, "wb") as f:
                        for chunk in resp.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                row["local_path"] = filepath
            except Exception as e:
                row["local_path"] = None
                row["download_error"] = str(e)[:200]
            return row

        downloaded = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(download_one, a) for a in assets]
            for future in tqdm(as_completed(futures), total=len(futures), desc="Downloading assets"):
                downloaded.append(future.result())

        logger.info(f"Downloads completed: {sum(1 for r in downloaded if r.get('local_path'))}/{len(assets)}")
        return downloaded

    # ---------- Notebook generation ----------
    def _build_notebook_for_lecture(self, course: str, section: str, lecture: str, lecture_assets: list):
        course_safe = safe_name(course)
        section_safe = safe_name(section or "No Section")
        lecture_safe = safe_name(lecture or "Untitled")

        folder = os.path.join(self.notebooks_dir, course_safe, section_safe)
        os.makedirs(folder, exist_ok=True)
        nb_path = os.path.join(folder, f"{lecture_safe}.ipynb")

        cells = [new_markdown_cell(f"# {lecture}\n\n**Course:** {course}\n\n**Section:** {section or '—'}")]

        if lecture_assets:
            cells.append(new_markdown_cell("## Assets"))
            lines = []
            for a in lecture_assets:
                title = a.get("asset_title") or "asset"
                url = a.get("download_url") or ""
                lines.append(f"- [{title}]({url})" if url else f"- {title} (no URL)")
            cells.append(new_markdown_cell("\n".join(lines)))

            preview_cells = self._make_inline_previews(lecture_assets)
            if preview_cells:
                cells.append(new_markdown_cell("## Inline Previews"))
                cells.extend(preview_cells)

        nb = new_notebook()
        nb.cells = cells
        try:
            with open(nb_path, "w", encoding="utf-8") as f:
                nbformat.write(nb, f)
            logger.info(f"Notebook created: {nb_path}")
        except Exception as e:
            logger.error(f"Failed to write notebook {nb_path}: {e}")
        return nb_path

    def _make_inline_previews(self, lecture_assets: list):
        new_cells = []
        MAX_BYTES = 200 * 1024
        for a in lecture_assets:
            local_path = a.get("local_path")
            if not local_path or not os.path.exists(local_path):
                continue
            try:
                if local_path.lower().endswith(".zip"):
                    with zipfile.ZipFile(local_path, "r") as zf:
                        for member in zf.namelist():
                            if member.endswith("/") or not is_texty(member):
                                continue
                            try:
                                info = zf.getinfo(member)
                                if info.file_size > MAX_BYTES:
                                    continue
                                content = zf.read(member).decode("utf-8", errors="ignore")
                                rel = os.path.basename(local_path) + "/" + member
                                new_cells.append(new_markdown_cell(f"### 📦 {a.get('asset_title')}: `{rel}`\n```text\n{content}\n```"))
                            except Exception:
                                pass
                elif is_texty(local_path) and os.path.getsize(local_path) <= MAX_BYTES:
                    with open(local_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    rel = os.path.basename(local_path)
                    new_cells.append(new_markdown_cell(f"### 📄 {a.get('asset_title')} — `{rel}`\n```text\n{content}\n```"))
            except Exception:
                continue
        return new_cells

    def build_notebooks(self, assets_downloaded: list):
        logger.info("Starting notebook generation...")
        lectures = {}
        for row in assets_downloaded:
            course = row.get("course_name") or f"Course {row.get('course_id')}"
            section = row.get("section_name") or "Section"
            lecture = row.get("lecture_name") or "Lecture"
            key = (course, section, lecture)
            lectures.setdefault(key, []).append(row)

        created = []

        def build_one(key_assets):
            (course, section, lecture), lecture_assets = key_assets
            return self._build_notebook_for_lecture(course, section, lecture, lecture_assets)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(build_one, k): k for k in lectures.items()}
            for future in tqdm(as_completed(futures), total=len(futures), desc="Creating notebooks"):
                created.append(future.result())

        logger.info(f"Notebooks created: {len(created)}")
        return created

    # ---------- Full pipeline ----------
    def run_all_courses(self, course_filter_ids=None):
        if course_filter_ids:
            courses = [{"id": int(cid), "title": self.get_course_name(int(cid))} for cid in course_filter_ids]
        else:
            courses = self.fetch_courses()

        all_assets = []
        for c in courses:
            cid = int(c["id"])
            logger.info(f"📘 Processing course: {c['title']} ({cid})")
            assets = self.fetch_assets_for_course(cid)
            all_assets.extend(assets)

        downloaded = self.download_assets(all_assets)
        notebooks = self.build_notebooks(downloaded)

        return {
            "courses_processed": [c["id"] for c in courses],
            "assets_count": len(all_assets),
            "files_downloaded": sum(1 for r in downloaded if r.get("local_path")),
            "notebooks_created": notebooks,
        }

# =========================
# Main runner
# =========================
if __name__ == "__main__":
    BASE = "./udemyDownloads"   # output folder
    builder = UdemyCourseNotebookBuilder(base_folder=BASE, auth_file="Authentication.json")

    # Option 1: run all subscribed courses
    summary = builder.run_all_courses()

    # Option 2: run only specific course IDs
    # summary = builder.run_all_courses(course_filter_ids=[397068, 123456])

    print("\n=== Summary ===")
    print(json.dumps(summary, indent=2))
