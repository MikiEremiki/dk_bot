import logging
import operator

from aiogram.types import CallbackQuery
from aiogram_dialog import Window, Dialog, DialogManager, ShowMode
from aiogram_dialog.widgets.common import sync_scroll
from aiogram_dialog.widgets.kbd import (
    Cancel, Select, Group, Back, ScrollingGroup
)
from aiogram_dialog.widgets.text import Format, List

import states
from db.enum import UserRole
from db.requests import get_all_users, update_role
from .custom_widgets.i18n_format import I18NFormat

logger = logging.getLogger('settings_role')


async def get_users(dialog_manager: DialogManager, **kwargs):
    session = dialog_manager.middleware_data['session']
    users = await get_all_users(session)
    users = [(user.last_name, user.user_id, user.role.value) for user in users]
    return {'users': users}


async def get_roles(dialog_manager: DialogManager, **kwargs):
    roles = [(role.value, role.name) for role in UserRole]
    return {'roles': roles}


async def click_get_user(
        callback: CallbackQuery,
        select: Select,
        dialog_manager: DialogManager,
        item_id: str
) -> None:
    dialog_manager.dialog_data['user_id'] = item_id
    await dialog_manager.next()


async def update_user_role(
        callback: CallbackQuery,
        widget: Select,
        dialog_manager: DialogManager,
        new_role: str
):
    new_role = UserRole[new_role]

    session = dialog_manager.middleware_data['session']
    user_id = int(dialog_manager.dialog_data['user_id'])
    await update_role(session, user_id, new_role)

    await callback.message.answer(
        f'Роль пользователя обновлена на {new_role.value}.')
    await dialog_manager.done(show_mode=ShowMode.DELETE_AND_SEND)

select_user_w = Window(
        I18NFormat('settings-role-user-info'),
        List(
            Format('{pos}. {item[0]}: {item[2]}'),
            items='users',
            id='user_scroll',
            page_size=8
        ),
        ScrollingGroup(
            Select(
                Format('{item[0]}'),
                id='user_get',
                item_id_getter=operator.itemgetter(1),
                items='users',
                on_click=click_get_user
            ),
            id='user_select',
            width=1,
            height=8,
            hide_on_single_page=True,
            on_page_changed=sync_scroll('user_scroll')
        ),
        Cancel(I18NFormat('cancel')),
        state=states.RoleSettings.SELECT_USER,
        getter=get_users,
    )
select_role_w = Window(
        I18NFormat('settings-role-change-info'),
        Group(
            Select(
                text=Format('{item[0]}'),
                id='role_select',
                item_id_getter=operator.itemgetter(1),
                items='roles',
                on_click=update_user_role,
            ),
            width=2
        ),
        Back(I18NFormat('back')),
        state=states.RoleSettings.SELECT_ROLE,
        getter=get_roles,
    )

settings_role_dialog = Dialog(
    select_user_w,
    select_role_w,
)
