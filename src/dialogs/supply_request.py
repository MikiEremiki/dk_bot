import logging
import operator

import msgpack
from nats.js.errors import KeyNotFoundError

from aiogram import F, Bot
from aiogram.types import ContentType, Message
from aiogram.types import CallbackQuery

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import (
    Button, Cancel, Multiselect, Group, Back, Next, ScrollingGroup, Select,
    SwitchTo
)
from aiogram_dialog.widgets.input import (
    MessageInput, TextInput, ManagedTextInput
)
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Format, List, Const

import states
from db import SupplyRequest
from db.requests import (
    create_supply_request,
    attach_supply_request_to_user,
    get_supply_request_by_user,
)
from .custom_widgets.i18n_format import I18NFormat
from utils.faststream_connect import get_kv_from_dialog_manager

logger = logging.getLogger('supply_request')


async def click_supply_request_edit(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
) -> None:
    # i18n: TranslatorRunner = dialog_manager.middleware_data.get('i18n')
    # await callback.answer(text=i18n.get('purchase_create'))
    print()
    pass


async def click_supply_request_get(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
) -> None:
    session = dialog_manager.middleware_data['session']
    event_from_user = dialog_manager.middleware_data['event_from_user']
    res = await get_supply_request_by_user(session, event_from_user.id)
    dialog_manager.dialog_data['supply_requests'] = [item.id for item in res]

    await dialog_manager.switch_to(states.SupplyRequest.GET_REQUESTS)


async def click_get_supply_request(
        callback: CallbackQuery,
        select: Select,
        dialog_manager: DialogManager,
        item_id: str
) -> None:
    dialog_manager.dialog_data['supply_request_id'] = item_id
    await dialog_manager.next()


async def media_handler(
        message: Message,
        message_input: MessageInput,
        dialog_manager: DialogManager,
):
    media_file_id = ''
    if message.document:
        media_file_id = message.document.file_id
    elif message.photo:
        media_file_id = message.photo[0].file_id
    dialog_manager.dialog_data['media_file_id'] = media_file_id
    dialog_manager.dialog_data['media_content_type'] = message.content_type
    i18n = dialog_manager.middleware_data.get('i18n')
    await message.answer(i18n.get('supply_request-document-apply'))
    await dialog_manager.next()


async def get_supply_request(
        message: Message,
        widget: ManagedTextInput[int],
        dialog_manager: DialogManager,
        value: int
):
    session = dialog_manager.middleware_data['session']

    supply_request = await session.get(SupplyRequest, value)
    if supply_request:
        await message.reply(
            f'Номер заявки: {supply_request.id}\n'
            f'Ответственные: {supply_request.users}\n'
            f'Примечание: {supply_request.comment}\n'
            f'Создал: {supply_request.creator_id}'
        )
    else:
        await message.answer('Нет такой заявки')
    await dialog_manager.done()


async def get_supply_requests(dialog_manager: DialogManager, **kwargs):
    supply_requests = dialog_manager.dialog_data['supply_requests']

    return {'supply_requests': [(item, str(item)) for item in supply_requests]}


async def getter_supply_request(dialog_manager: DialogManager, **kwargs):
    session = dialog_manager.middleware_data['session']
    item_id = dialog_manager.dialog_data['supply_request_id']

    supply_request = await session.get(SupplyRequest, item_id)

    return {'supply_request': supply_request}


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


async def get_comment(dialog_manager: DialogManager, **kwargs):
    comment = dialog_manager.find('comment').get_value()
    if comment == 'None':
        comment = False
    return {'comment': comment}


async def confirm(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
) -> None:
    i18n = dialog_manager.middleware_data.get('i18n')
    await callback.answer(i18n.get('apply'))
    await dialog_manager.next()


async def get_media(dialog_manager: DialogManager, **kwargs):
    all_responsible = dialog_manager.dialog_data.get('responsible')
    responsible_selected = (dialog_manager
                            .find('responsible_checked')
                            .get_checked())
    responsible = []
    for item in all_responsible:
        for i in responsible_selected:
            if i == item[1]:
                responsible.append(item)

    media_id = MediaId(dialog_manager.dialog_data.get('media_file_id'))
    media_content_type = dialog_manager.dialog_data.get('media_content_type')
    media = MediaAttachment(media_content_type, file_id=media_id)

    comment = dialog_manager.find('comment').get_value()
    if comment == 'None':
        comment = False
    return {
        'media': media,
        'responsible_selected': responsible,
        'comment': comment
    }


async def confirm_supply_request(
        callback: CallbackQuery,
        button: Button,
        dialog_manager: DialogManager
) -> None:
    session = dialog_manager.middleware_data['session']
    user_id = dialog_manager.event.from_user.id
    comment = dialog_manager.find('comment').get_value()
    media_id = MediaId(dialog_manager.dialog_data.get('media_file_id'))
    media_content_type = dialog_manager.dialog_data.get('media_content_type')
    supply_request = await create_supply_request(
        session=session,
        creator_id=user_id,
        comment=comment,
        media_id=media_id.file_id,
        media_content_type=media_content_type,
    )
    await attach_supply_request_to_user(
        session=session,
        user_ids=[user_id],
        supply_request_id=supply_request.id,
    )

    i18n = dialog_manager.middleware_data.get('i18n')
    await callback.message.edit_caption(
        caption=(callback.message.caption or '') + '\n\n' +
                i18n.get('settings-supply_request-id',
                         supply_request_id=supply_request.id)
    )
    current_stack = dialog_manager.current_stack()
    message_id = current_stack.last_message_id
    bot: Bot = dialog_manager.middleware_data.get('bot')

    res = await bot.copy_message(
        chat_id=-1002383995858,
        from_chat_id=454342281,
        message_id=message_id,
        message_thread_id=2
    )

    await dialog_manager.done()


start_w = Window(
    I18NFormat('supply_request-help'),
    Group(
        Button(
            I18NFormat('supply_request-edit'),
            id='supply_request_edit',
            on_click=click_supply_request_edit
        ),
        Button(
            I18NFormat('supply_request-get'),
            id='supply_request_get',
            on_click=click_supply_request_get
        ),
        width=2,
    ),
    Cancel(I18NFormat('cancel')),
    MessageInput(
        media_handler,
        content_types=[ContentType.DOCUMENT, ContentType.PHOTO]
    ),
    TextInput(
        id='supply_id_input',
        type_factory=int,
        on_success=get_supply_request
    ),
    state=states.SupplyRequest.START
)

responsible_w = Window(
    I18NFormat('supply_request-responsible'),
    Group(
        Multiselect(
            Format('✓ {item[0]}'),
            Format('{item[0]}'),
            id='responsible_checked',
            item_id_getter=operator.itemgetter(1),
            items='responsible',
        ),
        width=1
    ),
    Group(
        Back(I18NFormat('back')),
        Next(I18NFormat('confirm')),
        Cancel(I18NFormat('cancel')),
        width=2
    ),
    state=states.SupplyRequest.RESPONSIBLE,
    getter=get_responsible
)

comment_w = Window(
    I18NFormat('supply_request-comment', when=~F['comment']),
    I18NFormat('supply_request-comment-enter', when='comment'),
    Format('{comment}', when='comment'),
    Const(' '),
    I18NFormat('supply_request-comment-help', when='comment'),
    TextInput(id='comment'),
    Group(
        Back(I18NFormat('back')),
        Next(I18NFormat('confirm')),
        Cancel(I18NFormat('cancel')),
        width=2
    ),
    state=states.SupplyRequest.COMMENT,
    getter=get_comment
)

preview_request_w = Window(
    DynamicMedia('media'),
    I18NFormat(
        'supply_request-responsible_list',
        when='responsible_selected'
    ),
    List(Format('{item[0]}'), items='responsible_selected'),
    Const(' '),
    I18NFormat('note', when='comment'),
    Format('{comment}', when='comment'),
    Group(
        Back(I18NFormat('back')),
        Button(
            I18NFormat('confirm'),
            id='confirm',
            on_click=confirm_supply_request
        ),
        Cancel(I18NFormat('cancel')),
        width=2
    ),
    state=states.SupplyRequest.PREVIEW_REQUEST,
    getter=get_media
)

get_requests_w = Window(
    I18NFormat('supply_request-get'),
    ScrollingGroup(
        Select(
            Format('{item[0]}'),
            id='supply_request_get',
            item_id_getter=operator.itemgetter(1),
            items='supply_requests',
            on_click=click_get_supply_request
        ),
        id='supply_requests',
        width=4,
        height=4,
        hide_on_single_page=True
    ),
    SwitchTo(
        I18NFormat('back'),
        id='back',
        state=states.SupplyRequest.START
    ),
    state=states.SupplyRequest.GET_REQUESTS,
    getter=get_supply_requests
)

get_request_w = Window(
    I18NFormat('supply_request-get'),
    Format('Номер заявки: {supply_request.id}'),
    Format('Примечание: {supply_request.comment}'),
    Format('Создал: {supply_request.creator_id}'),
    Format('Ответственные: {supply_request.users}'),
    Back(I18NFormat('back')),
    state=states.SupplyRequest.GET_REQUEST,
    getter=getter_supply_request
)



supply_request_dialog = Dialog(
    start_w,
    responsible_w,
    comment_w,
    preview_request_w,
    get_requests_w,
    get_request_w,
)
