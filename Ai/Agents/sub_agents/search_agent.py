from google.adk.tools import google_search
from google.adk.agents import LlmAgent




search_agent = LlmAgent(
    model="gemini-2.0-flash-exp",
    name="search_agent",
    description="searching for quranic ayat and hadiths related to the key words from the summary_agent",
    instruction="You are a helpful assistant that can serach for quranic ayat and hadiths related to the key words from the summary_agent",
    tools=[google_search],
)





