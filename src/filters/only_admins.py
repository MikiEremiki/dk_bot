from aiogram.filters import BaseFilter
from aiogram.types import Message


class OnlyAdminFilter(BaseFilter):
    def __init__(self, admins):
        self.admins = admins

    async def __call__(self, message: Message):
        if message.from_user.id in self.admins:
            return True
        return False
