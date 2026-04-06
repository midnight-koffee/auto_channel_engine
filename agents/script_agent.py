import json
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def load_strategy():
    with open("data/todays_video.json", "r") as f:
        return json.load(f)

def write_script():
    strategy = load_strategy()
    
    prompt = f"""
    You are an expert YouTube Shorts scriptwriter. 
    Take this strategy and write the final spoken script.

    TOPIC: {strategy['topic']}
    TITLE: {strategy['title']}
    PREVIEW: {strategy['script']}

    CONSTRAINTS:
    - The script must be exactly 35 to 40 words (perfect for a fast 15-second Short).
    - Start with a powerful 3-second hook.
    - End with a call to action.
    - The tone should be engaging, scientific, and slightly mysterious.

    Return ONLY a valid JSON object matching this exact schema:
    {{"full_spoken_script": "string", "word_count": "number"}}
    """

    print("✍️ Script Agent: Writing the final 15-second script...")
    
    client = genai.Client()
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    
    script_data = json.loads(response.text)
    
    with open("data/final_script.json", "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=4)
        
    print("\n✅ Final Script Written and Saved to 'final_script.json'!")

if __name__ == "__main__":
    write_script()