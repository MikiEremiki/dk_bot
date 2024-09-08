import logging

import msgpack

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Window, Dialog, DialogManager, StartMode
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import (
    Start, Cancel, Back, Group, Button, SwitchTo
)
from aiogram_dialog.widgets.text import Format, List, Const
from nats.js.errors import KeyNotFoundError

import states
from .custom_widgets.i18n_format import I18NFormat
from utils.faststream_connect import get_kv_from_dialog_manager

logger = logging.getLogger('settings_supply_request')


async def get_responsible(dialog_manager: DialogManager, **kwargs):
    key_value = await get_kv_from_dialog_manager(dialog_manager)
    responsible = []
    key = 'supply_request-responsible'
    try:
        entity = await key_value.get(key)
        res = msgpack.unpackb(entity.value)
    except KeyNotFoundError as e:
        logger.error(e)
        res = []
    for i, v in enumerate(res, start=1):
        responsible.append((v, str(i)))

    dialog_manager.dialog_data['responsible'] = responsible
    return {'responsible': responsible}


async def click_confirm(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
) -> None:
    i18n = dialog_manager.middleware_data.get('i18n')
    await callback.answer(i18n.get('apply'))
    await dialog_manager.done()


async def add_responsible(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        input_data: str
):
    i18n = dialog_manager.middleware_data.get('i18n')
    if ' ' in message.text:
        cmd, name = message.text.split(maxsplit=1)
        key_value = await get_kv_from_dialog_manager(dialog_manager)
        key = 'supply_request-responsible'
        try:
            entity = await key_value.get(key)
            res = msgpack.unpackb(entity.value)
        except KeyNotFoundError as e:
            logger.error(e)
            res = []
        match cmd:
            case 'Добавить':
                res.append(name)
            case 'Удалить':
                try:
                    res.remove(name)
                except ValueError:
                    await message.answer(
                        i18n.get(
                            'settings-supply_request-responsible-correct_name',
                            name=name)
                    )
            case _:
                await message.answer(
                    i18n.get('settings-supply_request-responsible-correct_cmd',
                             cmd=cmd) + '\n' +
                    i18n.get('settings-supply_request-responsible-help')
                )
        await key_value.put(key,
                            msgpack.packb(res))
    else:
        await message.answer(
            i18n.get('settings-supply_request-responsible-help')
        )


settings_supply_request_responsible_dialog = Dialog(
    Window(
        I18NFormat('settings-supply_request-info'),
        SwitchTo(
            text=I18NFormat('settings-supply_request-responsible'),
            id='settings_supply_request_responsible',
            state=states.SupplyRequestSettings.RESPONSIBLE,
        ),
        Cancel(I18NFormat('back')),
        state=states.SupplyRequestSettings.START,
    ),
    Window(
        I18NFormat('settings-supply_request-responsible-info'),
        Const(' '),
        I18NFormat('settings-supply_request-responsible-help'),
        Const(' '),
        I18NFormat('settings-supply_request-responsible-current_list',
                   when='responsible'),
        List(
            Format(' + {item[0]}'),
            items='responsible',
            id='responsible',
        ),
        Button(I18NFormat('confirm'),
               id='confirm',
               on_click=click_confirm),
        Group(
            Back(I18NFormat('back')),
            Start(I18NFormat('cancel'),
                  id='cancel',
                  state=states.Settings.MAIN,
                  mode=StartMode.RESET_STACK),
            width=2
        ),
        TextInput(
            id='add_responsible',
            on_success=add_responsible,
        ),
        state=states.SupplyRequestSettings.RESPONSIBLE,
        getter=get_responsible,
    ),
)
