import json
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def load_memory():
    with open("data/channel_memory.json", "r") as f:
        return json.load(f)

def formulate_strategy():
    videos = load_memory()
    
    # Sort by the new intelligent SCORE metric, not just raw views
    sorted_videos = sorted(videos, key=lambda x: x.get("score", x.get("views", 0)), reverse=True)
    
    top_3 = sorted_videos[:3]
    bottom_3 = sorted_videos[-3:] if len(sorted_videos) >= 6 else []
    all_titles = [v["title"] for v in sorted_videos]

    top_performers_text = "\n".join([f"- '{v['title']}' (Score: {v.get('score', v.get('views', 0))})" for v in top_3])
    worst_performers_text = "\n".join([f"- '{v['title']}' (Score: {v.get('score', v.get('views', 0))})" for v in bottom_3])
    all_covered_text = "\n".join([f"- {t}" for t in all_titles])

    prompt = f"""
    You are the creative Brain Agent of an autonomous YouTube channel called PulsePerception.
    The channel focuses on mind-bending science, psychology, and strange mysteries.

    FEEDBACK LOOP (LEARN FROM THIS):
    These videos performed the BEST based on an engagement algorithm. Analyze why and do more of this:
    {top_performers_text}

    These videos performed the WORST. Avoid this style or topic:
    {worst_performers_text}

    ALL PAST TOPICS (Do NOT repeat these exact topics):
    {all_covered_text}

    TASK:
    Generate the next 15-second YouTube Short based on the feedback loop above. 
    1. Create a fresh topic inspired by the winners, avoiding the losers.
    2. Write a highly engaging, fast-paced script preview.
    3. Write a catchy title.
    4. Provide 5 hashtags.
    
    Return ONLY a valid JSON object matching this exact schema: 
    {{"topic": "string", "title": "string", "script": "string", "hashtags": ["string", "string"]}}
    """

    print("🧠 Strategist Agent: Analyzing algorithmic feedback and memory...")
    
    client = genai.Client()
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    
    strategy_data = json.loads(response.text)
    
    with open("data/todays_video.json", "w", encoding="utf-8") as f:
        json.dump(strategy_data, f, indent=4)
        
    print("\n✅ Strategy Decided based on Feedback Loop!")
    print(f"📌 Topic:  {strategy_data['topic']}")

if __name__ == "__main__":
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ Error: GEMINI_API_KEY not found in .env file.")
    else:
        formulate_strategy()