import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# We use force-ssl so the agent has permission to upload videos later
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def get_authenticated_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
            
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run so it's fully autonomous
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)

if __name__ == "__main__":
    print("Waking up the engine...")
    youtube = get_authenticated_service()
    
    # Ping the API to get your specific channel stats
    request = youtube.channels().list(
        part="snippet,statistics",
        mine=True
    )
    response = request.execute()

    if response["items"]:
        channel = response["items"][0]
        print("\n✅ Authentication Successful! The Engine has access.")
        print("-" * 40)
        print(f"Channel Name:     {channel['snippet']['title']}")
        print(f"Subscribers:      {channel['statistics']['subscriberCount']}")
        print(f"Total Views:      {channel['statistics']['viewCount']}")
        print(f"Videos Uploaded:  {channel['statistics']['videoCount']}")
        print("-" * 40)
    else:
        print("❌ Connected, but no channel found for this Google account.")