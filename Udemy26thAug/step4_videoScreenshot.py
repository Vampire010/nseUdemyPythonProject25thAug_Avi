import os
import cv2
import re

def safe_name(name: str) -> str:
    s = re.sub(r'[<>:"/\\|?*\n\r\t]', "_", str(name))
    s = s.strip()
    s = re.sub(r"_+", "_", s)
    s = s.rstrip(" .")
    reserved = {
        "CON","PRN","AUX","NUL",
        "COM1","COM2","COM3","COM4","COM5","COM6","COM7","COM8","COM9",
        "LPT1","LPT2","LPT3","LPT4","LPT5","LPT6","LPT7","LPT8","LPT9"
    }
    if s.upper() in reserved or s == "":
        s = f"_{s}_" if s else "Untitled"
    if len(s) > 120:
        s = s[:120]
    return s

def get_folder_parts(rel_path):
    parts = rel_path.split(os.sep)
    course = safe_name(parts[0]) if len(parts) > 0 else "UnknownCourse"
    section_idx, section_name = 0, "No Section"
    lecture_idx, lecture_name = 0, "Untitled"
    if len(parts) > 1:
        try:
            section_idx, section_name = parts[1].split("_", 1)
            section_idx = int(section_idx)
        except Exception:
            section_idx, section_name = 0, parts[1]
    if len(parts) > 2:
        try:
            lecture_idx, lecture_name = parts[2].split("_", 1)
            lecture_idx = int(lecture_idx)
        except Exception:
            lecture_idx, lecture_name = 0, parts[2]
    return course, section_idx, section_name, lecture_idx, lecture_name

def get_screenshot_folder(base_dir, course, section_idx, section_name, lecture_idx, lecture_name):
    section_folder = f"{section_idx:02d}_{safe_name(section_name)}"
    lecture_folder = f"{lecture_idx:02d}_{safe_name(lecture_name)}"
    folder = os.path.join(base_dir, safe_name(course), section_folder, lecture_folder)
    os.makedirs(folder, exist_ok=True)
    return folder

video_root = "./udemyDownloads/videoDownloaded"
screenshot_root = "./udemyDownloads/scene_frames"
interval_sec = 5

for root, dirs, files in os.walk(video_root):
    for file in files:
        if file.endswith(".mp4"):
            video_path = os.path.join(root, file)
            rel_path = os.path.relpath(root, video_root)
            course, section_idx, section_name, lecture_idx, lecture_name = get_folder_parts(rel_path)
            screenshot_folder = get_screenshot_folder(
                screenshot_root, course, section_idx, section_name, lecture_idx, lecture_name
            )

            print(f"\n---\nProcessing video: {video_path}")
            print(f"Saving screenshots to: {screenshot_folder}")

            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"Failed to open video: {video_path}")
                continue
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration_sec = total_frames / fps if fps else 0

            current_sec = 0
            img_idx = 1

            while current_sec < duration_sec:
                frame_num = int(current_sec * fps)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                ret, frame = cap.read()
                if ret:
                    img_path = os.path.join(screenshot_folder, f"screenshot_{img_idx:03d}.jpg")
                    cv2.imwrite(img_path, frame)
                    print(f"Saved {img_path} at {current_sec:.2f}s for video {video_path}")
                    img_idx += 1
                else:
                    print(f"Could not read frame at {current_sec:.2f}s in video {video_path}")
                current_sec += interval_sec

            cap.release()
print("All screenshots taken.")