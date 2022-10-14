import abc
import dataclasses
import typing
from typing import List
from dataclasses import dataclass

@dataclass
class QuestionData:
    service: typing.Optional[str]=None
    operation: typing.Optional[str]=None
    os: typing.Optional[str]=None
    version: typing.Optional[str]=None
    question: typing.Optional[str]=None

@dataclasses.dataclass
class AnswerData:
    id: str
    question: str
    answer: List[str]


class Properties:
    SERVICE = "service"
    OPERATION = "operation"
    OS = "os"
    VERSION = "version"
    QUESTION = "question"

class FAQService(abc.ABC):
    @abc.abstractmethod
    def get_answer(self, question: QuestionData) -> typing.Optional[List[AnswerData]]:
        pass
    def get_by_id(self, answer_id: str) -> AnswerData:
        pass
    def get_available_properties(self, current_data: QuestionData, property: str) -> typing.Optional[List[str]]:
        pass
