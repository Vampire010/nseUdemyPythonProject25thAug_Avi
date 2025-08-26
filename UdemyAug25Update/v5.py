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
import concurrent.futures
from tqdm import tqdm
from tabulate import tabulate
from PyPDF2 import PdfReader

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

def is_texty(filename: str) -> bool:
    return not re.search(r"\.(png|jpg|jpeg|gif|bmp|exe|dll|pdf|mp4|avi|mkv|mov|pptx?|docx?|xlsx?)$", filename, re.I)

def is_pdf(filename: str) -> bool:
    return filename.lower().endswith('.pdf')

def is_zip(filename: str) -> bool:
    return filename.lower().endswith('.zip')

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

def _language_from_filename(filename: str) -> str:
    ext = os.path.splitext(filename.lower())[1]
    return {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".json": "json",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".xml": "xml",
        ".html": "html",
        ".css": "css",
        ".sh": "bash",
        ".ps1": "powershell",
        ".md": "markdown",
        ".txt": ""
    }.get(ext, "")

def extract_zip(zip_path, extract_to):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        return [os.path.join(extract_to, f) for f in zip_ref.namelist()]
    except Exception as e:
        logger.error(f"Failed to extract zip {zip_path}: {e}")
        return []

def preview_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        if reader.pages:
            text = reader.pages[0].extract_text()
            return text if text else "[No extractable text found in first page]"
        else:
            return "[No pages found in PDF]"
    except Exception as e:
        logger.error(f"Failed to preview PDF {pdf_path}: {e}")
        return f"[Error reading PDF: {e}]"

# =========================
# UdemyCourseNotebookBuilder class
# =========================
class UdemyCourseNotebookBuilder:
    def __init__(self, base_folder, auth_file="Authentication.json", user_id_hint="256172910",
                 sleep_between_calls=0.05, max_workers=16):
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
        self.session = self._init_session()

    # ---------- Auth ----------
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

    # ---------- Fetch courses ----------
    def fetch_courses(self):
        url = "https://www.udemy.com/api-2.0/users/me/subscribed-courses?page_size=50"
        out = []
        while url:
            logger.info(f"Fetching courses page {url}...")
            r = self.session.get(url, headers=self.auth_header, timeout=30)
            r.raise_for_status()
            data = r.json()
            for c in data.get("results", []):
                out.append({"id": c.get("id"), "title": c.get("title")})
            url = data.get("next")
            time.sleep(self.sleep)
        logger.info(f"Total courses fetched: {len(out)}")
        return out

    def get_course_name(self, course_id):
        url = f"https://www.udemy.com/api-2.0/courses/{course_id}/?fields[course]=title"
        r = self.session.get(url, headers=self.cookie_headers, cookies=self.cookies, timeout=30)
        return r.json().get("title", f"Course {course_id}") if r.status_code == 200 else f"Course {course_id}"

    # ---------- Fetch curriculum ----------
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

    # ---------- Resolve asset URLs ----------
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
            logger.debug(f"Failed fetching asset URL: {e}")
        return None, None

    # ---------- Plan assets to download (includes stub rows for lectures with no assets) ----------
    def _enumerate_supplementary_assets(self, course_id, course_name):
        logger.info(f"Building asset list for course {course_name} ({course_id})...")
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
        logger.info(f"Planned {len(rows)} rows (including stubs) for {course_name}")
        return rows

    # ---------- Download assets (threaded, nested progress bars) ----------
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

            # Skip if file exists and is non-empty
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                row["local_path"] = filepath
                row["already_downloaded"] = True
                logger.info(f"Skipped download (exists): {filepath}")
                return row

            if not url:
                row["local_path"] = None
                row["download_error"] = row.get("download_error") or "No download URL"
                logger.warning(f"No download URL for asset: {row.get('asset_title')}")
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
                logger.info(f"Downloaded: {filepath} ({total_size/1024:.1f} KB)")
            except Exception as e:
                row["local_path"] = None
                row["download_error"] = str(e)[:200]
                logger.error(f"Download failed for {filepath}: {e}")
            return row

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(download_one, a) for a in assets]
            for future in tqdm(as_completed(futures), total=len(futures), desc=f"Downloading assets for {course_name}", position=0):
                out.append(future.result())
        return out

    # ---------- Notebook helpers ----------
    def _notebook_path_for(self, course, section_idx, section, lecture_idx, lecture):
        section_folder = f"{section_idx:02d}_{safe_name(section or 'No Section')}"
        lecture_file = f"{lecture_idx:02d}_{safe_name(lecture or 'Untitled')}.ipynb"
        return os.path.join(self.notebooks_dir, safe_name(course), section_folder, lecture_file)

    def _build_lecture_notebook(self, course_name, section_idx, section_name, lecture_idx, lecture_name, rows):
        time_est = rows[0].get("time_estimation") if rows else None
        lecture_title = lecture_name or "Untitled"

        # Title cell (only lecture title, styled)
        title_html = f"<h2 style='color:#1565c0;font-family:sans-serif;'>{lecture_title}</h2>"
        cells = [new_markdown_cell(title_html)]

        # Duration cell (separate, styled)
        if time_est:
            duration_html = f"<b style='color:#1a237e;'>Duration:</b> <span style='font-size:14px;'>{time_est} min</span>"
            cells.append(new_markdown_cell(duration_html))

        # No assets case
        if not rows or all(r.get("is_stub") for r in rows):
            cells.append(new_markdown_cell("<span style='color:#333;'>No supplementary assets for this lecture.</span>"))
            return new_notebook(cells=cells)

        # Each asset info/preview in its own cell
        for r in rows:
            if r.get("is_stub"):
                continue
            filename = r.get("asset_title") or "asset"
            url = r.get("download_url")
            lp = r.get("local_path")

            # Asset link cell
            if url:
                asset_link_html = f"<b style='color:#1565c0;'>Asset:</b> <a href='{url}' style='color:#0d47a1;'>{filename}</a>"
            else:
                err = r.get("download_error") or "Unavailable"
                asset_link_html = f"<b style='color:#1565c0;'>Asset:</b> {filename} <span style='color:red;'>(error: {err})</span>"
            cells.append(new_markdown_cell(asset_link_html))

            # Preview cell (if applicable)
            if not lp or filename.lower().endswith(".exe"):
                continue

            # ZIP: extract and list readable files
            if is_zip(filename):
                extract_dir = lp + "_extracted"
                os.makedirs(extract_dir, exist_ok=True)
                extracted_files = extract_zip(lp, extract_dir)
                for ef in extracted_files:
                    ef_name = os.path.basename(ef)
                    if is_texty(ef_name) and os.path.getsize(ef) <= 512 * 1024:
                        try:
                            with open(ef, "r", encoding="utf-8", errors="replace") as f:
                                content = f.read()
                            preview_html = f"<b style='color:#1565c0;'>Preview: {ef_name}</b><pre style='background:#f5f5f5;color:#263238;'>{content[:2000]}</pre>"
                            cells.append(new_markdown_cell(preview_html))
                        except Exception as e:
                            error_html = f"<span style='color:red;'>Failed to preview {ef_name}: {e}</span>"
                            cells.append(new_markdown_cell(error_html))
                    else:
                        skip_html = f"<span style='color:#888;'>Preview not available for {ef_name} (binary or too large)</span>"
                        cells.append(new_markdown_cell(skip_html))
                continue

            # PDF: preview first page
            if is_pdf(filename):
                pdf_text = preview_pdf(lp)
                pdf_html = f"<b style='color:#1565c0;'>Preview of {filename} (first page):</b><pre style='background:#f5f5f5;color:#263238;'>{pdf_text[:2000]}</pre>"
                cells.append(new_markdown_cell(pdf_html))
                continue

            # Text/code preview
            try:
                if is_texty(filename) and os.path.getsize(lp) <= 512 * 1024:
                    with open(lp, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                    lang = _language_from_filename(filename)
                    preview_html = f"<b style='color:#1565c0;'>Preview: {filename}</b><pre style='background:#f5f5f5;color:#263238;'>{content[:2000]}</pre>"
                    cells.append(new_markdown_cell(preview_html))
                else:
                    skip_html = f"<span style='color:#888;'>Preview not available for {filename} (binary or too large)</span>"
                    cells.append(new_markdown_cell(skip_html))
            except Exception as e:
                error_html = f"<span style='color:red;'>Failed to preview {filename}: {e}</span>"
                cells.append(new_markdown_cell(error_html))

        return new_notebook(cells=cells)

    def build_notebooks_for_course(self, course_name: str, results: list) -> int:
        groups = {}
        for r in results:
            key = (
                r.get("section_index", 0),
                r.get("section_name"),
                r.get("lecture_index", 0),
                r.get("lecture_name"),
            )
            groups.setdefault(key, []).append(r)

        created = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_nb = {
                executor.submit(self._build_lecture_notebook, course_name, s_idx, s_name, l_idx, l_name, rows): (s_idx, s_name, l_idx, l_name, rows)
                for (s_idx, s_name, l_idx, l_name), rows in groups.items()
            }
            for future in tqdm(concurrent.futures.as_completed(future_to_nb), total=len(future_to_nb), desc=f"Building Notebooks for {course_name}", position=0):
                s_idx, s_name, l_idx, l_name, rows = future_to_nb[future]
                nb = future.result()
                nb_path = self._notebook_path_for(course_name, s_idx, s_name, l_idx, l_name)
                os.makedirs(os.path.dirname(nb_path), exist_ok=True)
                with open(nb_path, "w", encoding="utf-8") as f:
                    nbformat.write(nb, f)
                created += 1
                logger.info(f"Notebook created: {nb_path} [{course_name} | {s_name} | {l_name}]")
        return created

    # ---------- Orchestrator ----------
    def run_all_courses(self, course_ids=None):
        if course_ids:
            courses = [{"id": cid, "title": self.get_course_name(cid)} for cid in course_ids]
        else:
            courses = self.fetch_courses()

        summary = {
            "courses_processed": 0,
            "assets_attempted": 0,
            "assets_downloaded": 0,
            "notebooks_created": 0,
            "courses": []
        }

        all_course_results = []
        for c in tqdm(courses, desc="Courses", dynamic_ncols=True, position=0):
            course_id = c.get("id")
            course_name = c.get("title") or self.get_course_name(course_id)
            logger.info(f"Planning and downloading assets for course: {course_name} ({course_id})")
            try:
                planned_rows = self._enumerate_supplementary_assets(course_id, course_name)
                results = self.download_assets(course_name, planned_rows)
                all_course_results.append((course_name, results, course_id))
            except Exception as e:
                logger.exception(f"Failed processing course {course_name} ({course_id})")
                summary["courses"].append({
                    "course_id": course_id,
                    "course_name": course_name,
                    "assets_attempted": 0,
                    "assets_downloaded": 0,
                    "notebooks_created": 0,
                    "errors": [str(e)]
                })
                continue

        for course_name, results, course_id in all_course_results:
            try:
                notebooks_created = self.build_notebooks_for_course(course_name, results)
            except Exception as e:
                logger.exception(f"Failed building notebooks for course {course_name} ({course_id})")
                summary["courses"].append({
                    "course_id": course_id,
                    "course_name": course_name,
                    "assets_attempted": 0,
                    "assets_downloaded": 0,
                    "notebooks_created": 0,
                    "errors": [str(e)]
                })
                continue

            attempted = sum(1 for r in results if not r.get("is_stub"))
            downloaded = sum(1 for r in results if r.get("local_path"))
            errs = [
                {
                    "section": r.get("section_name"),
                    "lecture": r.get("lecture_name"),
                    "asset": r.get("asset_title"),
                    "error": r.get("download_error")
                }
                for r in results if (not r.get("is_stub")) and (not r.get("local_path"))
            ]

            summary["courses"].append({
                "course_id": course_id,
                "course_name": course_name,
                "assets_attempted": attempted,
                "assets_downloaded": downloaded,
                "notebooks_created": notebooks_created,
                "errors": errs[:25]
            })
            summary["courses_processed"] += 1
            summary["assets_attempted"] += attempted
            summary["assets_downloaded"] += downloaded
            summary["notebooks_created"] += notebooks_created

        # Print summary table
        print("\n=== Summary Table ===")
        table = []
        for c in summary["courses"]:
            table.append([
                c.get("course_name"),
                c.get("assets_attempted"),
                c.get("assets_downloaded"),
                c.get("notebooks_created"),
                len(c.get("errors", []))
            ])
        print(tabulate(table, headers=["Course", "Assets Attempted", "Assets Downloaded", "Notebooks", "Errors"], tablefmt="github"))

        return summary

if __name__ == "__main__":
    BASE = "./udemyDownloads"
    AUTH_FILE = "Authentication.json"

    builder = UdemyCourseNotebookBuilder(base_folder=BASE, auth_file=AUTH_FILE)

    summary = builder.run_all_courses()

    print("\n=== Summary JSON ===")
    print(json.dumps(summary, indent=2))