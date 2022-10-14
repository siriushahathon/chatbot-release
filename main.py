from backend.internal.db.db import DB
from backend.internal.db.parser import parse_faqs
from backend.internal.service.service_impl import FAQServiceImpl
from frontend.bot import Bot

DB_FILEPATH = "faq.json"
db = DB(parse_faqs(DB_FILEPATH))
service = FAQServiceImpl(db)
bot = Bot("5693177989:AAHFQ2WtmL4E2I_b_6WJFyQXfYpO2c_y2Vk", service)
bot.start()

