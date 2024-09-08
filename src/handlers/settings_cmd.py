from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

import states

settings_router = Router()


@settings_router.message(Command(commands='settings'))
async def cmd_settings(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(states.Settings.MAIN,
                               mode=StartMode.RESET_STACK)
