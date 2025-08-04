from .interface import IOpenAiService
import openai
from llm_clean.domain.enums.models import AIModelType
from llm_clean.application.dtos.prompt import PromptDTO

class OpenAIApiClient(IOpenAiService):
    
    def __init__(self, api_key: str, model_type: AIModelType,settings:dict):
        self.api_key = api_key
        self.model_type = model_type
        self.settings=settings
        openai.api_key = api_key

    def get_response(self, prompt: PromptDTO) -> str:
        model_mapping = {
            AIModelType.gpt_model: "gpt-4",
            AIModelType.gpt_4o_mini_model: "gpt-4o-mini"
        }
        
        model_name = model_mapping.get(self.model_type)
        if not model_name:
            raise ValueError(f"Unsupported model type: {self.model_type}")

        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[{"role": msg.role, "content": msg.content} for msg in prompt.messages],
            max_tokens=self.settings.get('max_tokens'),
            temperature=self.settings.get('temperature', 1.0),
            top_p=self.settings.get('top_p', 1.0),
            presence_penalty=self.settings.get('presence_penalty'),
            frequency_penalty=self.settings.get('frequency_penalty'),
            stop=self.settings.get('stop'),
            extra=self.settings.get('extra', {}))
        return response.choices[0].message.content.strip()