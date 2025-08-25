import os
import nbformat
from nbformat.v4 import new_markdown_cell
import re
import zipfile

# ---------- Helpers ----------
def normalize_name(name: str) -> str:
    """Make filenames comparable (ignore case, spaces, underscores, dashes)."""
    return re.sub(r'[\s_\-]+', '', name).lower()

def find_resource_file(resources_dir, resource_name):
    """
    Recursively search for a resource file inside course/section/lecture folders.
    Uses fuzzy match for small differences (spaces, underscores, case).
    Returns absolute path if found, else None.
    """
    target = normalize_name(resource_name)
    print(f"🔍 Looking for: {resource_name} (normalized: {target})")

    for root, dirs, files in os.walk(resources_dir):
        for f in files:
            if normalize_name(f) == target:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, resources_dir)
                print(f"✅ Found match: {f} at {rel_path}")
                return full_path
    return None


def insert_file_content(new_cells, resource_name, rel_path, content):
    """Helper to append file content as a new markdown cell."""
    new_cells.append(new_markdown_cell(
        f"### 📄 Resource File: **{resource_name}**  \n"
        f"📂 Path: `{rel_path}`\n\n"
        f"```\n{content}\n```"
    ))


# ---------- Main Logic ----------
def insert_resources_into_notebook(nb_path, resources_dir):
    if not os.path.exists(nb_path):
        print(f"❌ Notebook file not found: {nb_path}")
        return

    with open(nb_path, "r", encoding="utf-8") as f:
        try:
            nb = nbformat.read(f, as_version=4)
        except Exception as e:
            print(f"❌ Failed to read notebook {nb_path}: {e}")
            return

    new_cells = []
    resources_appended = 0

    for cell in nb.cells:
        new_cells.append(cell)

        if cell.cell_type == "markdown":
            for line in cell.source.splitlines():
                if "Orange" in line and "</font>" in line:
                    match = re.search(r">([^<]+)</font>", line)
                    if match:
                        resource_name = match.group(1).strip()

                        # Clean "Resource:" prefix
                        if resource_name.lower().startswith("resource:"):
                            resource_name = resource_name.split(":", 1)[1].strip()

                        print(f"🔎 Found resource reference: {resource_name}")

                        # 🔍 Search inside course resources
                        resource_path = find_resource_file(resources_dir, resource_name)

                        if resource_path:
                            try:
                                if resource_path.lower().endswith(".zip"):
                                    # 📦 Handle ZIP file
                                    with zipfile.ZipFile(resource_path, "r") as zf:
                                        for member in zf.namelist():
                                            # Skip folders and binary files
                                            if member.endswith("/") or re.search(r"\.(png|jpg|jpeg|gif|bmp|exe|dll|pdf|mp4|avi|mkv)$", member, re.I):
                                                continue
                                            try:
                                                content = zf.read(member).decode("utf-8", errors="ignore")
                                                rel_member_path = os.path.join(os.path.relpath(resource_path, resources_dir), member)
                                                insert_file_content(new_cells, member, rel_member_path, content)
                                                resources_appended += 1
                                                print(f"✅ Appended {member} from ZIP {resource_name}")
                                            except Exception as e:
                                                print(f"⚠️ Could not read {member} in {resource_name}: {e}")
                                else:
                                    # 📄 Handle normal text file
                                    with open(resource_path, "r", encoding="utf-8", errors="ignore") as rf:
                                        content = rf.read()
                                    rel_path = os.path.relpath(resource_path, resources_dir)
                                    insert_file_content(new_cells, resource_name, rel_path, content)
                                    resources_appended += 1
                                    print(f"✅ Appended content of {resource_name} from {rel_path}")
                            except Exception as e:
                                print(f"⚠️ Could not read resource {resource_name}: {e}")
                        else:
                            print(f"⚠️ Resource file not found in {resources_dir} for {resource_name}")

    nb.cells = new_cells

    with open(nb_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)

    if resources_appended > 0:
        print(f"🎉 {resources_appended} resources appended into {os.path.basename(nb_path)}")
    else:
        print(f"ℹ️ No resources appended for {os.path.basename(nb_path)}")


# ---------- Run ----------
if __name__ == "__main__":
    notebook_file = r"C:\Users\giris\source\repos\nseDemoUemyPythonProject\Udemy\udemy_notebooks_enhanced\397068__Selenium_Webdriver_with_PYTHON_from_Scratch_+_Frameworks_enhanced_v2.ipynb"
    resources_dir = r"C:\Users\giris\source\repos\nseDemoUemyPythonProject\Udemy\Resourcesdownloads"

    insert_resources_into_notebook(notebook_file, resources_dir)
