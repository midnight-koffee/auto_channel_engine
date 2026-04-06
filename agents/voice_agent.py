import json
import asyncio
import edge_tts
import os

def load_script():
    with open("data/final_script.json", "r", encoding="utf-8") as f:
        return json.load(f)

async def generate_voice():
    print("🎙️ Voice Agent: Waking up...")
    
    script_data = load_script()
    text = script_data.get("full_spoken_script", "")
    
    if not text:
        print("❌ Error: No script found in final_script.json")
        return

    print(f"Reading script: {len(text.split())} words.")
    
    # We use a deep, engaging voice (Christopher is great for science/mystery)
    VOICE = "en-US-ChristopherNeural"
    OUTPUT_FILE = "data/voiceover.mp3"
    
    print("⏳ Generating neural audio...")
    communicate = edge_tts.Communicate(text, VOICE)
    
    await communicate.save(OUTPUT_FILE)
    
    print(f"\n✅ SUCCESS! Voiceover generated and saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    asyncio.run(generate_voice())