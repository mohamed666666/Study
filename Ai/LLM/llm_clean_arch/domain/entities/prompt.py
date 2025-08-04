from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from llm_clean.domain.entities.message import Message


class PromptSettings:
    temperature: Optional[float] = 1.0
    max_tokens: Optional[int] = None
    top_p: Optional[float] = 1.0
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    stop: Optional[List[str]] = None
    # You can include any extra custom settings that might be needed by a particular provider.
    extra: Optional[Dict[str, Any]] = {}

class Prompt:
    messages: List[Message]
    settings: Optional[PromptSettings] = None

