from aiogram import Router, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message

echo_router = Router()


@echo_router.message(Command(commands='echo'))
async def echo_cmd(message: Message, bot: Bot):
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)
    is_forum = str(message.chat.is_forum)
    is_topic_message = str(message.is_topic_message)

    text = 'chat_id = <code>' + chat_id + '</code>\n'
    text += 'user_id = <code>' + user_id + '</code>\n\n'

    text += 'is_forum = <code>' + is_forum + '</code>\n'
    text += 'is_topic_message = <code>' + is_topic_message + '</code>\n'

    message_thread_id = message.message_thread_id
    if message_thread_id:
        text += 'message_thread_id = <code>' + str(message_thread_id) + '</code>\n'
    rtm = message.reply_to_message
    if rtm:
        ftc = message.reply_to_message.forum_topic_created
        fte = message.reply_to_message.forum_topic_edited
        if ftc:
            topic_name_created = ftc.name
            text += 'topic_name_created = <code>' + topic_name_created + '</code>\n'
        if fte:
            topic_name_edited = fte.name
            text += 'topic_name_edited = <code>' + topic_name_edited + '</code>\n'

    await bot.send_message(
        chat_id=chat_id,
        text=text,
        message_thread_id=message_thread_id
    )
