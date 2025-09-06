import pandas as pd
import requests
import json

class VideoTranscriptionFetcher:
    def __init__(self, excel_path, output_json=r"./udemyDownloads/videoTranscriptions.json", EXCLUDED_COURSE_IDS=None):
        self.excel_path = excel_path
        self.df = None
        self.output_json = output_json
        self.transcriptions = []
        self.EXCLUDED_COURSE_IDS = EXCLUDED_COURSE_IDS or []

    def read_excel(self):
        try:
            self.df = pd.read_excel(self.excel_path)
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return False
        return True

    def fetch_transcriptions(self):
        if self.df is None:
            print("Excel file not loaded.")
            return

        if 'caption_url' not in self.df.columns:
            print("The column 'caption_url' does not exist in the Excel file.")
            return

        for _, row in self.df.iterrows():
            course_id = row.get("course_id")
            if course_id in self.EXCLUDED_COURSE_IDS:
                print(f"Skipping excluded course_id {course_id}")
                continue

            url = row.get('caption_url')
            if pd.isna(url):
                continue
            # Collect all relevant details from the row
            details = {
                "course_id": course_id,
                "course_name": row.get("course_name", ""),
                "chapter_id": row.get("chapter_id", ""),
                "chapter_title": row.get("chapter_title", ""),
                "item_class": row.get("item_class", ""),
                "lecture_id": row.get("lecture_id", ""),
                "lecture_title": row.get("lecture_title", ""),
                "caption_url": url
            }
            try:
                response = requests.get(url)
                transcription = response.text
                print(f"Fetched transcription for: {details['lecture_title']}")
                details["transcription"] = transcription
                self.transcriptions.append(details)
            except requests.RequestException as e:
                print(f"Error fetching URL {url}: {e}")
                details["transcription"] = None
                self.transcriptions.append(details)

        with open(self.output_json, "w", encoding="utf-8") as f:
            json.dump(self.transcriptions, f, ensure_ascii=False, indent=2)

    def run(self):
        if self.read_excel():
            self.fetch_transcriptions()

if __name__ == "__main__":
    excel_path = r"./udemyDownloads/udemyCaptionsWithUrl.xlsx"
    # Add more IDs as needed
    EXCLUDED_COURSE_IDS = [  2186622, 2847630, 3118336, 3195180, 3465656, 1422920,
    5436376, 5524980, 5720876, 5412670, 5600412, 571876, 5339746, 4299801, 4581660,
    5631164, 5763504, 5070128, 5173778, 4510136, 4601546, 6024616, 1035000, 4672206,
    3980730, 5684142, 4668148, 4595938, 5752334, 1565838, 3652610, 5573566, 397068] 

    fetcher = VideoTranscriptionFetcher(excel_path, EXCLUDED_COURSE_IDS=EXCLUDED_COURSE_IDS)
    fetcher.run()