from typing import List

from backend.internal.db.model import FAQModel


class DB:
    def __init__(self, faqs: List[FAQModel]):
        self._faqs = faqs
    def get_faqs(self) -> List[FAQModel]:
        return self._faqs
