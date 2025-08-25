import os
import json
import requests
from openpyxl import Workbook


class UdemyCourseFetcher:
    def __init__(self, base_folder, auth_file="Authentication.json"):
        self.base_folder = base_folder
        self.auth_file = auth_file
        self.all_courses = []

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

    def fetch_courses(self):
        base_url = "https://www.udemy.com/api-2.0/users/me/subscribed-courses?page_size=50"
        course_count = 1
        page = 1

        while base_url:
            print(f"📡 Fetching page {page}...")
            response = requests.get(base_url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                self.all_courses.extend(results)

                # Print course titles and IDs
                for course in results:
                    print(f"{course_count}. {course['title']} - {course['id']}")
                    course_count += 1

                base_url = data.get("next")
                page += 1
            else:
                print("❌ Failed to fetch courses:", response.status_code, response.text)
                break

        print(f"\n✅ Total courses fetched: {len(self.all_courses)}")

    def save_to_excel(self):
        wb = Workbook()
        ws = wb.active
        ws.title = "Udemy Courses"

        ws.append(["S.No", "Course ID", "Course Title", "Completion Ratio", "Last Accessed Time"])

        for index, course in enumerate(self.all_courses, start=1):
            ws.append([
                index,
                course.get("id"),
                course.get("title"),
                course.get("completion_ratio", 0),
                course.get("last_accessed_time", "N/A")
            ])

        output_file = os.path.join(self.base_folder, "udemy_courses.xlsx")
        wb.save(output_file)
        print(f"📁 Excel file saved: {output_file}")

    def run(self):
        self.fetch_courses()
        if self.all_courses:
            self.save_to_excel()


if __name__ == "__main__":
    BASE_FOLDER = r"./udemyDownloads"

    udemy_fetcher = UdemyCourseFetcher(base_folder=BASE_FOLDER)
    udemy_fetcher.run()
