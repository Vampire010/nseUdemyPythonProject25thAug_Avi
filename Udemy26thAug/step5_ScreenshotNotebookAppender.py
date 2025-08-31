import os
import base64
import re
from nbformat import read, write, NO_CONVERT, v4

def normalize_name(name):
    # Lowercase, remove non-alphanumeric characters
    return re.sub(r'[^a-z0-9]', '', name.lower())

class ScreenshotNotebookAppender:
    def __init__(self, notebook_path, screenshot_folder):
        self.notebook_path = notebook_path
        self.screenshot_folder = screenshot_folder

    def append_screenshots(self):
        with open(self.notebook_path, "r", encoding="utf-8") as f:
            nb = read(f, as_version=NO_CONVERT)

        screenshots = sorted([
            f for f in os.listdir(self.screenshot_folder)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ])

        if not screenshots:
            print(f"No screenshots found in {self.screenshot_folder}")
            return

        for img in screenshots:
            img_path = os.path.join(self.screenshot_folder, img)
            with open(img_path, "rb") as img_file:
                img_bytes = img_file.read()
                img_b64 = base64.b64encode(img_bytes).decode("utf-8")

            ext = os.path.splitext(img)[1].lower()
            mime = "image/png" if ext == ".png" else "image/jpeg" if ext in [".jpg", ".jpeg"] else "application/octet-stream"

            cell = v4.new_markdown_cell(f"![{img}](attachment:{img})")
            cell['attachments'] = {img: {mime: img_b64}}
            nb.cells.append(cell)

        with open(self.notebook_path, "w", encoding="utf-8") as f:
            write(nb, f)

        print(f"Appended {len(screenshots)} screenshots as attachments to {self.notebook_path}")

def find_matching_screenshot_folder(screenshots_root, rel_path_parts, notebook_name):
    # Normalize notebook name
    target_name = normalize_name(notebook_name)
    # Build candidate path
    candidate_root = os.path.join(screenshots_root, *rel_path_parts)
    if not os.path.exists(candidate_root):
        return None
    # Search for folder with matching normalized name
    for folder in os.listdir(candidate_root):
        if os.path.isdir(os.path.join(candidate_root, folder)):
            if normalize_name(folder) == target_name:
                return os.path.join(candidate_root, folder)
    return None

def process_all_notebooks(notebooks_root, screenshots_root):
    for root, dirs, files in os.walk(notebooks_root):
        for file in files:
            if file.endswith(".ipynb"):
                notebook_path = os.path.join(root, file)
                rel_path = os.path.relpath(root, notebooks_root)
                rel_path_parts = rel_path.split(os.sep) if rel_path != '.' else []
                notebook_name = os.path.splitext(file)[0]
                screenshot_folder = find_matching_screenshot_folder(screenshots_root, rel_path_parts, notebook_name)
                print(f"Notebook: {notebook_path}")
                print(f"Looking for screenshots in: {screenshot_folder}")
                if screenshot_folder and os.path.exists(screenshot_folder):
                    appender = ScreenshotNotebookAppender(notebook_path, screenshot_folder)
                    appender.append_screenshots()
                else:
                    print(f"No matching screenshot folder for: {notebook_path}")

if __name__ == "__main__":
    notebooks_root = r"C:\Users\giris\OneDrive\Documents\GitHub\nseUdemyPythonProject25thAug_Avi\Udemy26thAug\udemyDownloads\notebooks"
    screenshots_root = r"C:\Users\giris\OneDrive\Documents\GitHub\nseUdemyPythonProject25thAug_Avi\Udemy26thAug\udemyDownloads\scene_frames"
    process_all_notebooks(notebooks_root, screenshots_root)