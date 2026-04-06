import os
import base64
import re

print("🚀 Running automated cloud prep...")

# 1. Save Token to a file automatically
try:
    with open("token.pickle", "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    with open("cloud_token.txt", "w") as f:
        f.write(encoded)
    print("✅ Saved base64 token securely to cloud_token.txt (Open this later for Railway)")
except Exception as e:
    print(f"❌ Error with token.pickle: {e}")

# 2. Auto-Generate requirements.txt
with open("requirements.txt", "w") as f:
    f.write("google-api-python-client\ngoogle-auth-httplib2\ngoogle-auth-oauthlib\ngoogle-genai\nmoviepy==1.0.3\nopencv-python-headless\nnumpy\nrequests\npython-dotenv\nedge-tts\n")
print("✅ Generated requirements.txt")

# 3. Auto-Generate .gitignore
with open(".gitignore", "w") as f:
    f.write(".env\ntoken.pickle\n__pycache__/\nautovenv/\ndata/final_short.mp4\ndata/background.mp4\ndata/voiceover.mp3\ncloud_token.txt\n")
print("✅ Generated .gitignore")

# 4. Auto-Patch the Python Agents
new_auth_func = """def get_authenticated_service():
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
    return build("youtube", "v3", credentials=creds)"""

for file_path in ["agents/upload_agent.py", "agents/feedback_agent.py"]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Regex to find and replace the old function seamlessly
        pattern = re.compile(r"def get_authenticated_service\(\):.*?return build\([^)]+\)", re.DOTALL)
        if pattern.search(content):
            content = pattern.sub(new_auth_func, content)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Auto-patched {file_path}")
        else:
            print(f"⚠️ Could not find function in {file_path}")
    except Exception as e:
        print(f"❌ Error patching {file_path}: {e}")

print("\n🎉 All local prep is DONE.")