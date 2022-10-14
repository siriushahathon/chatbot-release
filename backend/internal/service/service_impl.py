import random
from typing import List, Optional

from backend.interface import FAQService, QuestionData, AnswerData
from backend.internal.db import db
from backend.internal.db.model import FAQModel
import ru_core_news_lg


class FAQServiceImpl(FAQService):
    def __init__(self, db_handle: db.DB):
        self._db = db_handle
        self._nlp = ru_core_news_lg.load()

    def _check_requirements(faq: FAQModel, question: QuestionData):
        return not (question.service and faq.service != question.service or
                question.operation and faq.operation != question.operation or
                question.os and faq.os != question.os or
                question.version and faq.version != question.version)

    def get_by_id(self, answer_id: str) -> AnswerData:
        for faq in self._db.get_faqs():
            if faq.id == answer_id:
                return AnswerData(id=faq.id, answer=faq.steps, question=faq.question)

    def get_answer(self, question: QuestionData) -> Optional[List[AnswerData]]:
        faqs = self._db.get_faqs()
        question_nlp = self._nlp(question.question)
        rating = []
        handled = []
        for i, faq in enumerate(faqs):
            if not FAQServiceImpl._check_requirements(faq, question) or faq.question in handled:
                continue
            ratio = question_nlp.similarity(self._nlp(faq.question))
            rating.append((ratio, i))
            handled.append(faq.question)
        rating.sort(reverse=True)
        return [AnswerData(id=faqs[i].id, question=faqs[i].question, answer=faqs[i].steps) for _, i in rating][:5]



    def get_available_properties(self, q: QuestionData, property) -> Optional[List[str]]:
        props = set()
        for faq in self._db.get_faqs():
            if FAQServiceImpl._check_requirements(faq, q):# and self._get_ratio(faq.question, q.question) > 0.5:
                props.add(faq.__getattribute__(property))
        return sorted(list(props))



