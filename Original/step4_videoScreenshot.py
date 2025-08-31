import os
import cv2

video_root = "./udemyDownloads/videoDownloaded"
screenshot_root = "./udemyDownloads/scene_frames"
interval_sec = 5

for root, dirs, files in os.walk(video_root):
    for file in files:
        if file.endswith(".mp4"):
            video_path = os.path.join(root, file)
            # Get relative path from video_root
            rel_path = os.path.relpath(root, video_root)
            # Create corresponding screenshot folder
            screenshot_folder = os.path.join(screenshot_root, rel_path)
            os.makedirs(screenshot_folder, exist_ok=True)

            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration_sec = total_frames / fps if fps else 0

            print(f"Processing: {video_path}")
            print(f"Saving screenshots to: {screenshot_folder}")

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