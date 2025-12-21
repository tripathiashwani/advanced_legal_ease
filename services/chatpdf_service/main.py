from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from gemini import stream_from_gemini

app = FastAPI()

# Add logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"🌐 HTTP Request: {request.method} {request.url}")
    response = await call_next(request)
    print(f"📤 Response: {response.status_code}")
    return response

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print("=" * 60)
    print("🚀 WEBSOCKET ENDPOINT HIT - CLIENT ATTEMPTING CONNECTION")
    print(f"Client: {websocket.client}")
    print(f"Headers: {websocket.headers}")
    print("=" * 60)
    await websocket.accept()
    print("✅ WEBSOCKET CONNECTION ACCEPTED AND ESTABLISHED!")
    print("=" * 60)

    history = [
        {
            "role": "model",
            "parts": [
                {
                    "text": "Hello! I'm your Docextract.ai assistant. I can help you with information about Docextract.ai, services, and support. How can I assist you today?"
                }
            ]
        }
    ]

    while True:
        try:
            data = await websocket.receive_text()
            print("=" * 60)
            print(f"📥 RECEIVED MESSAGE FROM CLIENT: '{data}'")
            print(f"📏 Message length: {len(data)} characters")
            print("=" * 60)
            
            if data.lower() == "exit":
                await websocket.close()
                print("WebSocket connection closed")
                break
            
            # Add system instruction with the user message
            user_message = f"You are an AI assistant for Docextract.ai. Only talk about Docextract, services, or support. Do not answer unrelated questions. User question: {data}"
            
            history.append({
                "role": "user",
                "parts": [{"text": user_message}]
            })

            full_response = ""
            async for chunk in stream_from_gemini(history):
                full_response += chunk
                await websocket.send_text(chunk)
            
            # Add the complete response to history for context
            if full_response.strip():
                history.append({
                    "role": "model",
                    "parts": [{"text": full_response}]
                })

        except Exception as e:
            print(f"Error: {e}")
            break

# Add a simple HTTP endpoint to test if the server is working
@app.get("/test")
async def test_endpoint():
    print("🧪 Test endpoint hit!")
    return {"message": "Server is working!", "websocket_available": True}

# Add a direct route for the main page to debug
@app.get("/debug")
async def debug_page():
    print("🏠 Debug page accessed!")
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head><title>Debug Page</title></head>
    <body>
        <h1>Server is working!</h1>
        <p>If you see this, the server is running correctly.</p>
        <a href="/">Go to main page</a>
    </body>
    </html>
    """)

# Serve static files from the client directory (this must be last!)
app.mount("/", StaticFiles(directory="../client", html=True), name="static")