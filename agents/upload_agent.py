import os
import json
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

def get_authenticated_service():
    import base64, os, pickle
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    creds = None
    token_b64 = os.getenv("YOUTUBE_TOKEN_BASE64")
    if token_b64:
        creds = pickle.loads(base64.b64decode(token_b64))
    elif os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            if os.path.exists("token.pickle"):
                with open("token.pickle", "wb") as token:
                    pickle.dump(creds, token)
        else:
            return None
    return build("youtube", "v3", credentials=creds)

def upload_video():
    print("🚀 Upload Agent: Preparing for PUBLIC launch...")

    if not os.path.exists("data/final_short.mp4"):
        print("❌ Error: final_short.mp4 missing. Run video_agent.py first.")
        return
        
    with open("data/todays_video.json", "r", encoding="utf-8") as f:
        strategy = json.load(f)

    with open("data/final_script.json", "r", encoding="utf-8") as f:
        script_data = json.load(f)

    youtube = get_authenticated_service()
    if not youtube:
        return

    # 1. Title formatting
    title = strategy.get("title", "PulsePerception Short")[:100]

    # 2. Hashtags formatting (FIX: Explicitly add #shorts)
    raw_hashtags = strategy.get("hashtags", [])
    clean_hashtags = [h if h.startswith('#') else f"#{h}" for h in raw_hashtags]
    if "#shorts" not in [h.lower() for h in clean_hashtags]:
        clean_hashtags.append("#shorts")
    
    hashtags_str = " ".join(clean_hashtags)

    # 3. Description
    transcript = script_data.get("full_spoken_script", "")
    description = (
        f"Did you know? 🤔 Subscribe for more mind-bending science and mysteries! \n\n"
        f"Transcript:\n{transcript}\n\n"
        f"{hashtags_str}\n\n"
        f"(Note: Some visuals in this video may be AI-assisted.)"
    )

    print(f"Target Title: '{title}'")
    print("Privacy Status: PUBLIC ⚠️ (Going Live!)")
    
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": [h.replace('#', '') for h in clean_hashtags],
            "categoryId": "28"  
        },
        "status": {
            "privacyStatus": "public",  
            "selfDeclaredMadeForKids": False
        }
    }

    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload("data/final_short.mp4", chunksize=-1, resumable=True)
    )

    print("⏳ Uploading to YouTube... ")
    
    response = None
    while response is None:
        status, response = insert_request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")

    print(f"\n✅ SUCCESS! Video uploaded.")
    video_url = f"https://youtube.com/shorts/{response['id']}"
    print(f"Watch it here: {video_url}")

    # FIX: Log the upload so the agent has a history
    log_entry = {"video_id": response["id"], "title": title, "url": video_url}
    with open("data/upload_log.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

if __name__ == "__main__":
    upload_video()