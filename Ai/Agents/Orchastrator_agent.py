

from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import google_search
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import asyncio
import os
from dotenv import load_dotenv
import logging
from google.adk.tools.tool_context import ToolContext
from vertexai import rag
from config import DEFAULT_DISTANCE_THRESHOLD, DEFAULT_TOP_K
from utils import check_corpus_exists, get_corpus_resource_name
from sub_agents.sequentila_agent import pipeline
# Load environment variables
load_dotenv()

# Configure authentication - try Google AI API first, then Vertex AI
if os.getenv('GOOGLE_API_KEY'):
    # Use Google AI API
    os.environ.setdefault('GOOGLE_API_KEY', os.getenv('GOOGLE_API_KEY'))
    print("Using Google AI API")
elif os.getenv('GOOGLE_CLOUD_PROJECT') and os.getenv('GOOGLE_CLOUD_LOCATION'):
    # Use Vertex AI
    import google.auth
    from google.cloud import aiplatform
    
    # Initialize Vertex AI
    aiplatform.init(
        project=os.getenv('GOOGLE_CLOUD_PROJECT'),
        location=os.getenv('GOOGLE_CLOUD_LOCATION')
    )
    print("Using Google Cloud Vertex AI")
else:
    print("Warning: No authentication configured. Please set either:")
    print("- GOOGLE_API_KEY for Google AI API")
    print("- GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION for Vertex AI")

# Constants
APP_NAME = "islamic_sermon_app"
USER_ID = "user_123"
SESSION_ID = "session_456"



session_service = InMemorySessionService()
runner = Runner(
    agent=pipeline,
    app_name=APP_NAME,
    session_service=session_service
)



async def generate_sermon_async(topic: str) -> str:
    """Generate Islamic sermon based on topic using runner with proper async handling."""
    # Ensure session exists, create if it doesn't
    session = await session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    if session is None:
        session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    
    # Format the query to be more specific for sermon generation
    sermon_query = f"""Please generate a comprehensive Islamic sermon about '{topic}'. 

Follow these steps:
1. First, search for relevant content using the Islamic content database
2. Create an authentic, inspiring sermon that incorporates the retrieved content
3. Structure it according to traditional Islamic sermon format
4. Include practical guidance for the Muslim community
5. The sermon should be in arabic only 
6. The sermon should be suitable for Friday prayers or community gatherings."""
    
    user_content = types.Content(role='user', parts=[types.Part(text=sermon_query)])
    
    final_response_content = "No response received."
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=user_content):
        print(f"Event: {event}")
        if event.is_final_response() and event.content and event.content.parts:
            final_response_content = event.content.parts[0].text
            break
    
    return final_response_content