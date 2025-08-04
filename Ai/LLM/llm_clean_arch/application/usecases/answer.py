from llm_clean.application.interfaces.cleint import IClient
from llm_clean.application.dtos.prompt import PromptDTO
from llm_clean.domain.entities.prompt import Prompt
from llm_clean.application.dtos.respose import Response
from llm_clean.domain.entities.message import Message

class AnswerUsecase:
    def __init__(self, client: IClient):
        self.client = client

    def execute(self, prompt_request: PromptDTO) -> Response:
        prompt = Prompt()
        prompt.messages = [Message(role=message.role, content=message.content) for message in prompt_request.messages]
        response = self.client.invoke(prompt)
        return Response(txt=response.txt, metadata=response.metadata)
