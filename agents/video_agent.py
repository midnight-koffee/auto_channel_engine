import json
import cv2
import numpy as np
import os
import requests
from moviepy.editor import AudioFileClip, VideoFileClip, CompositeVideoClip, ImageClip, concatenate_videoclips
from dotenv import load_dotenv

load_dotenv()

def load_script():
    with open("data/todays_video.json", "r", encoding="utf-8") as f:
        strategy = json.load(f)
        
    with open("data/final_script.json", "r", encoding="utf-8") as f:
        script = json.load(f)
        
    return strategy.get("topic", "science mystery"), script.get("full_spoken_script", "")

def fetch_background_video(keyword):
    print(f"🔍 Searching Pexels for: '{keyword}'...")
    
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        print("❌ Error: PEXELS_API_KEY not found in .env")
        return None

    headers = {"Authorization": api_key}
    # We ask for portrait orientation to minimize cropping issues
    response = requests.get(
        "https://api.pexels.com/videos/search",
        headers=headers,
        params={"query": keyword, "per_page": 5, "orientation": "portrait"}
    )
    
    data = response.json()
    
    if not data.get("videos"):
        print("⚠️ No videos found for that topic. Using fallback: 'galaxy'")
        response = requests.get(
            "https://api.pexels.com/videos/search",
            headers=headers,
            params={"query": "galaxy", "per_page": 5, "orientation": "portrait"}
        )
        data = response.json()

    # Get the best quality video file link
    try:
        video = data["videos"][0]
        video_url = sorted(
            video["video_files"],
            key=lambda x: x.get("width", 0),
            reverse=True
        )[0]["link"]
    except (IndexError, KeyError):
        print("❌ Error parsing Pexels response.")
        return None

    print(f"⬇️ Downloading cinematic background...")
    r = requests.get(video_url, stream=True)
    path = "data/background.mp4"
    with open(path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
            
    print("✅ Background downloaded.")
    return path

def crop_to_vertical(clip):
    """Ensures the video is perfectly 9:16 (1080x1920) without stretching."""
    target_ratio = 1080 / 1920
    clip_ratio = clip.w / clip.h

    if clip_ratio > target_ratio:
        # Video is too wide, crop the sides
        new_w = int(clip.h * target_ratio)
        x_center = clip.w / 2
        return clip.crop(x1=x_center - new_w/2, y1=0, x2=x_center + new_w/2, y2=clip.h).resize((1080, 1920))
    else:
        # Video is too tall, crop top/bottom
        new_h = int(clip.w / target_ratio)
        y_center = clip.h / 2
        return clip.crop(x1=0, y1=y_center - new_h/2, x2=clip.w, y2=y_center + new_h/2).resize((1080, 1920))

def create_text_overlay(text, duration, size=(1080, 1920)):
    """Creates a transparent image with centered, shadowed text."""
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

    img = np.zeros((size[1], size[0], 4), dtype=np.uint8) 
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 2.2
    thickness = 4
    line_height = 90

    y_start = size[1] // 2 - (len(lines) * line_height) // 2

    for i, line in enumerate(lines):
        textsize = cv2.getTextSize(line, font, font_scale, thickness)[0]
        x = (size[0] - textsize[0]) // 2
        y = y_start + i * line_height

        # Black shadow drop for contrast
        cv2.putText(img, line, (x+4, y+4), font, font_scale, (0, 0, 0, 255), thickness + 3)
        # Main white text
        cv2.putText(img, line, (x, y), font, font_scale, (255, 255, 255, 255), thickness)

    return ImageClip(img, duration=duration)

def build_video():
    print("🎬 Video Agent V2: Assembling Dynamic Short...")

    topic, text = load_script()
    
    if not os.path.exists("data/voiceover.mp3"):
        print("❌ Error: voiceover.mp3 missing.")
        return

    audio = AudioFileClip("data/voiceover.mp3")
    duration = audio.duration

    # 1. Fetch and prep background
    bg_path = fetch_background_video(topic)
    if not bg_path:
        return
        
    bg = VideoFileClip(bg_path, audio=False)

    # 2. Loop background if it's shorter than the audio
    if bg.duration < duration:
        loops = int(duration / bg.duration) + 1
        bg = concatenate_videoclips([bg] * loops)

    # 3. Crop and trim exactly to audio length
    bg = bg.subclip(0, duration)
    bg = crop_to_vertical(bg)

    # 4. Generate Text
    txt = create_text_overlay(text, duration)

    # 5. Final Composite
    final = CompositeVideoClip([bg, txt])
    final = final.set_audio(audio)

    output_path = "data/final_short.mp4"
    print("⏳ Rendering final MP4... This might take 1-2 minutes...")
    final.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        logger=None
    )

    print(f"\n✅ SUCCESS! V2 Video saved to {output_path}")

if __name__ == "__main__":
    build_video()