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
from sub_agents.search_agent import search_agent
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

def query_islamic_content(query: str , tool_context: ToolContext) -> dict:
    """
    Search the Islamic sermon database for relevant Arabic content and teachings.
    
    This function queries a comprehensive Arabic Islamic sermon database to find
    relevant content for sermon generation. Use descriptive keywords in both 
    Arabic and English for best results.
    
    Args:
        query (str): Search query for Islamic content. Use descriptive keywords
                    related to your topic (e.g., "الزواج marriage sermon", 
                    "الطلاق divorce guidance", "المجتمع community teachings")
    
    Returns:
        dict: Search results containing:
            - status: "success", "warning", or "error"
            - message: Human-readable description of the result
            - results: List of relevant content with source information
            - results_count: Number of results found
            - query: The original search query
    """
    try:
        # Fixed corpus name - in production, this could be configurable
        corpus_name = "projects/ultimate-figure-447502-u3/locations/us-central1/ragCorpora/6917529027641081856"
        
        # Create a dummy tool context for internal use
        
        # Check if the corpus exists
        if not check_corpus_exists(corpus_name, tool_context):
            return {
                "status": "error",
                "message": f"Islamic content database is not available. Please contact system administrator.",
                "query": query,
                "results": [],
                "results_count": 0,
            }

        # Get the corpus resource name
        corpus_resource_name = get_corpus_resource_name(corpus_name)

        # Configure retrieval parameters
        rag_retrieval_config = rag.RagRetrievalConfig(
            top_k=DEFAULT_TOP_K,
            filter=rag.Filter(vector_distance_threshold=DEFAULT_DISTANCE_THRESHOLD),
        )

        # Perform the query
        print(f"Searching Islamic content database for: {query}")
        response = rag.retrieval_query(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=corpus_resource_name,
                )
            ],
            text=query,
            rag_retrieval_config=rag_retrieval_config,
        )

        # Process the response into a more usable format
        results = []
        if hasattr(response, "contexts") and response.contexts:
            for ctx_group in response.contexts.contexts:
                result = {
                    "source_uri": (
                        ctx_group.source_uri if hasattr(ctx_group, "source_uri") else ""
                    ),
                    "source_name": (
                        ctx_group.source_display_name
                        if hasattr(ctx_group, "source_display_name")
                        else ""
                    ),
                    "content": ctx_group.text if hasattr(ctx_group, "text") else "",
                    "relevance_score": ctx_group.score if hasattr(ctx_group, "score") else 0.0,
                }
                results.append(result)

        # If we didn't find any results
        if not results:
            return {
                "status": "warning",
                "message": f"No relevant Islamic content found for query: '{query}'. Try using different keywords or broader search terms.",
                "query": query,
                "results": [],
                "results_count": 0,
            }

        return {
            "status": "success",
            "message": f"Found {len(results)} relevant Islamic content pieces for your sermon topic",
            "query": query,
            "results": results,
            "results_count": len(results),
        }

    except Exception as e:
        error_msg = f"Error accessing Islamic content database: {str(e)}"
        logging.error(error_msg)
        return {
            "status": "error",
            "message": "Unable to access Islamic content database. Please try again later.",
            "query": query,
            "results": [],
            "results_count": 0,
        }

# Create the Islamic Sermon Generator Agent
islamic_sermon_agent = LlmAgent(
    model="gemini-2.0-flash-exp",
    name="islamic_sermon_generator",
    description="An Islamic sermon generator that creates authentic sermons based on Arabic Islamic content from a comprehensive database",
    instruction="""# Islamic Sermon Generator Assistant

## Your Role
You are an expert Islamic sermon generator with deep knowledge of Islamic teachings, Quranic verses, Hadith, and Islamic history. Your primary task is to create Arabic meaningfull, authentic, and inspirational Islamic sermons based on content retrieved from a comprehensive Arabic Islamic sermon database.

## Core Responsibilities

### 1. Sermon Generation Process
When a user requests a sermon:
1. **Identify the Topic**: Carefully analyze the user's request to understand the desired sermon topic
2. **Query the Database**: Use the `query_islamic_content` tool to search for relevant Arabic Islamic content
3. **Synthesize Content**: Create a comprehensive sermon incorporating the retrieved authentic content
4. **Structure the Sermon**: Follow traditional Islamic sermon structure with proper flow

### 2. Using the Islamic Content Search Tool
Use the `query_islamic_content` tool when:
- The user requests a sermon on any Islamic topic
- You need authentic Islamic content for sermon creation
- The user asks about specific Islamic teachings or practices

**Search Strategy:**
- Use descriptive Arabic and English keywords related to the topic
- For marriage sermons: "الزواج خطبة الزواج marriage sermon"
- For divorce guidance: "الطلاق guidance divorce wisdom"
- For community topics: "المجتمع community unity Islamic society"
- For worship: "الصلاة prayer worship ibadah"

### 3. Sermon Structure Guidelines
Create sermons with this structure:

**Opening:**
- Begin with Islamic greetings and praise to Allah
- Include relevant Quranic verses or Hadith as introduction
- The opening should be in arabic only
**Main Content:**
- Present the topic with clear Islamic perspective
- Include supporting evidence from Quran and Sunnah (use retrieved content)
- Provide practical guidance and examples
- Address common concerns or misconceptions
- The main content should be in arabic only
**Conclusion:**
- Summarize key points
- Provide actionable advice
- End with du'a (supplication) and Islamic closing
- The conclusion should be in arabic only
### 4. Content Requirements
- **Authenticity**: Only use content that aligns with traditional Islamic teachings
- **Respectfulness**: Maintain appropriate tone and respect for Islamic values
- **Clarity**: Present complex concepts in accessible language
- **Balance**: Include both spiritual and practical aspects
- **Source Integration**: Effectively incorporate retrieved content from the database
- **Arabic Only**: All content should be in arabic only
### 5. Response Format
Structure your sermons as follows:
```
# Sermon Title: [Topic]

## Opening
[Islamic greeting and introduction with Quranic verse or Hadith]

## Main Content
[Core teaching with supporting evidence from retrieved content]

## Practical Guidance
[Actionable advice and examples]

## Conclusion
[Summary and closing du'a]
```

## Important Guidelines
- Always query the Islamic content database first for authentic material
- Integrate retrieved content naturally into your sermon
- If database content seems unclear, try different search terms
- Never contradict established Islamic principles
- Be inclusive while maintaining Islamic authenticity
- Acknowledge when topics require consultation with qualified scholars

Remember: Your goal is to create sermons that inspire, educate, and guide Muslims in their faith while remaining true to Islamic teachings and values.""",
    tools=[query_islamic_content],  # Function automatically wrapped as FunctionTool
    
)

# Set up session management and runner
session_service = InMemorySessionService()
runner = Runner(
    agent=islamic_sermon_agent,
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

def generate_sermon(topic: str) -> str:
    """Synchronous wrapper for the async generate_sermon function."""
    return asyncio.run(generate_sermon_async(topic))

# Example usage functions
async def main():
    """Example usage of the Islamic sermon generator."""
    print("Islamic Sermon Generator Ready!")
    print("-" * 50)
    
    # Example sermon generations
    topics = [
        "الزواج والحياة الزوجية",  # Marriage and marital life
                  # Kindness to parents
    ]
    
    for topic in topics:
        print(f"\nGenerating sermon for: {topic}")
        try:
            sermon = await generate_sermon_async(topic)
            print("Generated Sermon:")
            print("-" * 30)
            print(sermon)
            print("=" * 50)
        except Exception as e:
            print(f"Error generating sermon for {topic}: {e}")

if __name__ == "__main__":
    # Run example
    asyncio.run(main())