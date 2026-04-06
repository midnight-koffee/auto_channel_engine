import json
import os
from auth_test import get_authenticated_service

def fetch_channel_intelligence(max_results=20):
    youtube = get_authenticated_service()
    print("🤖 Ingestion Agent: Accessing YouTube Data...")

    # 1. Get the 'Uploads' playlist ID (this is where all your videos live)
    channels_response = youtube.channels().list(
        part="contentDetails",
        mine=True
    ).execute()

    uploads_playlist_id = channels_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # 2. Get the video IDs from that playlist
    playlist_items = youtube.playlistItems().list(
        part="snippet",
        playlistId=uploads_playlist_id,
        maxResults=max_results
    ).execute()

    video_ids = [item["snippet"]["resourceId"]["videoId"] for item in playlist_items.get("items", [])]

    if not video_ids:
        print("❓ No videos found on this channel.")
        return

    # 3. Get detailed stats (Views, Likes) for those specific IDs
    stats_response = youtube.videos().list(
        part="snippet,statistics",
        id=",".join(video_ids)
    ).execute()

    processed_videos = []
    for item in stats_response.get("items", []):
        processed_videos.append({
            "video_id": item["id"],
            "title": item["snippet"]["title"],
            "published_at": item["snippet"]["publishedAt"],
            "views": int(item["statistics"].get("viewCount", 0)),
            "likes": int(item["statistics"].get("likeCount", 0)),
            "comments": int(item["statistics"].get("commentCount", 0))
        })

    # 4. Save to 'Memory'
    os.makedirs("data", exist_ok=True)
    with open("data/channel_memory.json", "w") as f:
        json.dump(processed_videos, f, indent=4)

    print(f"✅ Memory Updated: {len(processed_videos)} videos analyzed.")
    
    # Show the top performing video to prove it worked
    top_video = max(processed_videos, key=lambda x: x['views'])
    print(f"🔥 Top Performer: '{top_video['title']}' with {top_video['views']} views.")

if __name__ == "__main__":
    fetch_channel_intelligence()