import os
import re
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell
from docx import Document
import pandas as pd

# ---------- Helpers ----------
def safe_folder_name(name: str) -> str:
    """Replace invalid folder characters with underscore."""
    return re.sub(r'[<>:"/\\|?*]', "_", str(name)).strip()

def normalize_name(name: str) -> str:
    """Normalize names for matching (ignore case, spaces, underscores, dashes)."""
    return re.sub(r'[\s_\-]+', '', str(name)).lower()

def read_docx_sections(docx_path):
    """Read DOCX and return structure: {course -> {section -> [lectures]}}"""
    doc = Document(docx_path)
    courses = {}
    current_course, current_section = None, None

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        if para.style.name.startswith("Heading 1"):  # Course
            current_course = text
            courses[current_course] = {}
            current_section = None  # reset section

        elif para.style.name.startswith("Heading 2"):  # Section
            if current_course is None:
                # Skip orphan section
                continue
            current_section = text
            courses[current_course][current_section] = []

        elif para.style.name.startswith("Heading 3"):  # Lecture
            if current_course and current_section:
                courses[current_course][current_section].append(text)

    return courses

def generate_notebooks(docx_path, output_dir, excel_path):
    # Read course outline
    courses = read_docx_sections(docx_path)

    # Read Excel resources
    df = pd.read_excel(excel_path)
    resource_map = {
        normalize_name(str(row["asset_title"])): str(row["download_url"])
        for _, row in df.iterrows()
        if pd.notna(row.get("asset_title")) and pd.notna(row.get("download_url"))
    }

    for course, sections in courses.items():
        course_dir = os.path.join(output_dir, safe_folder_name(course))
        os.makedirs(course_dir, exist_ok=True)

        for section, lectures in sections.items():
            section_dir = os.path.join(course_dir, safe_folder_name(section))
            os.makedirs(section_dir, exist_ok=True)

            for lecture in lectures:
                lecture_clean = re.sub(r'^\d+\s*-\s*', '', lecture).strip()
                lecture_file = safe_folder_name(lecture_clean) + ".ipynb"
                lecture_path = os.path.join(section_dir, lecture_file)

                nb = new_notebook()
                cells = [new_markdown_cell(f"# {lecture_clean}")]

                # Attach resources if matched
                for asset, url in resource_map.items():
                    if asset in normalize_name(lecture_clean):
                        cells.append(new_markdown_cell(f"📎 **Resource:** [{asset}]({url})"))

                nb.cells = cells

                with open(lecture_path, "w", encoding="utf-8") as f:
                    nbformat.write(nb, f)

                print(f"✅ Created: {lecture_path}")

# ---------- Main ----------
if __name__ == "__main__":
    docx_path = r"C:\Users\giris\source\repos\nseDemoUemyPythonProject\Udemy\udemyDownloads\DockerExample.docx"
    output_dir = r"C:\Users\giris\source\repos\nseDemoUemyPythonProject\Udemy\UdemyCourses"
    excel_path = r"C:\Users\giris\source\repos\nseDemoUemyPythonProject\Udemy\udemyDownloads\udemy_resources.xlsx"

    generate_notebooks(docx_path, output_dir, excel_path)
