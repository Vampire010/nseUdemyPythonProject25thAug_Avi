import os
import re
import json
import time
import zipfile
import requests
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell
from urllib.parse import urlparse, parse_qs, unquote

# =========================
# Helpers
# =========================

def safe_name(name: str) -> str:
    """Make a string safe for Windows/Linux file/folder names."""
    return re.sub(r'[<>:"/\\|?*\n\r\t]', "_", str(name)).strip()

def normalize_name(name: str) -> str:
    """Normalize names for matching (ignore case, spaces, underscores, dashes)."""
    return re.sub(r'[\s_\-]+', '', str(name)).lower()

def get_filename_from_url(url: str, asset_title: str) -> str:
    """
    Try to derive a filename from the URL; fall back to the asset title.
    Mirrors logic in your step5 downloader.
    """
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
    """
    Heuristic for text-like files we might inline into notebooks.
    (We skip binaries like images/video/pdf/office formats.)
    """
    return not re.search(r"\.(png|jpg|jpeg|gif|bmp|exe|dll|pdf|mp4|avi|mkv|mov|pptx?|docx?|xlsx?)$", filename, re.I)


# =========================
# Unified Orchestrator
# =========================

class UdemyCourseNotebookBuilder:
    """
    One class to:
      1) Read auth
      2) Fetch courses
      3) Fetch course outline (sections/lectures)
      4) Fetch supplementary File assets + download URLs
      5) Download assets into downloads/Course/Section/Lecture
      6) Build one Jupyter notebook per lecture with Course→Section→Lecture + assets (links + inline text previews)
    """

    def __init__(self, base_folder: str,
                 auth_file: str = "Authentication.json",
                 user_id_hint: str = "256172910",
                 sleep_between_calls: float = 0.3):
        """
        base_folder: root working folder; we'll create:
            - downloads/ (assets saved here by Course/Section/Lecture)
            - notebooks/ (one .ipynb per lecture)
        auth_file: file containing at least {"access_token": "..."} (optionally client_id, csrf)
        user_id_hint: used only for certain Udemy cache headers; not strictly required for auth
        """
        self.base_folder = os.path.abspath(base_folder)
        self.auth_file = auth_file
        self.user_id_hint = user_id_hint
        self.sleep = sleep_between_calls

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
        self.CLIENT_ID = data.get("client_id")  # optional
        self.CSRF = data.get("csrf")            # optional
        if not self.ACCESS_TOKEN:
            raise ValueError("Missing 'access_token' in Authentication.json")

    def _init_headers(self):
        # Two forms are used across your scripts:
        # 1) Authorization: Bearer (works for 'me/subscribed-courses')
        # 2) Cookies + X-Requested-With etc. (works for fetch of lecture assets/download URLs)
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
        # cookies via header or requests' cookies parameter
        self.cookies = {"access_token": self.ACCESS_TOKEN}
        # For a few endpoints you used "Cookie" header joined; requests handles cookies param cleanly.

    # ---------- API calls ----------

    def fetch_courses(self):
        """
        Return a list of {id, title, completion_ratio, last_accessed_time}
        """
        url = "https://www.udemy.com/api-2.0/users/me/subscribed-courses?page_size=50"
        page = 1
        out = []
        while url:
            resp = requests.get(url, headers=self.auth_header)
            if resp.status_code != 200:
                raise RuntimeError(f"Failed to fetch courses (HTTP {resp.status_code}): {resp.text[:200]}")
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
        return out

    def get_course_name(self, course_id: int) -> str:
        url = f"https://www.udemy.com/api-2.0/courses/{course_id}/?fields[course]=id,title"
        r = requests.get(url, headers=self.cookie_headers, cookies=self.cookies)
        if r.status_code == 200:
            return r.json().get("title", f"Course {course_id}")
        return f"Course {course_id}"

    def fetch_curriculum_map(self, course_id: int):
        """
        Returns:
          section_map: {section_id -> section_title}
          lecture_map: {lecture_id -> {"lecture_title", "section_id", "section_title"}}
        Uses the 'public-curriculum-items' endpoint like your step3 script.
        """
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
        """
        For a course, fetch all lectures (me/subscribed-courses/.../lectures)
        and collect supplementary assets of type 'File'.
        Then, for each, resolve the actual download URL.
        Returns a list of dicts with:
          course_id, course_name, section_name, lecture_name, asset_title, download_url
        """
        course_name = self.get_course_name(course_id)
        _, lecture_map = self.fetch_curriculum_map(course_id)

        base_lectures_url = (
            f"https://www.udemy.com/api-2.0/users/me/subscribed-courses/{course_id}/lectures/"
            "?page_size=1000&fields[lecture]=id,title,asset,supplementary_assets"
        )
        r = requests.get(base_lectures_url, headers=self.cookie_headers, cookies=self.cookies)
        if r.status_code != 200:
            raise RuntimeError(f"Failed to fetch lectures for {course_id} (HTTP {r.status_code})")

        results = []
        for lecture in r.json().get("results", []):
            lecture_id = lecture.get("id")
            lecture_info = lecture_map.get(lecture_id, {})
            for asset in (lecture.get("supplementary_assets") or []):
                if asset.get("asset_type") != "File":
                    continue
                sup_asset_id = asset.get("id")
                asset_title = asset.get("title")
                # Resolve a downloadable URL
                url = (
                    f"https://www.udemy.com/api-2.0/users/me/subscribed-courses/{course_id}/"
                    f"lectures/{lecture_id}/supplementary-assets/{sup_asset_id}/"
                    "?fields[asset]=download_urls"
                )
                rr = requests.get(url, headers=self.cookie_headers, cookies=self.cookies)
                file_url = None
                if rr.status_code == 200:
                    try:
                        data = rr.json()
                        if "download_urls" in data and "File" in data["download_urls"]:
                            file_url = data["download_urls"]["File"][0]["file"]
                        elif "asset" in data and "download_urls" in data["asset"]:
                            file_url = data["asset"]["download_urls"]["File"][0]["file"]
                    except Exception:
                        file_url = None
                results.append({
                    "course_id": course_id,
                    "course_name": course_name,
                    "section_name": lecture_info.get("section_title", ""),
                    "lecture_name": lecture_info.get("lecture_title", lecture.get("title")),
                    "lecture_id": lecture_id,
                    "supplementary_asset_id": sup_asset_id,
                    "asset_title": asset_title,
                    "download_url": file_url,
                })
                time.sleep(self.sleep)
        return results

    # ---------- Downloading ----------

    def _target_folder_for(self, course: str, section: str, lecture: str):
        return os.path.join(self.downloads_dir, safe_name(course), safe_name(section or "No Section"), safe_name(lecture or "Untitled"))

    def download_assets(self, assets: list):
        """
        Download each asset that has a download_url into downloads/Course/Section/Lecture/<filename>
        Returns list of dicts with an added 'local_path' where saved (or None if skipped/failure).
        """
        out = []
        for row in assets:
            url = row.get("download_url")
            course = row.get("course_name") or f"Course {row.get('course_id')}"
            section = row.get("section_name") or "Section"
            lecture = row.get("lecture_name") or "Lecture"
            asset_title = row.get("asset_title") or "asset"

            save_dir = self._target_folder_for(course, section, lecture)
            os.makedirs(save_dir, exist_ok=True)

            if not url or url == "N/A":
                row["local_path"] = None
                out.append(row)
                continue

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
            out.append(row)
            time.sleep(self.sleep)
        return out

    # ---------- Notebook generation ----------

    def _build_notebook_for_lecture(self, course: str, section: str, lecture: str, lecture_assets: list):
        """
        Create one notebook for a lecture. Add:
          - H1 with lecture
          - Course/Section meta
          - Assets section with links
          - Inline previews for small text files and text files inside zips
        """
        course_safe = safe_name(course)
        section_safe = safe_name(section or "No Section")
        lecture_safe = safe_name(lecture or "Untitled")

        # Where to place the notebook
        folder = os.path.join(self.notebooks_dir, course_safe, section_safe)
        os.makedirs(folder, exist_ok=True)
        nb_path = os.path.join(folder, f"{lecture_safe}.ipynb")

        cells = []
        cells.append(new_markdown_cell(f"# {lecture}\n\n**Course:** {course}\n\n**Section:** {section or '—'}"))

        if lecture_assets:
            cells.append(new_markdown_cell("## Assets"))
            # links list
            lines = []
            for a in lecture_assets:
                title = a.get("asset_title") or "asset"
                url = a.get("download_url") or ""
                local_path = a.get("local_path")
                if url:
                    lines.append(f"- [{title}]({url})")
                else:
                    lines.append(f"- {title} (no URL)")
            cells.append(new_markdown_cell("\n".join(lines)))

            # Inline previews
            preview_cells = self._make_inline_previews(lecture_assets)
            if preview_cells:
                cells.append(new_markdown_cell("## Inline Previews"))
                cells.extend(preview_cells)

        nb = new_notebook()
        nb.cells = cells
        with open(nb_path, "w", encoding="utf-8") as f:
            nbformat.write(nb, f)
        return nb_path

    def _make_inline_previews(self, lecture_assets: list):
        """
        Try to inline small text files (<= 200 KB) or text files inside zip assets.
        """
        new_cells = []
        MAX_BYTES = 200 * 1024

        for a in lecture_assets:
            local_path = a.get("local_path")
            if not local_path or not os.path.exists(local_path):
                continue

            try:
                # ZIP handling
                if local_path.lower().endswith(".zip"):
                    with zipfile.ZipFile(local_path, "r") as zf:
                        for member in zf.namelist():
                            # skip directories and obvious binaries
                            if member.endswith("/") or not is_texty(member):
                                continue
                            try:
                                info = zf.getinfo(member)
                                if info.file_size > MAX_BYTES:
                                    continue
                                content = zf.read(member).decode("utf-8", errors="ignore")
                                rel = os.path.basename(local_path) + "/" + member
                                new_cells.append(new_markdown_cell(
                                    f"### 📦 {a.get('asset_title')}: `{rel}`\n"
                                    f"```text\n{content}\n```"
                                ))
                            except Exception:
                                # ignore unreadables inside the zip
                                pass

                # Plain text-like file
                elif is_texty(local_path) and os.path.getsize(local_path) <= MAX_BYTES:
                    with open(local_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    rel = os.path.basename(local_path)
                    new_cells.append(new_markdown_cell(
                        f"### 📄 {a.get('asset_title')} — `{rel}`\n"
                        f"```text\n{content}\n```"
                    ))
            except Exception:
                # skip on any error; keep notebook generation robust
                continue

        return new_cells

    def build_notebooks(self, assets_downloaded: list):
        """
        Build notebooks per lecture using the downloaded assets list.
        """
        # Group by (course, section, lecture)
        lectures = {}
        for row in assets_downloaded:
            course = row.get("course_name") or f"Course {row.get('course_id')}"
            section = row.get("section_name") or "Section"
            lecture = row.get("lecture_name") or "Lecture"
            key = (course, section, lecture)
            lectures.setdefault(key, []).append(row)

        created = []
        for (course, section, lecture), lecture_assets in lectures.items():
            nb_path = self._build_notebook_for_lecture(course, section, lecture, lecture_assets)
            created.append(nb_path)
        return created

    # ---------- Public runners ----------

    def run_all_courses(self, course_filter_ids=None):
        """
        Orchestrate the full pipeline for either:
          - all subscribed courses, or
          - the provided subset of course IDs.
        Returns: {
            "courses_processed": [...],
            "assets_count": int,
            "files_downloaded": int,
            "notebooks_created": [...]
        }
        """
        if course_filter_ids:
            courses = [{"id": int(cid), "title": self.get_course_name(int(cid))} for cid in course_filter_ids]
        else:
            courses = self.fetch_courses()

        all_assets = []
        for c in courses:
            cid = int(c["id"])
            print(f"📘 Processing course: {c['title']} ({cid})")
            assets = self.fetch_assets_for_course(cid)
            all_assets.extend(assets)

        # Download
        downloaded = self.download_assets(all_assets)

        # Build notebooks
        notebooks = self.build_notebooks(downloaded)

        return {
            "courses_processed": [c["id"] for c in courses],
            "assets_count": len(all_assets),
            "files_downloaded": sum(1 for r in downloaded if r.get("local_path")),
            "notebooks_created": notebooks,
        }


# =========================
# Example usage
# =========================
if __name__ == "__main__":
    """
    Run the entire pipeline. Adjust base_folder to your workspace.
    Make sure Authentication.json is alongside this script (or pass a full path).
    """
    BASE = "./udemyDownloads"   # will create BASE/downloads and BASE/notebooks
    builder = UdemyCourseNotebookBuilder(base_folder=BASE, auth_file="Authentication.json")

    # Option A: process all subscribed courses
    summary = builder.run_all_courses()

    # Option B: only specific course IDs
    # summary = builder.run_all_courses(course_filter_ids=[397068, 123456])

    print("\n=== Summary ===")
    print(json.dumps(summary, indent=2))
