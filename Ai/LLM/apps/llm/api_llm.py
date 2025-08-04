from langchain_openai import ChatOpenAI
from .base_llm import BaseLLM
from typing import Optional, Dict
 


class ApiLLM(BaseLLM):
    def __init__(
        self, model_api_key: str, model_name: str, model_args: Optional[Dict] = None
    ):
        super().__init__(model_name)
        model_args = model_args or {}
        self.client = ChatOpenAI(
            api_key=model_api_key,
            model=model_name,
            temperature=1,
            top_p=1,
            model_kwargs={"response_format": {"type": "json_object"}},
            **model_args,
        )

    # get_answer is inherited from AIBaseModel
