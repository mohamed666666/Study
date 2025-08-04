from .enums import AIModelType
from apps.llm.api_llm import ApiLLM
from typing import Optional, Dict
from config import config

 
class LLMFactory:
    @staticmethod
    def get_ai_model(model_type: str, model_args: Optional[Dict] = None):
        model_args = model_args or {}
        models = {
            AIModelType.gpt_model.value: ApiLLM(
                model_name="gpt-4o",
                model_api_key=config.OPENAI_API_KEY,
                model_args=model_args,
            ),
            AIModelType.gpt_4o_mini_model.value: ApiLLM(
                model_name="gpt-4o-mini",
                model_api_key=config.OPENAI_API_KEY,
                model_args=model_args,
            ),
        }
        if model_type not in models:
            raise ValueError(f"Unknown model type: {model_type}")
        return models[model_type]
