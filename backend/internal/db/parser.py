import codecs
import json
from typing import List

import typing

from backend.internal.db.model import FAQModel


def parse_faqs(filepath: str) -> List[FAQModel]:
    json_content = _load_faq(filepath)
    return _parse_faqs(json_content)#[:200]


def _load_faq(filepath: str) -> typing.Dict:
    with open(filepath, 'r', encoding="utf-8-sig") as file:
        return json.load(file)

def _parse_faqs(json: typing.Dict) -> List[FAQModel]:
    data = json["Data"]
    return [_parse_faq(faq) for faq in data]

def _parse_faq(faq: typing.Dict) -> FAQModel:
    return FAQModel(
        id=faq["ID"],
        service=faq["Service"],
        operation=faq.get("Operation", ""),
        os="Web" if faq["FrontChannel"] == "ИБ" else faq.get("OS", "All"),
        version=faq.get("Version", ""),
        question=faq["Question"],
        steps=_parse_steps(faq),
    )

def _parse_steps(faq: typing.Dict) -> List[str]:
    steps = []
    i = 1
    while True:
        step = faq.get("Step"+str(i), "")
        if not step:
            return steps
        steps += [step]
        i += 1


