import os
import sys
import json
from dotenv import load_dotenv

# Add your YouTube API imports here (e.g., googleapiclient)

load_dotenv()
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_video_metadata():
    with open("data/todays_video.json", "r", encoding="utf-8") as f:
        strategy = json.load(f)
    return strategy.get("title", "Science Mystery Short"), strategy.get("description", "#shorts #science")

def save_upload_log(video_id, title):
    log_file = "data/upload_log.json"
    history = []
    
    # Try to load existing history as a JSON list
    if os.path.exists(log_file):
        try:
            with open(log_file, "r") as f:
                history = json.load(f)
        except json.JSONDecodeError:
            # If the file is broken (old format), start fresh
            print("⚠️ Existing upload log is corrupted. Starting a fresh log.")
            history = []

    # Append the new video to the list
    history.append({
        "video_id": video_id,
        "title": title
    })

    # Save it back as a properly formatted JSON list
    with open(log_file, "w") as f:
        json.dump(history, f, indent=4)

def upload_video():
    print("🚀 Upload Agent: Preparing for PUBLIC launch...")
    
    # 🚨 The Fail-Safe Check: Ensure a fresh video was actually rendered
    if not os.path.exists("data/video_ready.flag"):
        print("❌ CRITICAL: No fresh video ready flag found. Aborting ghost upload.")
        sys.exit(1)
        
    # Delete the flag so it cannot be reused on the next run
    os.remove("data/video_ready.flag")

    video_path = "data/final_short.mp4"
    title, description = get_video_metadata()

    print(f"Target Title: '{title}'")
    print("Privacy Status: PUBLIC ⚠️ (Going Live!)")
    print("⏳ Uploading to YouTube...")

    # =====================================================================
    # 🚨 INSERT YOUR YOUTUBE API UPLOAD CODE HERE
    # Execute the actual API call to upload `video_path`.
    # Assume the API call returns a successful `video_id`.
    # =====================================================================
    
    # --- Mock Example (Replace with your actual API response) ---
    video_id = "mock_video_id" # <--- REPLACE WITH ACTUAL ID FROM YOUTUBE
    # ------------------------------------------------------------

    print(f"✅ SUCCESS! Video uploaded.")
    print(f"Watch it here: https://youtube.com/shorts/{video_id}")
    
    # 🚨 Save the log safely as a JSON List
    save_upload_log(video_id, title)

if __name__ == "__main__":
    upload_video()