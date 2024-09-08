from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

import states

supply_request_router = Router()


@supply_request_router.message(Command(commands='supply_request'))
async def supply_request_cmd(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(states.SupplyRequest.START,
                               mode=StartMode.RESET_STACK)
