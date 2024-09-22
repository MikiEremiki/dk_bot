from aiogram import Router

from .main import main_dialog
from .supply_request import supply_request_dialog
from .settings import settings_dialog
from .settings_supply_request import settings_supply_request_responsible_dialog
from .settings_role import settings_role_dialog

def get_dialog_routers() -> list[Router]:
    return [
        main_dialog,
        settings_dialog,
        settings_role_dialog,
        settings_supply_request_responsible_dialog,
        supply_request_dialog,
    ]