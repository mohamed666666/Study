from dataclasses import dataclass
from typing import Dict, Any




class Response:
    response: Dict[str, Any]
    metadata: Dict[str, Any]