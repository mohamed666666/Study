from abc import ABC, abstractmethod

class IOpenAiService(ABC):
    @abstractmethod
    def get_response(self) -> str:
        pass 