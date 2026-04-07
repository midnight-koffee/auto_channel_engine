import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def send_discord_ping():
    print("📢 Report Agent: Compiling daily dispatch...")
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    
    if not webhook_url:
        print("❌ No DISCORD_WEBHOOK_URL found in .env. Skipping report.")
        return

    try:
        # Load the upload history
        with open("data/upload_log.json", "r") as f:
            history = json.load(f)
            
        if not history:
            print("⚠️ Upload log is empty. Nothing to report.")
            return

        # Grab the NEWEST video (the last item in the list)
        latest_video = history[-1]
        
        # Build the message
        video_id = latest_video.get('video_id', 'Unknown ID')
        video_title = latest_video.get('title', 'Unknown Title')
        video_url = f"https://youtube.com/shorts/{video_id}"
        
        message = f"🚀 **NEW VIDEO UPLOADED SUCCESSFULLY!**\n\n**Title:** {video_title}\n**Link:** {video_url}\n\n*The Autonomous Engine has completed its daily run.*"

        # Send it to Discord
        data = {"content": message}
        response = requests.post(webhook_url, json=data)
        
        if response.status_code == 204:
            print("✅ Report successfully pinged to your phone!")
        else:
            print(f"⚠️ Failed to send Discord ping. Status code: {response.status_code}")

    except FileNotFoundError:
        print("❌ upload_log.json not found. Cannot send report.")
    except Exception as e:
        print(f"❌ Error sending Discord report: {e}")

if __name__ == "__main__":
    send_discord_ping()