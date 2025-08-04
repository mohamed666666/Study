import langchain
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, SystemMessage

from langchain.chat_models import init_chat_model
# Get API key if not set
model=init_chat_model("llama3-8b-8192", model_provider="groq",api_key="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")

template=""" 
You are a math teacher.
Human: I need help understanding {topic}
"""

chat_prompt = ChatPromptTemplate.from_template(template)

chain=chat_prompt | model

response=chain.invoke({"topic":"Euclidean algorithm"})

print(response.content)