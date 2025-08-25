import os
import re
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell
from docx import Document
import zipfile

# ---------- Helpers ----------
def normalize_name(name: str) -> str:
    return re.sub(r'[\s_\-]+', '', name).lower()

def safe_filename(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def find_resource_file(resources_dir, resource_name):
    target = normalize_name(resource_name)
    for root, _, files in os.walk(resources_dir):
        for f in files:
            if normalize_name(f) == target:
                return os.path.join(root, f)
    return None

def insert_file_content(cells, resource_name, rel_path, content):
    cells.append(new_markdown_cell(
        f"#### 📄 Resource: **{resource_name}**\n"
        f"📂 Path: `{rel_path}`\n\n"
        f"```text\n{content}\n```"
    ))

def process_resource(cells, resources_dir, resource_name):
    resource_path = find_resource_file(resources_dir, resource_name)
    if not resource_path:
        print(f"⚠️ Resource not found: {resource_name}")
        return

    rel_path = os.path.relpath(resource_path, resources_dir)
    try:
        if resource_path.lower().endswith(".zip"):
            with zipfile.ZipFile(resource_path, "r") as zf:
                for member in zf.namelist():
                    if member.endswith("/"):
                        continue
                    if re.search(r"\.(png|jpg|jpeg|gif|bmp|exe|dll|pdf|mp4|avi|mkv)$", member, re.I):
                        continue
                    try:
                        content_bytes = zf.read(member)
                        try:
                            content = content_bytes.decode("utf-8")
                        except UnicodeDecodeError:
                            content = content_bytes.decode("latin-1", errors="ignore")
                        rel_member_path = os.path.join(rel_path, member)
                        insert_file_content(cells, member, rel_member_path, content)
                        print(f"✅ Appended {member} from ZIP {resource_name}")
                    except Exception as e:
                        print(f"⚠️ Could not read {member} in {resource_name}: {e}")
        else:
            with open(resource_path, "r", encoding="utf-8", errors="ignore") as rf:
                content = rf.read()
            insert_file_content(cells, resource_name, rel_path, content)
            print(f"✅ Appended {resource_name} from {rel_path}")
    except Exception as e:
        print(f"⚠️ Failed resource {resource_name}: {e}")


# ---------- Main Logic ----------
def generate_notebooks(docx_path, output_dir, resources_dir):
    doc = Document(docx_path)

    current_course = None
    section_index = 0
    lecture_index = 0
    current_section = None
    current_nb = None
    current_nb_path = None

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # 🟢 New course
        if text.startswith("Course ID:"):
            # Save last open notebook if any
            if current_nb and current_nb_path:
                with open(current_nb_path, "w", encoding="utf-8") as f:
                    nbformat.write(current_nb, f)

            current_course = safe_filename(text)
            section_index = 0
            lecture_index = 0
            current_section = None
            current_nb = None
            current_nb_path = None

            print(f"\n📘 Course: {text}")
            continue

        # 🟢 New section
        if text.startswith("Section"):
            section_index += 1
            lecture_index = 0
            section_title = safe_filename(text)
            current_section = f"{section_index:02d} - {section_title}"
            print(f"📂 Section {section_index:02d}: {text}")
            continue

        # 🟢 New lecture
        if re.match(r"^\d+\s*-\s*", text):
            # Save previous lecture
            if current_nb and current_nb_path:
                with open(current_nb_path, "w", encoding="utf-8") as f:
                    nbformat.write(current_nb, f)

            lecture_index += 1

            # Remove numbers at start
            lecture_title = re.sub(r"^\d+\s*-\s*", "", text).strip()
            # Remove "(Time: ...)" from title (robust: handles extra spaces, case, weird chars)
            lecture_title = re.sub(r"\( *Time:.*?\)", "", lecture_title, flags=re.IGNORECASE).strip()

            # Extract time info separately
            time_info_match = re.search(r"\( *Time:\s*([^)]+)\)", text, flags=re.IGNORECASE)
            time_info = f"\n\n⏱️ {time_info_match.group(1)}" if time_info_match else ""

            lecture_filename = f"{lecture_index:02d} - {safe_filename(lecture_title)}.ipynb"

            current_nb = new_notebook()
            # ✅ Title only, with time below if available
            current_nb.cells = [new_markdown_cell(f"# 🎥 {lecture_title}{time_info}")]

            folder = os.path.join(output_dir, current_course, current_section)
            os.makedirs(folder, exist_ok=True)
            current_nb_path = os.path.join(folder, lecture_filename)

            print(f"➡️ Lecture {section_index:02d}.{lecture_index:02d}: {lecture_title}")
            continue

        # 🟢 Resource line
        if text.startswith("Resource:") and current_nb:
            resource_name = text.split("Resource:", 1)[1].strip()
            process_resource(current_nb.cells, resources_dir, resource_name)

    # Save last lecture of last course
    if current_nb and current_nb_path:
        with open(current_nb_path, "w", encoding="utf-8") as f:
            nbformat.write(current_nb, f)


# ---------- Run ----------
if __name__ == "__main__":
    docx_path = r"C:\Users\giris\source\repos\nseDemoUemyPythonProject\Udemy\udemyDownloads\DockerExample.docx"
    output_dir = r"C:\Users\giris\source\repos\nseDemoUemyPythonProject\Udemy\UdemyCourses"
    resources_dir = r"C:\Users\giris\source\repos\nseDemoUemyPythonProject\Udemy\Resourcesdownloads"

    generate_notebooks(docx_path, output_dir, resources_dir)
