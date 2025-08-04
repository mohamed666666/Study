from pydantic import BaseModel
from typing import Dict
class Response(BaseModel):
    txt: str
    metadata: Dict
