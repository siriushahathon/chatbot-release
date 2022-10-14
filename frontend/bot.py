#!/usr/bin/env python
# pylint: disable=C0116,W0613
import dataclasses
import logging
from typing import List, Text

import telegram
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext, CallbackQueryHandler,
)

from backend.interface import FAQService, QuestionData, Properties, AnswerData
from backend.internal.service import speech_rec
from frontend.display import Text

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

class State:
    START, QUESTION, SERVICE, OPERATION, OS, VERSION = range(6)

@dataclasses.dataclass
class QuizState:
    next_state: int
    text: str
    property: str


states = {
    State.QUESTION: QuizState(State.SERVICE, "", Properties.QUESTION),
    State.SERVICE: QuizState(State.OPERATION, Text.CHOOSE_SERVICE, Properties.SERVICE),
    State.OPERATION: QuizState(State.OS, Text.CHOOSE_OPERATION, Properties.OPERATION),
    State.OS: QuizState(State.VERSION, Text.CHOOSE_OS, Properties.OS),
    State.VERSION: QuizState(ConversationHandler.END, Text.CHOOSE_VERSION, Properties.VERSION),
}


QUESTION_DATA_KEY = "question"
CLARIFY_DATA = "clarify"
ANOTHER_QUESTION_DATA = "another"

class Bot:
    def __init__(self, token: str, service: FAQService):
        self._token = token
        self._service = service

    def _another_question_markup(self):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(Text.ANOTHER_QUESTION, callback_data=ANOTHER_QUESTION_DATA)]
        ])

    def _get_keyboard(self, options: List[str]) -> ReplyKeyboardMarkup:
        keyboard = [[option] for option in options]
        return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    # TODO: bugs related to showing empty buttons
    def _show_output_for_state(self, update, context, state_id: int):
        if state_id == ConversationHandler.END:
            self._show_end(update, context)
            return
        state = states[state_id]

        options = self._service.get_available_properties(context.user_data[QUESTION_DATA_KEY], state.property)
        if not options or not options[0]:
            return self._show_output_for_state(update, context, state.next_state)
        keyboard = self._get_keyboard(options)
        update.message.reply_text(state.text, reply_markup=keyboard)
        return state.next_state

    def _update_attr(self, context, attr, new_val):
        if not QUESTION_DATA_KEY in context.user_data:
            context.user_data[QUESTION_DATA_KEY] = QuestionData()
        setattr(context.user_data[QUESTION_DATA_KEY], attr, new_val)

    def _base_handler_for_state(self, state_id: int):
        def handler(update, context) -> int:
            state = states[state_id]

            data = update.message.text
            if state_id == State.QUESTION:
                if update.message.voice:
                    data = speech_rec.convert_to_text(update.message.voice.get_file().download_as_bytearray())
                    update.message.reply_text(data)
                self._clear_question_data(context)
            self._update_attr(context, state.property, data)

            message = update.message.reply_text(Text.PROCESSING)
            answers = self._service.get_answer(question=context.user_data[QUESTION_DATA_KEY])
            keyboard = [[InlineKeyboardButton(answer.question, callback_data=answer.id)] for answer in answers]
            keyboard += [[InlineKeyboardButton(Text.CLARIFY_TEXT, callback_data=CLARIFY_DATA+str(state_id))]]
            markup = InlineKeyboardMarkup(keyboard)
            message.edit_text(Text.PRE_DATA, reply_markup=markup)

            return ConversationHandler.END


        return handler
    def _keyboard_query_handler(self, update: Update, context: CallbackContext) -> int:
        query = update.callback_query
        update.message = query.message
        query.answer()
        data = str(query.data)
        if data.startswith(CLARIFY_DATA):
            query.message.delete()
            current_state = int(data.removeprefix(CLARIFY_DATA))
            self._show_output_for_state(update, context, states[current_state].next_state)
            return states[current_state].next_state
        elif data == ANOTHER_QUESTION_DATA:
            state = self._start_handler(update, context)
            query.message.delete()
            return state
        else:
            answer = self._service.get_by_id(data)
            self._display_answer(update, answer)
            return ConversationHandler.END

    def _display_answer(self, update: Update, answer: AnswerData):
        text = "<b>" + answer.question + "</b>\n"
        add_indices = not answer.answer[0][0].isdigit()
        for i, step in enumerate(answer.answer):
            text += "<i><b>" + str(i+1) + ". </b></i>" if add_indices else ""
            text += step + "\n"
        text = text.replace("\n\n", "\n")
        markup = self._another_question_markup()
        update.callback_query.edit_message_text(text, parse_mode=telegram.ParseMode.HTML, reply_markup=markup)

    def _start_handler(self, update: Update, context: CallbackContext) -> int:
        update.message.reply_text(Text.GREETING)
        return State.QUESTION
    def _clear_question_data(self, context: CallbackContext):
        context.user_data[QUESTION_DATA_KEY] = QuestionData()

    def _show_end(self, update,context) -> int:
        update.message.reply_text(Text.NOT_FOUND, reply_markup=self._another_question_markup())
        return ConversationHandler.END

    def start(self) -> None:
        updater = Updater(self._token)
        dispatcher = updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self._keyboard_query_handler),
                CommandHandler('start', self._start_handler),
                MessageHandler(Filters.text | Filters.voice, self._base_handler_for_state(State.QUESTION)),
            ],
            states={
                state: [
                    MessageHandler(
                        (Filters.text | Filters.voice) if state == State.QUESTION else Filters.text & ~Filters.command ,
                        self._base_handler_for_state(state)
                    ),
                    CommandHandler('start', self._start_handler),
                ] for state in range(6)
            },
            fallbacks=[],
        )
        dispatcher.add_handler(conv_handler)
        updater.start_polling()
        updater.idle()