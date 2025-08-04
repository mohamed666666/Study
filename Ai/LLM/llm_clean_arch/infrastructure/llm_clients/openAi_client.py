from llm_clean.application.interfaces.cleint import IClient

from llm_clean.infrastructure.llm_clients.openai_service.interface import IOpenAiService
from llm_clean.domain.entities.reponse import Response
from llm_clean.domain.enums.models import AIModelType
from llm_clean.application.dtos.prompt import PromptDTO


class OpenAiClient(IClient):
    def __init__(self, openai_service: IOpenAiService):
        self.openai_service = openai_service

    def invoke(self, prompt: PromptDTO) -> Response:
        # Use the injected openai_service instead of creating a new client
        response_text = self.openai_service.get_response(prompt)
        result = Response(txt=response_text, metadata={})  # Empty metadata since IOpenAiService doesn't provide usage info
        return result



