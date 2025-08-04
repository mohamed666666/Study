from dataclasses import dataclass
from enum import Enum
from typing import List

class PromptRole(str, Enum):
    system = "system"
    user = "user"
    assistant = "assistant"
    

class Message:
    role: PromptRole
    content: str
    
    def __init__(self, role: PromptRole, content: str):
        self.role = role
        self.content = content
