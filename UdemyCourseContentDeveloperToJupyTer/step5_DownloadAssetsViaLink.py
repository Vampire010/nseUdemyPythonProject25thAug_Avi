import os
import requests
import pandas as pd
from urllib.parse import urlparse, parse_qs, unquote
import re
from tqdm import tqdm  # pip install tqdm

# === CONFIGURE BASE DOWNLOAD FOLDER ===
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")

def safe_name(name: str) -> str:
    """
    Make a string safe for Windows folder/file names
    """
    return re.sub(r'[<>:"/\\|?*]', "_", name).strip()

def get_filename_from_url(url: str, asset_title: str):
    """
    Extract filename from URL, otherwise fallback to asset_title
    """
    try:
        # Extract filename from response-content-disposition
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        if "response-content-disposition" in qs:
            disp = unquote(qs["response-content-disposition"][0])
            if "filename=" in disp:
                return disp.split("filename=")[-1].strip('"').replace("+", " ")
    except Exception:
        pass

    # fallback
    return asset_title


def download_file(row):
    course = safe_name(str(row["course_name"]).strip())
    section = safe_name(str(row["section_name"]).strip())
    lecture = safe_name(str(row["lecture_name"]).strip())
    asset_title = safe_name(str(row["asset_title"]).strip())
    url = str(row["download_url"]).strip()

    folder_path = os.path.join(BASE_DIR, course, section, lecture)
    os.makedirs(folder_path, exist_ok=True)

    filename = safe_name(get_filename_from_url(url, asset_title))
    filepath = os.path.join(folder_path, filename)

    print(f"⬇ Downloading: {filename} -> {filepath}")
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            total_size = int(response.headers.get("content-length", 0))
            with open(filepath, "wb") as f, tqdm(
                total=total_size, unit="B", unit_scale=True, desc=filename, ncols=80
            ) as bar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    bar.update(len(chunk))

        print(f"✅ Saved: {filepath}")
    except Exception as e:
        print(f"❌ Failed {filename}: {e}")


def main():
    excel_file = "./udemyDownloads/udemy_resources.xlsx"  # replace with your file path
    df = pd.read_excel(excel_file)

    for _, row in df.iterrows():
        download_file(row)


if __name__ == "__main__":
    main()

# "# Directory structure:
#     downloads/
#    └── course_name/
#          └── section_name/
#                └── lecture_name/
#                      └── asset_file (from URL) "
