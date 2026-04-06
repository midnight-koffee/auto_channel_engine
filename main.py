import subprocess
import sys
import time

def run_pipeline():
    print("🚀 INITIALIZING AUTONOMOUS YOUTUBE ENGINE...\n")
    
    agents = [
        "agents/feedback_agent.py",
        "agents/strategist.py",     
        "agents/script_agent.py",   
        "agents/voice_agent.py",    
        "agents/video_agent.py",    
        "agents/upload_agent.py",
        "agents/report_agent.py"    # <--- NEW: Pings your phone at the end
    ]

    start_time = time.time()

    for agent in agents:
        print(f"{'='*50}")
        print(f"▶ WAKING AGENT: {agent}")
        print(f"{'='*50}")
        
        result = subprocess.run([sys.executable, agent])
        
        if result.returncode != 0:
            print(f"\n❌ FATAL ERROR: {agent} failed. Halting pipeline.")
            return
            
        print("\n")
        time.sleep(2)

    end_time = time.time()
    elapsed = round((end_time - start_time) / 60, 2)
    
    print(f"{'='*50}")
    print(f"🎉 MISSION ACCOMPLISHED.")
    print(f"⏱️ Total Engine Runtime: {elapsed} minutes.")
    print(f"{'='*50}")

if __name__ == "__main__":
    run_pipeline()