# app.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types
import uuid

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("⚠️ python-dotenv not installed. Install with: pip install python-dotenv")
except Exception as e:
    print(f"⚠️ Could not load .env file: {e}")

# Check for required API key
if not os.getenv("GOOGLE_API_KEY"):
    print("❌ GOOGLE_API_KEY not found in environment variables!")
    print("Please create a .env file with:")
    print("GOOGLE_API_KEY=your_actual_api_key_here")
    print("Get your API key from: https://aistudio.google.com/app/apikey")

# Configure ADK to use API keys directly (not Vertex AI)
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

# 1. Define request schema
class QueryRequest(BaseModel):
    query: str

# 2. Initialize ADK agent, session service, and runner
app = FastAPI()

# Create session service
session_service = InMemorySessionService()

try:
    agent = Agent(
        name="search_agent",
        tools=[google_search],
        model="gemini-2.0-flash-exp"  # or other supported LLM
    )
    
    # Create runner with session service
    runner = Runner(
        agent=agent,
        app_name="search_app",
        session_service=session_service
    )
    print("✅ Agent and runner initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize agent: {e}")
    runner = None

@app.post("/query")
async def run_query(req: QueryRequest):
    if not runner:
        raise HTTPException(status_code=500, detail="Agent not properly initialized. Check API key configuration.")
    
    if not os.getenv("GOOGLE_API_KEY"):
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY not configured. Please set it in your .env file.")
    
    # 3. Create content and run the agent
    user_content = types.Content(parts=[types.Part(text=req.query)])
    user_id = "default_user"  # In production, get from authentication
    session_id = str(uuid.uuid4())  # Generate unique session ID per request
    
    try:
        # Create session before running
        session = await session_service.create_session(
            app_name="search_app",
            user_id=user_id,
            session_id=session_id
        )
        
        # Collect all events and return the final response
        events = []
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_content
        ):
            events.append(event)
        
        # Extract the agent's response from the events
        response_text = ""
        print(len(events))
        for event in events:
            if hasattr(event, 'content') and event.content:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        response_text += part.text
        
        return {"response": response_text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

# 4. Run with: uvicorn app:app --reload
