import os
import json
import pickle
from googleapiclient.discovery import build
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

def fetch_feedback():
    print("📈 Feedback Agent: Waking up to evaluate performance...")

    if not os.path.exists("data/upload_log.json"):
        print("ℹ️ No upload log found. Skipping feedback loop for now.")
        return

    with open("data/upload_log.json", "r", encoding="utf-8") as f:
        log_lines = f.readlines()
        
    recent_uploads = []
    for line in log_lines:
        try:
            recent_uploads.append(json.loads(line.strip()))
        except json.JSONDecodeError:
            continue

    if not recent_uploads:
        return

    youtube = get_authenticated_service()
    if not youtube:
        return

    video_ids = [upload["video_id"] for upload in recent_uploads[-5:]]

    request = youtube.videos().list(
        part="statistics,snippet",
        id=",".join(video_ids)
    )
    response = request.execute()

    fresh_stats = {}
    for item in response.get("items", []):
        vid_id = item["id"]
        views = int(item["statistics"].get("viewCount", 0))
        likes = int(item["statistics"].get("likeCount", 0))
        
        # THE ALGORITHM: Likes are worth 10x more than a simple view.
        score = views + (likes * 10) 
        
        fresh_stats[vid_id] = {
            "title": item["snippet"]["title"],
            "views": views,
            "likes": likes,
            "score": score
        }

    with open("data/channel_memory.json", "r", encoding="utf-8") as f:
        memory = json.load(f)

    updated_count = 0
    for vid_id, stats in fresh_stats.items():
        found = False
        for mem_video in memory:
            if mem_video.get("video_id") == vid_id:
                mem_video["views"] = stats["views"]
                mem_video["likes"] = stats["likes"]
                mem_video["score"] = stats["score"]
                found = True
                updated_count += 1
                break
        
        if not found:
            stats["video_id"] = vid_id
            memory.append(stats)
            updated_count += 1

    with open("data/channel_memory.json", "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4)

    print(f"✅ Feedback Loop Closed: Scored and updated {updated_count} videos.")

if __name__ == "__main__":
    fetch_feedback()