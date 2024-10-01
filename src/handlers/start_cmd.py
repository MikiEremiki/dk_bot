from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

import states

start_router = Router()


@start_router.message(CommandStart())
async def start_cmd(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(states.Main.MAIN,
                               mode=StartMode.RESET_STACK)
