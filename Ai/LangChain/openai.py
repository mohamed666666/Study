from data import article
from schemas import Paragraph
from langchain_openai import ChatOpenAI
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.prompts import ChatPromptTemplate

import os
from getpass import getpass

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY") or getpass(
    "Enter OpenAI API Key: "
)

 # api_key="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"


llm = ChatOpenAI(temperature=0.0, model="gpt-4o-mini")

system_prompt = SystemMessagePromptTemplate.from_template(
    "You are an AI assistant that helps generate article titles."
)

# the user prompt is provided by the user, in this case however the only dynamic
# input is the article
user_prompt = HumanMessagePromptTemplate.from_template(
    """You are tasked with creating a name for a article.
The article is here for you to examine {article}

The name should be based of the context of the article.
Be creative, but make sure the names are clear, catchy,
and relevant to the theme of the article.

Only output the article name, no other explanation or
text can be provided.""",
    input_variables=["article"]
)

first_prompt = ChatPromptTemplate.from_messages([system_prompt, user_prompt])

chain_one = (
    {"article": lambda x: x["article"]}
    | first_prompt
    | llm
    | {"article_title": lambda x: x.content}
)

response = chain_one.invoke({"article": article})
print(response["article_title"])

structured_llm = llm.with_structured_output(Paragraph)