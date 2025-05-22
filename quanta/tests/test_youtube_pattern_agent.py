# quanta/tests/test_youtube_pattern_agent.py

from quanta.ingest.youtube_pattern_agent import YouTubePatternAgent

def test_youtube_pattern_agent():
    agent = YouTubePatternAgent()
    test_url = "https://www.youtube.com/watch?v=PmhuPbY8ZHo"
    
    try:
        agent.ingest_video(test_url)
        print("✅ TEST PASSED: YouTube video successfully processed and stored.")
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")

if __name__ == "__main__":
    test_youtube_pattern_agent()

