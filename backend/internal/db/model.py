import dataclasses
from typing import List

@dataclasses.dataclass
class FAQModel:
    id: str
    service: str
    operation: str
    os: str
    version: str
    question: str
    steps: List[str]
