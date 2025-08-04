from langchain_ollama import ChatOllama
from .base_llm import AIBaseModel
from typing import Optional, Dict



class LocalLLM(AIBaseModel): 
    def __init__(
        self, model_url: str, model_name: str, model_args: Optional[Dict] = None
    ):
        super().__init__(model_name)
        kwargs = {
            "base_url": model_url,
            "model": model_name,
            "model_kwargs": {
                "num_beams": 1,
                "do_sample": True,
                "max_new_tokens": 256,
            },
            "num_ctx": 4096,
        }
        if model_args:
            kwargs.update(model_args)
        self.client = ChatOllama(**kwargs)

    # get_answer is inherited from AIBaseModel
