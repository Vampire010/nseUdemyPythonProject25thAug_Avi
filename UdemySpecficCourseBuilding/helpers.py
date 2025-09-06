import re
import os
import zipfile
import logging
from PyPDF2 import PdfReader

def safe_name(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*\n\r\t]', "_", str(name)).strip()

def is_texty(filename: str) -> bool:
    return not re.search(r"\.(png|jpg|jpeg|gif|bmp|exe|dll|pdf|mp4|avi|mkv|mov|pptx?|docx?|xlsx?)$", filename, re.I)

def is_pdf(filename: str) -> bool:
    return filename.lower().endswith('.pdf')

def is_zip(filename: str) -> bool:
    return filename.lower().endswith('.zip')

def get_filename_from_url(url: str, asset_title: str) -> str:
    from urllib.parse import urlparse, parse_qs, unquote
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
        logging.error(f"Failed to extract zip {zip_path}: {e}")
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
        logging.error(f"Failed to preview PDF {pdf_path}: {e}")
        return f"[Error reading PDF: {e}]"