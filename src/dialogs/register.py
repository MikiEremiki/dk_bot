import re

from aiogram_dialog.widgets.text import Format

from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Window, Dialog, DialogManager
from aiogram_dialog.widgets.kbd import Cancel, Next, Button
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput

import states
from .custom_widgets.i18n_format import I18NFormat


def phone_type_check(text):
    text = re.sub(r'[-\s)(+]', '', text)
    text = re.sub(r'^[78]{,2}(?=9)', '', text)
    try:
        int(text)
    except ValueError:
        raise ValueError('Введено не число', text)
    if len(text) != 10:
        raise ValueError('Нет 10 цифр', text)
    elif text[0] != '9':
        raise ValueError('Начинается не с 9', text)
    else:
        return text


async def phone_error(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        error_: ValueError
):
    await message.answer(
        f'Вы ввели: {error_.args[1]}\n'
        f'{error_.args[0]}\n'
        f'Проверьте и повторите ввод'
    )


async def save_data_on_input(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        real_name: str
):
    session = dialog_manager.middleware_data['session']
    phone = dialog_manager.find('phone').get_value()

    await message.answer('Ok')


async def save_data_on_click(
        query: CallbackQuery,
        widget: Button,
        dialog_manager: DialogManager,
):
    session = dialog_manager.middleware_data['session']
    phone = dialog_manager.find('phone').get_value()
    user = dialog_manager.middleware_data['event_from_user']

    await query.answer('Ok')


async def get_tg_name(event_from_user, dialog_manager: DialogManager, **kwargs):
    return {'full_name': event_from_user.full_name}


register_dialog = Dialog(
    Window(
        I18NFormat('register-phone'),
        TextInput(
            'phone',
            phone_type_check,
            Next(),
            phone_error
        ),
        Cancel(I18NFormat('cancel')),
        state=states.Register.PHONE,
    ),
    Window(
        I18NFormat('register-full_tg_name'),
        Format('Если ФИ корректные, то нажмите подтвердить или'),
        I18NFormat('register-real_name'),
        TextInput(
            'real_name',
            str,
            save_data_on_input,
        ),
        Button(
            I18NFormat('confirm'),
            id='confirm',
            on_click=save_data_on_click,
        ),
        Cancel(I18NFormat('cancel')),
        state=states.Register.REAL_NAME,
        getter=get_tg_name,
    ),
)
