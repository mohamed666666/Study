from .interface import IOpenAiService
from langchain.llms import OpenAI
from llm_clean.domain.enums.models import AIModelType


class OpenAILangChainClient(IOpenAiService):
    def __init__(self, api_key: str, model_type:AIModelType):
        self.llm = OpenAI(openai_api_key=api_key)

    def get_response(self, prompt: str) -> str:
        
        return self.llm(prompt) 