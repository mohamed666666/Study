from pydantic import BaseModel
from typing import Optional, Type, Dict, Any


# Prompt Schema 
class PromptSchema(BaseModel):
    system_template: Optional[str] = None
    human_template: Optional[str] = None
    pydantic_model: Optional[Type[BaseModel]] = None
    template_params: Dict[str, Any] = {}
    llm_model: Any = None


# Response Schema
class ResponseSchema(BaseModel):
    response: Dict[str, Any]
    metadata: Dict[str, Any]
