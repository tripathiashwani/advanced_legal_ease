import os
import httpx
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print("GEMINI_API_KEY:", GEMINI_API_KEY)  # Debugging line to check if the key is loaded

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent"

async def stream_from_gemini(history):
    print(f"🔥 Starting Gemini API call with history: {len(history)} messages")
    headers = {
        "Content-Type": "application/json"
    }
    params = {
        "key": GEMINI_API_KEY
    }
    body = {
        "contents": history,
        "generationConfig": {
            "temperature": 0.9,
            "maxOutputTokens": 100
        }
    }
    print(f"📤 Sending request to Gemini API...")
    print(f"📋 Request body: {body}")

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream("POST", GEMINI_URL, params=params, headers=headers, json=body) as response:
                print(f"📡 Response status: {response.status_code}")
                print(f"📡 Response headers: {dict(response.headers)}")
                
                if response.status_code != 200:
                    error_text = await response.aread()
                    print(f"❌ API Error: {response.status_code} - {error_text.decode()}")
                    return
                
                chunk_count = 0
                full_response = ""
                async for line in response.aiter_lines():
                    line = line.strip()
                    if not line:
                        continue
                    
                    print(f"🔍 Raw line: {line}")
                    full_response += line
                
                # Parse the complete response once we have it all
                try:
                    import json
                    print(f"🔧 Attempting to parse complete response ({len(full_response)} chars)")
                    response_data = json.loads(full_response)
                    
                    # Handle array of response objects
                    if isinstance(response_data, list):
                        for item in response_data:
                            if "candidates" in item and len(item["candidates"]) > 0:
                                candidate = item["candidates"][0]
                                if "content" in candidate and "parts" in candidate["content"]:
                                    parts = candidate["content"]["parts"]
                                    if len(parts) > 0 and "text" in parts[0]:
                                        text_content = parts[0]["text"]
                                        chunk_count += 1
                                        print(f"📦 Chunk {chunk_count}: '{text_content}'")
                                        yield text_content
                    
                except json.JSONDecodeError as je:
                    print(f"❌ Failed to parse complete response: {je}")
                    print(f"Response preview: {full_response[:200]}...")
                except Exception as parse_error:
                    print(f"❌ Parse error: {parse_error}")
                
                print(f"✅ Finished streaming. Total chunks: {chunk_count}")
    
    except Exception as e:
        print(f"💥 Exception in Gemini API call: {e}")
        print(f"💥 Exception type: {type(e).__name__}")