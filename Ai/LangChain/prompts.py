from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
import os
import getpass
from langchain.chat_models import init_chat_model
# Get API key if not set
model=init_chat_model("llama3-8b-8192", model_provider="groq",api_key="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")

template=""" 
You are a math teacher.
Human: I need help understanding {topic}
"""

# Define the chat template properly
chat_prompt = ChatPromptTemplate.from_template(template)

# Prepare variables for prompt
variables = {
    "topic": "Euclidean algorithm"
}

# Generate formatted messages
messages = chat_prompt.format_messages(**variables)

# Get response from model
response = model.invoke(messages)

print("\nAI Response:", response.content)









