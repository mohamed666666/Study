from llm_clean.application.interfaces.cleint import IClient
from llm_clean.infrastructure.llm_clients.openAi_client import OpenAiClient
from llm_clean.domain.enums.models import AIModelType
from llm_clean.application.usecases.answer import AnswerUsecase
from llm_clean.application.dtos.settings import SettingsDTO
from typing import List
from llm_clean.infrastructure.llm_clients.openai_service.interface import IOpenAiService
from llm_clean.infrastructure.llm_clients.openai_service.openai_API_client import OpenAIApiClient
from llm_clean.application.dtos.prompt import PromptDTO
from llm_clean.application.dtos.message import MessageDTO
from typing import Dict,Any

def get_api_service(model_type:AIModelType,settings:dict)->IOpenAiService:
    return OpenAIApiClient(
        api_key="sk-proj-zBp78OALhQG_RPJv2Y_e60j27DkgUnxft8Dto2_NaVOogkz",
        model_type=model_type,
        settings=settings)

def get_llm_client(model_type:AIModelType,settings:dict)->IClient:
    cleint=get_api_service(model_type=model_type ,settings=settings)
    return OpenAiClient(openai_service=cleint )



class Prompt:
    def __init__(self, prompt: str,history:List['Prompt']=[None],role:str="user"):
        self.prompt = prompt
        self.history = history
        self.role = role

    def get_prompt(self):        
        return self.prompt
    
    def _convert_to_dto(self):
        messages = []
        # Add current prompt as a message
        messages.append(MessageDTO(content=self.prompt, role=self.role))
        
        # Add history messages if they exist
        if self.history and self.history[0] is not None:
            for prompt in self.history:
                messages.append(MessageDTO(content=prompt.get_prompt(), role=prompt.role))
        
        return PromptDTO(messages=messages)
        
        
        
class settings:
    def __init__(self,temperature:float,max_tokens:int,top_p:float,presence_penalty:float,frequency_penalty:float,stop:List[str],extra:Dict[str,Any]):
        self.temperature=temperature
        self.max_tokens=max_tokens
        self.top_p=top_p
        self.presence_penalty=presence_penalty
        self.frequency_penalty=frequency_penalty
        self.stop=stop
        self.extra=extra

class LLM:
    def __init__(self, model_type: AIModelType,settings:settings):
        """
        Initialize the LLM interface with the model type and the llm client.
        
        Functionality:
            - Initializes the language model client with specified model type
            - Provides a standardized interface for generating responses
            - Abstracts the complexity of direct model interaction
            - Supports dependency injection for flexible client implementation
        
        Example usage:
            ```python
            llm = LLM(model_type=AIModelType.GPT4)
            response = llm.get_response()
            ```
                
        """
        self.settings=settings
        self.llm_client = get_llm_client(model_type=model_type,settings=self.settings.__dict__)
        self.answer_usecase = AnswerUsecase(client=self.llm_client)
        

    def get_response(self ,prompt:Prompt):
        input_prompt = prompt._convert_to_dto()
        response = self.answer_usecase.execute(prompt_request=input_prompt)
        return response

    
    
