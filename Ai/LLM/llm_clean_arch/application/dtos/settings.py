from pydantic import BaseModel
from typing import Optional, List, Any, Dict


class SettingsDTO(BaseModel):
    temperature: Optional[float] = 1.0
    max_tokens: Optional[int] = None
    top_p: Optional[float] = 1.0
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    stop: Optional[List[str]] = None
    extra: Optional[Dict[str, Any]] = {}