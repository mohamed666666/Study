from abc import ABC, abstractmethod
from llm_clean.domain.entities.prompt import Prompt
from llm_clean.domain.entities.reponse import Response

class IClient(ABC):
    @abstractmethod
    def invoke(self, prompt: Prompt) -> Response:
        pass

    
    
