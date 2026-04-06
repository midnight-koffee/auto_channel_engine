import json
import cv2
import numpy as np
import os
import requests
import subprocess
from dotenv import load_dotenv

load_dotenv()
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_script():
    with open("data/final_script.json", "r", encoding="utf-8") as f:
        script = json.load(f)
    with open("data/todays_video.json", "r", encoding="utf-8") as f:
        strategy = json.load(f)
    return strategy.get("topic", "science mystery"), script.get("full_spoken_script", "")

def fetch_background_video(keyword):
    print(f"🔍 Searching Pexels for: '{keyword[:50]}'...")
    api_key = os.getenv("PEXELS_API_KEY")
    headers = {"Authorization": api_key}
    
    response = requests.get(
        "https://api.pexels.com/videos/search",
        headers=headers,
        params={"query": keyword[:50], "per_page": 5, "orientation": "portrait"}
    )
    data = response.json()

    if not data.get("videos"):
        response = requests.get(
            "https://api.pexels.com/videos/search",
            headers=headers,
            params={"query": "galaxy space", "per_page": 5, "orientation": "portrait"}
        )
        data = response.json()

    video = data["videos"][0]
    # Pick lowest quality to avoid download issues on server
    video_files = sorted(
        [f for f in video["video_files"] if f.get("width")],
        key=lambda x: x.get("width", 0)
    )
    video_url = video_files[0]["link"]

    print(f"⬇️ Downloading background...")
    r = requests.get(video_url, stream=True, timeout=30)
    path = "data/background.mp4"
    with open(path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print("✅ Background downloaded.")
    return path

def create_text_image(text, size=(1080, 1920)):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line) + len(word) + 1 <= 28:
            current_line += (" " + word) if current_line else word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    img = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 2.0
    thickness = 4
    line_height = 90
    y_start = size[1] // 2 - (len(lines) * line_height) // 2

    for i, line in enumerate(lines):
        textsize = cv2.getTextSize(line, font, font_scale, thickness)[0]
        x = (size[0] - textsize[0]) // 2
        y = y_start + i * line_height
        cv2.putText(img, line, (x+4, y+4), font, font_scale, (0,0,0), thickness+3)
        cv2.putText(img, line, (x, y), font, font_scale, (255,255,255), thickness)

    overlay_path = "data/text_overlay.png"
    cv2.imwrite(overlay_path, img)
    return overlay_path

def get_audio_duration(audio_path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())

def build_video():
    print("🎬 Video Agent V3 (FFmpeg Direct): Assembling Short...")

    topic, text = load_script()
    audio_path = "data/voiceover.mp3"
    output_path = "data/final_short.mp4"

    if not os.path.exists(audio_path):
        print("❌ voiceover.mp3 missing.")
        return

    duration = get_audio_duration(audio_path)
    print(f"Audio duration: {duration:.1f}s")

    bg_path = fetch_background_video(topic)
    overlay_path = create_text_image(text)

    print("⏳ Rendering with FFmpeg...")

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", bg_path,
        "-i", overlay_path,
        "-i", audio_path,
        "-filter_complex",
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[bg];"
        f"[bg][1:v]overlay=0:0[v]",
        "-map", "[v]",
        "-map", "2:a",
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ FFmpeg error:\n{result.stderr[-500:]}")
        return

    print(f"✅ Video saved to {output_path}")

if __name__ == "__main__":
    build_video()