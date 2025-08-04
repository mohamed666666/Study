from pydantic import BaseModel

class MessageDTO(BaseModel):
    # Define the fields that represent your Message entity.
    role: str
    content: str