from aiogram import Router

from filters import OnlyAdminFilter

from .supply_request_cmd import supply_request_router
from .start_cmd import start_router
from .settings_cmd import settings_router
from .echo_cmd import echo_router


def get_routers(config) -> list[Router]:
    settings_router.message.filter(
        OnlyAdminFilter([config.bot.developer_chat_id]))
    return [
        start_router,
        settings_router,
        supply_request_router,
        echo_router,
    ]
