# Udemy26thAug/getCourseID.py
import os
import json
import requests
import pandas as pd

class UdemyLectureAssetExporter:
    """
    Fetches all lectures and their assets (including supplementary assets) for enrolled Udemy courses,
    and exports all attributes to an Excel spreadsheet.
    """

    def __init__(self, auth_file, output_file, base_folder):
        self.auth_file = auth_file
        self.output_file = output_file
        self.base_folder = base_folder

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
        self.cookie_headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US",
            "x-requested-with": "XMLHttpRequest"
        }
        self.cookies = {"access_token": self.ACCESS_TOKEN}

    def fetch_course_ids(self):
        base_url = "https://www.udemy.com/api-2.0/users/me/subscribed-courses?page_size=50"
        course_ids = []
        page = 1
        while base_url:
            print(f"📡 Fetching course page {page} ...")
            response = requests.get(base_url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                ids = [str(course["id"]) for course in results]
                course_ids.extend(ids)
                base_url = data.get("next")
                page += 1
            else:
                print("❌ Failed to fetch courses:", response.status_code, response.text)
                break
        print(f"✅ Total enrolled courses found: {len(course_ids)}")
        return course_ids

    def get_course_name(self, course_id):
        url = f"https://www.udemy.com/api-2.0/courses/{course_id}/?fields[course]=id,title"
        response = requests.get(url, headers=self.cookie_headers, cookies=self.cookies)
        if response.status_code == 200:
            return response.json().get("title", "Unknown Course")
        return "Unknown Course"

    def fetch_lectures_and_assets(self, course_id):
        course_name = self.get_course_name(course_id)
        url = (
            f"https://www.udemy.com/api-2.0/users/me/subscribed-courses/{course_id}/lectures/"
            "?page_size=1000&fields[lecture]=id,title,created,is_published,is_free,asset,supplementary_assets,sort_order,object_index,chapter"
        )
        response = requests.get(url, headers=self.cookie_headers, cookies=self.cookies)
        lectures_data = []
        if response.status_code == 200:
            results = response.json().get("results", [])
            # This variable holds the last known chapter from a mixed response.
            current_chapter = {"id": "", "title": "", "_class": ""}
            for item in results:
                item_class = item.get("_class", "")
                # If a lecture stores chapter info inline, use that.
                if item_class == "lecture":
                    lecture = item
                    # Use inline chapter if available; otherwise, fallback to current_chapter.
                    chapter = lecture.get("chapter", {})
                    if chapter:
                        chap_id = chapter.get("id", "")
                        chap_title = chapter.get("title", "")
                        chap_class = chapter.get("_class", "")
                    else:
                        chap_id = current_chapter.get("id", "")
                        chap_title = current_chapter.get("title", "")
                        chap_class = current_chapter.get("_class", "")
                    asset = lecture.get("asset", {})
                    base_row = {
                        "course_id": course_id,
                        "course_name": course_name,
                        "lecture__class": lecture.get("_class", ""),
                        "lecture_id": lecture.get("id", ""),
                        "lecture_title": lecture.get("title", ""),
                        "lecture_created": lecture.get("created", ""),
                        "lecture_is_published": lecture.get("is_published", ""),
                        "lecture_is_free": lecture.get("is_free", ""),
                        "lecture_sort_order": lecture.get("sort_order", ""),
                        "lecture_object_index": lecture.get("object_index", ""),
                        "asset__class": asset.get("_class", ""),
                        "asset_id": asset.get("id", ""),
                        "asset_asset_type": asset.get("asset_type", ""),
                        "asset_title": asset.get("title", ""),
                        "asset_status": asset.get("status", ""),
                        "asset_is_external": asset.get("is_external", ""),
                        "asset_filename": asset.get("filename", ""),
                        "asset_time_estimation": asset.get("time_estimation", ""),
                        "supplementary_asset__class": "",
                        "supplementary_asset_id": "",
                        "supplementary_asset_time_estimation": "",
                        "supplementary_asset_status": "",
                        "supplementary_asset_filename": "",
                        "supplementary_asset_asset_type": "",
                        "supplementary_asset_title": "",
                        "supplementary_asset_is_external": "",
                        "chapter_id": chap_id,
                        "chapter_class": chap_class,
                        "chapter_title": chap_title
                    }
                    supp_assets = lecture.get("supplementary_assets", [])
                    if supp_assets:
                        for supp in supp_assets:
                            supp_row = base_row.copy()
                            supp_row.update({
                                "supplementary_asset__class": supp.get("_class", ""),
                                "supplementary_asset_id": supp.get("id", ""),
                                "supplementary_asset_time_estimation": supp.get("time_estimation", ""),
                                "supplementary_asset_status": supp.get("status", ""),
                                "supplementary_asset_filename": supp.get("filename", ""),
                                "supplementary_asset_asset_type": supp.get("asset_type", ""),
                                "supplementary_asset_title": supp.get("title", ""),
                                "supplementary_asset_is_external": supp.get("is_external", ""),
                            })
                            lectures_data.append(supp_row)
                    else:
                        lectures_data.append(base_row)
                # If the current item is a chapter (and not a lecture), update the current chapter context.
                elif item_class == "chapter":
                    current_chapter = {
                        "id": item.get("id", ""),
                        "title": item.get("title", ""),
                        "_class": item.get("_class", "")
                    }
                # Ignore other types such as quizzes.
        else:
            print(f"❌ Failed to fetch lectures for course {course_id}: {response.status_code}")
        return lectures_data

    def fetch_subscriber_curriculum(self, course_id):
        """
        Fetches curriculum items using the subscriber-curriculum-items endpoint
        and extracts Course Id, Course Name, Chapter Id, Chapter Name, Lecture Id, Lecture Name,
        asset details and supplementary asset details.
        """
        course_name = self.get_course_name(course_id)
        url = (
            f"https://www.udemy.com/api-2.0/courses/{course_id}/subscriber-curriculum-items/"
            "?curriculum_types=chapter,lecture,practice,quiz,role-play&page_size=200"
            "&fields[lecture]=title,object_index,is_published,sort_order,created,asset,supplementary_assets,is_free"
            "&fields[quiz]=title,object_index,is_published,sort_order,type"
            "&fields[practice]=title,object_index,is_published,sort_order"
            "&fields[chapter]=title,object_index,is_published,sort_order"
            "&fields[asset]=title,filename,asset_type,status,time_estimation,is_external&caching_intent=True"
        )
        response = requests.get(url, headers=self.cookie_headers, cookies=self.cookies)
        rows = []
        if response.status_code == 200:
            results = response.json().get("results", [])
            current_chapter = {"id": "", "title": "", "_class": ""}
            for item in results:
                item_class = item.get("_class", "")
                if item_class in ["lecture", "quiz", "practice", "role-play"]:
                    lecture = item
                    chapter = lecture.get("chapter", {})
                    if chapter:
                        chap_id = chapter.get("id", "")
                        chap_title = chapter.get("title", "")
                        chap_class = chapter.get("_class", "")
                    else:
                        chap_id = current_chapter.get("id", "")
                        chap_title = current_chapter.get("title", "")
                        chap_class = current_chapter.get("_class", "")
                    asset = lecture.get("asset", {})
                    base_row = {
                        "course_id": course_id,
                        "course_name": course_name,
                        "chapter_id": chap_id,
                        "chapter_title": chap_title,
                        "item__class": lecture.get("_class", ""),
                        "lecture_id": lecture.get("id", ""),
                        "lecture_title": lecture.get("title", ""),
                        "item_created": lecture.get("created", ""),
                        "item_is_published": lecture.get("is_published", ""),
                        "item_is_free": lecture.get("is_free", ""),
                        "item_sort_order": lecture.get("sort_order", ""),
                        "item_object_index": lecture.get("object_index", ""),
                        "asset__class": asset.get("_class", ""),
                        "asset_id": asset.get("id", ""),
                        "asset_asset_type": asset.get("asset_type", ""),
                        "asset_title": asset.get("title", ""),
                        "asset_status": asset.get("status", ""),
                        "asset_is_external": asset.get("is_external", ""),
                        "asset_filename": asset.get("filename", ""),
                        "asset_time_estimation": asset.get("time_estimation", ""),                       
                        "supplementary_asset__class": "",
                        "supplementary_asset_id": "",
                        "supplementary_asset_time_estimation": "",
                        "supplementary_asset_status": "",
                        "supplementary_asset_filename": "",
                        "supplementary_asset_asset_type": "",
                        "supplementary_asset_title": "",
                        "supplementary_asset_is_external": ""
                    }
                    supp_assets = lecture.get("supplementary_assets", [])
                    if supp_assets:
                        for supp in supp_assets:
                            supp_row = base_row.copy()
                            supp_row.update({
                                "supplementary_asset__class": supp.get("_class", ""),
                                "supplementary_asset_id": supp.get("id", ""),
                                "supplementary_asset_time_estimation": supp.get("time_estimation", ""),
                                "supplementary_asset_status": supp.get("status", ""),
                                "supplementary_asset_filename": supp.get("filename", ""),
                                "supplementary_asset_asset_type": supp.get("asset_type", ""),
                                "supplementary_asset_title": supp.get("title", ""),
                                "supplementary_asset_is_external": supp.get("is_external", "")
                            })
                            rows.append(supp_row)
                    else:
                        rows.append(base_row)
                elif item_class == "chapter":
                    current_chapter = {
                        "id": item.get("id", ""),
                        "title": item.get("title", ""),
                        "_class": item.get("_class", "")
                    }
                else:
                    # Ignore other types
                    pass
        else:
            print(f"❌ Failed to fetch curriculum details for course {course_id}: {response.status_code}")
        return rows

    def export_to_excel(self, all_rows):
        if all_rows:
            df = pd.DataFrame(all_rows)
            df.to_excel(self.output_file, index=False)
            print(f"✅ Exported to {self.output_file}")
        else:
            print("⚠️ No lectures/assets found.")

    def run(self):
        course_ids = self.fetch_course_ids()
        all_rows = []
        for idx, course_id in enumerate(course_ids, start=1):
            print(f"📥 Fetching subscriber curriculum for course {idx}/{len(course_ids)}: {course_id} ...")
            all_rows.extend(self.fetch_subscriber_curriculum(course_id))
        self.export_to_excel(all_rows)

# ======================= USAGE =======================
if __name__ == "__main__":
    base_folder = r"./udemyDownloads"
    output_file = os.path.join(base_folder, "udemySubscriberCurriculumItems.xlsx")
    auth_file = "Authentication.json"   # contains {"access_token": "XXXX"}

    exporter = UdemyLectureAssetExporter(auth_file, output_file, base_folder)
    exporter.run()