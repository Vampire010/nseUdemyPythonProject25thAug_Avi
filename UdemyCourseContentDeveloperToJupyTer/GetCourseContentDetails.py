import os
import json
import requests


class UdemyCourseOutline:
    def __init__(self, base_folder, course_id, auth_file="Authentication.json"):
        self.base_folder = base_folder
        self.course_id = course_id
        self.auth_file = auth_file

        # Ensure base folder exists
        os.makedirs(self.base_folder, exist_ok=True)

        # Load authentication data
        with open(self.auth_file, "r") as f:
            auth_data = json.load(f)
        self.ACCESS_TOKEN = auth_data.get("access_token")

        self.headers = {
            "Authorization": f"Bearer {self.ACCESS_TOKEN}",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json"
        }

    def fetch_curriculum(self):
        url = f"https://www.udemy.com/api-2.0/courses/{self.course_id}/subscriber-curriculum-items/?page_size=1000"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            print("❌ Failed to fetch data:", response.status_code)
            return None
        return response.json()

    def print_outline(self, data):
        current_section = None
        lesson_count = 0
        section_lesson_count = 0
        section_duration = 0
        section_index = 0

        for item in data.get("results", []):
            item_type = item.get("_class")
            title = item.get("title")
            duration = item.get("asset", {}).get("time_estimation", 0)  # in seconds
            duration_min = f"{duration // 60}min" if duration else ""

            if item_type == "chapter":
                if current_section:
                    print(f"\n    🔹 {section_lesson_count} lectures | ⏱ {section_duration}min")
                section_index += 1
                section_lesson_count = 0
                section_duration = 0
                current_section = title
                print(f"\n▶ Section {section_index}: {title}")

            elif item_type == "lecture":
                section_lesson_count += 1
                lesson_count += 1
                section_duration += duration // 60
                check = "✔"
                print(f"  {check} {lesson_count}. {title}  ⏱ {duration_min}")

        # Print last section summary
        if current_section:
            print(f"\n    🔹 {section_lesson_count} lectures | ⏱ {section_duration}min")

    def run(self):
        print(f"📘 Fetching curriculum for Course ID: {self.course_id}")
        data = self.fetch_curriculum()
        if data:
            self.print_outline(data)


if __name__ == "__main__":
    BASE_FOLDER = r"C:\Users\giris\source\repos\nseDemoUemyPythonProject\Udemy\udemyDownloads"
    COURSE_ID = 397068  # replace with your Udemy course ID

    udemy_outline = UdemyCourseOutline(base_folder=BASE_FOLDER, course_id=COURSE_ID)
    udemy_outline.run()
