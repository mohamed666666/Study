

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.tools import FunctionTool
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents import LlmAgent
import litellm



# Constants — define application, user, and session identifiers
APP_NAME      = "adk_course_app"
USER_ID       = "user_123"
SESSION_ID    = "support_session"

# FAQ knowledge base & tool 
FAQ_DATA = {
    "return policy": "You can return items within 30 days of purchase.",
    "hours": "Our support team is available from 9 am to 5 pm, Monday to Friday.",
    "contact": "You can reach support at help@example.com."
}

def lookup_faq(question: str) -> str:
    faq_text = "\n".join(f"- {k}: {v}" for k, v in FAQ_DATA.items())
    prompt = (
        f"You are a helpful assistant. Here is a list of FAQs:\n\n{faq_text}\n\n"
        f"User question: \"{question}\". "
        f"Reply with the best match or say you don't know."
    )
    response = litellm.completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"].strip()

faq_tool  = FunctionTool(func=lookup_faq)

AGENT_MODEL = LiteLlm(model="openai/gpt-4o-mini")
# Specialist Agents
greeting_agent = LlmAgent(
    name="GreetingAgent",
    description="Handles greetings from users.",
    instruction="Respond cheerfully when the user says hello.",
    model=AGENT_MODEL
)

account_agent = LlmAgent(
    name="AccountAgent",
    description="Handles questions about login issues or account access.",
    instruction="Help users who are having trouble logging in or accessing their account.",
    model=AGENT_MODEL
)

faq_agent = LlmAgent(
    name="FAQAgent",
    description="Answers common questions using the FAQ knowledge base.",
    instruction="Use the FAQ tool to answer questions that match the FAQs.",
    model=AGENT_MODEL,
    tools=[faq_tool]
)

# Root agent with delegation logic
root_agent = LlmAgent(
    name="SupportRootAgent",
    description="Delegates to specialized sub-agents for support queries.",
    instruction=(
        "If the user greets you, delegate to GreetingAgent.\n"
        "If the user has an account or login issue, delegate to AccountAgent.\n"
        "If the question matches a known FAQ topic (e.g., returns, hours, contact), "
        "delegate to FAQAgent. Do not answer as the FAQAgent if the topic doesn't match any of the FAQs.\n"
        "Otherwise, answer directly as best you (the Root Agent) can."
    ),
    model=AGENT_MODEL,
    sub_agents=[greeting_agent,faq_agent,account_agent]
)


