from backend.interface import FAQService
from backend.internal.db.db import DB
from backend.internal.db.parser import parse_faqs
from backend.internal.service.service_impl import FAQServiceImpl


def initialize(db_filepath: str) -> FAQService:
    db_handle = DB(parse_faqs(db_filepath))
    return FAQServiceImpl(db_handle)