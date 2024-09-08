from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from fluentogram import TranslatorRunner

start_router = Router()


@start_router.message(CommandStart())
async def start_cmd(message: Message,
                    i18n: TranslatorRunner):
    await message.answer(
        i18n.get('start', username=message.from_user.full_name)
    )
