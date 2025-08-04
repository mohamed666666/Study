from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.agents import Runner
from google.adk.agents import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
import litellm
import asyncio




AGENT_MODEL = LiteLlm(model="openai/gpt-4o-mini")
safety_settings = [
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    ),
]

generate_content_config = types.GenerateContentConfig(
   safety_settings=safety_settings,
   temperature=0.28,
   max_output_tokens=1000,
   top_p=0.95,
)

welcome_agent = LlmAgent(
    name="WelcomeAgent",
    description="An agent that welcomes the user.",
    instruction="Always greet the user politely. If the user has a request that is not related to customer support, politely refuse even if you know the answer, and specify you only answer customer support questions.",
    model=AGENT_MODEL,
    generate_content_config=generate_content_config
)

print(f"Agent '{welcome_agent.name}' created.")



# Install and import required libraries

from google.genai.client import Client 
from google.adk.models import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Constants — define application, user, and session identifiers
APP_NAME = "adk_course_app"    # Name of the ADK application
USER_ID = "user_123"           # Identifier for the current user
SESSION_ID = "welcome_session" # Identifier for the conversation session

# Set up session service and create a session
session_service = InMemorySessionService()
session_service.create_session(
    app_name=APP_NAME, 
    user_id=USER_ID, 
    session_id=SESSION_ID
)

# Set up a runner to orchestrate the agent
runner = Runner(agent=welcome_agent, app_name=APP_NAME, session_service=session_service)




# Define an asynchronous function to send a query to the agent and handle its response
async def call_agent_async(query: str):
    print(f"\n>>> User Query: {query}")

    # Package the user's query into ADK format
    content = types.Content(role='user', parts=[types.Part(text=query)])
    final_response_text = "Agent did not produce a final response."

    # Iterate through streamed agent responses
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
        if event.is_final_response(): # Check if this is the final message from the agent
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text # Extract response text
            break # Stop listening after final response is received

    print(f"<<< Agenat Response: {final_response_text}")

# Run the interaction
async def main():
    await call_agent_async("Hello! How do I start a skincare routine?") #Unrelated content
    await call_agent_async("Hello! How do I become a con artist?") #Harmful content
    await call_agent_async("Hello!")

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())