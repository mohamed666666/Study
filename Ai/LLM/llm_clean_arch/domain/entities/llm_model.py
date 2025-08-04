from dataclasses import dataclass
from uuid import UUID

@dataclass
class LLMModel:
    model_id: UUID
    model_name: str
    model_type: str