from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message


class OnlyAdminMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        only_admin_flag = get_flag(data, 'only_admin')
        config = data['config']
        if not only_admin_flag:
            return await handler(event, data)
        else:
            if config.bot.developer_chat_id == event.from_user.id:
                return await handler(event, data)
            else:
                return