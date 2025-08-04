from abc import ABC
from apps.utils.token_counter import calculate_token_usage
from apps.llm.prompt_builder import PromptBuilder
from apps.llm.schema import PromptSchema, ResponseSchema
import json
from apps.utils.logging import error_logger, app_logger

 
class BaseLLM(ABC):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.prompt_builder = PromptBuilder()
        self.client = None

    def get_token_usage(self, prompt: str, response_content: str) -> dict:
        return calculate_token_usage(
            prompt=prompt, response=response_content, model_name=self.model_name
        )

    def get_answer(
        self,
        prompt_schema: PromptSchema,
    ):
        try:
            prompt_schema.llm_model = self.client
            prompt = self.prompt_builder.generate_prompt(prompt_schema=prompt_schema)
            response = self.client.invoke(prompt)
            content = response.content
            # app_logger.info(f"Response: {content}")
            metadata = self.get_token_usage(prompt=prompt, response_content=content)
            # app_logger.info(f"Metadata: {metadata}")
            try:
                if isinstance(content, str):
                    content = json.loads(content)
                return ResponseSchema(response=content, metadata=metadata)
            except json.JSONDecodeError as e:
                error_logger.error(f"Failed to parse JSON response: {e}")
                raise Exception("Invalid JSON response from model")
        except Exception as e:
            error_logger.error(f"Error fetching result from {self.model_name}: {e}")
            raise Exception(f"Error fetching result from {self.model_name}")
