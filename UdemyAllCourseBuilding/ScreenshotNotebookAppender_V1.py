import os
import base64
from nbformat import read, write, NO_CONVERT, v4

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

            # Determine mime type
            ext = os.path.splitext(img)[1].lower()
            if ext == ".png":
                mime = "image/png"
            elif ext in [".jpg", ".jpeg"]:
                mime = "image/jpeg"
            else:
                mime = "application/octet-stream"

            # Create markdown cell with attachment
            cell = v4.new_markdown_cell(f"![{img}](attachment:{img})")
            cell['attachments'] = {
                img: {
                    mime: img_b64
                }
            }
            nb.cells.append(cell)

        with open(self.notebook_path, "w", encoding="utf-8") as f:
            write(nb, f)

        print(f"Appended {len(screenshots)} screenshots as attachments to {self.notebook_path}")

if __name__ == "__main__":
    appender = ScreenshotNotebookAppender(
        notebook_path=r"C:\Users\giris\OneDrive\Documents\GitHub\nseUdemyPythonProject25thAug_Avi\Udemy26thAug\udemyDownloads\notebooks\Web Scraping In Python_ Master The Fundamentals\01_Prerequisite knowledge\01_Installing Webscraping Prerequisite Libraries.ipynb",
        screenshot_folder=r"C:\Users\giris\OneDrive\Documents\GitHub\nseUdemyPythonProject25thAug_Avi\Udemy26thAug\udemyDownloads\scene_frames\Web Scraping In Python Master The Fundamentals\01_Prerequisite knowledge\01_Installing Webscraping Prerequisite Libraries"
    )
    appender.append_screenshots()