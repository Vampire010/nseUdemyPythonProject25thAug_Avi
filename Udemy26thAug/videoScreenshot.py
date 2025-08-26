import os
import time
import cv2
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- USER SETTINGS ---
m3u8_url = "https://www.udemy.com/assets/35357816/files/2021-08-07_08-10-23-f0420cdf436995091bef63c49990323a/2/aa00d84944423034059058c0302b6aa3a4bb.m3u8?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwYXRoIjoiMjAyMS0wOC0wN18wOC0xMC0yMy1mMDQyMGNkZjQzNjk5NTA5MWJlZjYzYzQ5OTkwMzIzYS8yLyIsImV4cCI6MTc1NjIwNzUwMn0.AMuo8YW_MlZ9j-hXpyq_IcPOZRWRcZezeI1Y7-iEl_s&provider=cloudfront&v=1"

# Specify your output folders
video_folder = r"C:\Users\giris\OneDrive\Documents\GitHub\nseUdemyPythonProject25thAug_Avi\Udemy26thAug\videoDownloaded"
screenshot_folder = r"C:\Users\giris\OneDrive\Documents\GitHub\nseUdemyPythonProject25thAug_Avi\Udemy26thAug\scene_frames\screenshots"
video_file = os.path.join(video_folder, "downloaded_video.mp4")
interval_sec = 5
ffmpeg_path = r"C:\ffmpeg\bin\ffmpeg.exe"

# --- Ensure folders exist ---
os.makedirs(video_folder, exist_ok=True)
os.makedirs(screenshot_folder, exist_ok=True)

# --- STEP 1: Launch URL with Selenium ---
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.implicitly_wait(10)
driver.get(m3u8_url)
print("URL launched in browser.")
time.sleep(5)
driver.quit()

# --- STEP 2: Download Video Using FFmpeg ---
if not os.path.exists(video_file):
    print("Downloading video with ffmpeg...")
    cmd = [ffmpeg_path, '-y', '-i', m3u8_url, '-c', 'copy', video_file]
    subprocess.run(cmd, check=True)
    print(f"Downloaded video: {video_file}")
else:
    print(f"Video already exists: {video_file}")

# --- STEP 3: Take Screenshot Every 5 Seconds ---
cap = cv2.VideoCapture(video_file)
fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration_sec = total_frames / fps if fps else 0

print(f"Video duration: {duration_sec:.2f} seconds. FPS: {fps}")

current_sec = 0
img_idx = 1

while current_sec < duration_sec:
    frame_num = int(current_sec * fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
    ret, frame = cap.read()
    if ret:
        img_path = os.path.join(screenshot_folder, f"screenshot_{img_idx:03d}.jpg")
        cv2.imwrite(img_path, frame)
        print(f"Saved {img_path} at {current_sec:.2f}s")
        img_idx += 1
    else:
        print(f"Could not read frame at {current_sec:.2f}s")
    current_sec += interval_sec

cap.release()
print("All screenshots taken.")