import logging

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ReplyKeyboardRemove
from aiogram_dialog import DialogManager, StartMode, ShowMode

import states


async def on_unknown_intent(event, dialog_manager: DialogManager):
    logging.error('Restarting dialog: %s', event.exception)
    if event.update.callback_query:
        await event.update.callback_query.answer(
            'Bot process was restarted due to maintenance.\n'
            'Redirecting to main menu.',
        )
        if event.update.callback_query.message:
            try:
                await event.update.callback_query.message.delete()
            except TelegramBadRequest:
                pass  # whatever
    elif event.update.message:
        await event.update.message.answer(
            'Bot process was restarted due to maintenance.\n'
            'Redirecting to main menu.',
            reply_markup=ReplyKeyboardRemove(),
        )
    await dialog_manager.start(
        states.Main.MAIN,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.SEND,
    )


async def on_unknown_state(event, dialog_manager: DialogManager):
    logging.error('Restarting dialog: %s', event.exception)
    answer_msg = (
        'Bot process was restarted due to maintenance.\n'
        'Redirecting to main menu.'
    )
    if event.update.callback_query:
        await event.update.callback_query.answer(answer_msg)
        if event.update.callback_query.message:
            try:
                await event.update.callback_query.message.delete()
            except TelegramBadRequest:
                pass  # whatever
    elif event.update.message:
        await event.update.message.answer(
            answer_msg,
            reply_markup=ReplyKeyboardRemove(),
        )
    await dialog_manager.start(
        states.Main.MAIN,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.SEND,
    )