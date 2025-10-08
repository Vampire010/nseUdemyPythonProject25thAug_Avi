import pandas as pd
import requests
import json

class VideoTranscriptionFetcher:
    def __init__(self, excel_path, output_json=r"./udemyDownloads/videoTranscriptions.json", COURSE_IDS_TO_PROCESS=None):
        self.excel_path = excel_path
        self.df = None
        self.output_json = output_json
        self.transcriptions = []
        self.COURSE_IDS_TO_PROCESS = COURSE_IDS_TO_PROCESS or []

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

        # Only process rows with course_id in COURSE_IDS_TO_PROCESS
        df_filtered = self.df[self.df["course_id"].isin(self.COURSE_IDS_TO_PROCESS)]

        for _, row in df_filtered.iterrows():
            course_id = row.get("course_id")
            url = row.get('caption_url')
            if pd.isna(url):
                continue
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
    # Specify the course IDs you want to process
    COURSE_IDS_TO_PROCESS = [2942646]  # <-- Replace with your actual course IDs

    fetcher = VideoTranscriptionFetcher(excel_path, COURSE_IDS_TO_PROCESS=COURSE_IDS_TO_PROCESS)
    fetcher.run()