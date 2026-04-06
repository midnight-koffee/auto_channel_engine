import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def send_report():
    print("📢 Report Agent: Compiling daily dispatch...")

    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("❌ Error: DISCORD_WEBHOOK_URL not found in .env. Skipping notification.")
        return

    try:
        # Read the upload log
        with open("logs/upload_log.json", "r", encoding="utf-8") as f:
            lines = f.readlines()
            if not lines:
                return
            
            # The last line is the video we JUST uploaded
            last_upload = json.loads(lines[-1].strip())
            
            # The second-to-last line is yesterday's video (if it exists)
            yesterday_upload = json.loads(lines[-2].strip()) if len(lines) > 1 else None

    except Exception as e:
        print(f"❌ Error reading logs: {e}")
        return

    # Find yesterday's stats in memory
    y_title = "N/A"
    y_views, y_likes, y_score = 0, 0, 0
    
    if yesterday_upload:
        y_title = yesterday_upload.get("title", "Unknown")
        try:
            with open("data/channel_memory.json", "r", encoding="utf-8") as f:
                memory = json.load(f)
                for video in memory:
                    if video.get("video_id") == yesterday_upload.get("video_id"):
                        y_views = video.get("views", 0)
                        y_likes = video.get("likes", 0)
                        y_score = video.get("score", 0)
                        break
        except Exception:
            pass

    # Construct the Discord message
    title = last_upload.get("title", "Unknown Title")
    url = last_upload.get("url", "")

    message = f"🚀 **PulsePerception Agent Finished!**\n\n"
    message += f"🎬 **JUST UPLOADED:**\n"
    message += f"> {title}\n"
    message += f"> 🔗 {url}\n\n"
    
    if yesterday_upload:
        message += f"📈 **YESTERDAY's PERFORMANCE:**\n"
        message += f"> **{y_title}**\n"
        message += f"> 👀 Views: {y_views}\n"
        message += f"> 👍 Likes: {y_likes}\n"
        message += f"> 🧠 Agent Score: {y_score}\n"

    # Send to Discord
    payload = {"content": message}
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code in [200, 204]:
            print("✅ Report successfully pinged to your phone!")
        else:
            print(f"❌ Failed to ping Discord: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Discord network request failed: {e}")

if __name__ == "__main__":
    send_report()