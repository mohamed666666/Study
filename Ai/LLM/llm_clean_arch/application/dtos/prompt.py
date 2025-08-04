from pydantic import BaseModel
from llm_clean.application.dtos.message import MessageDTO
from typing import Optional, List, Any, Dict



class PromptDTO(BaseModel):
    messages: List[MessageDTO]
