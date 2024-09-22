import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram_dialog import setup_dialogs
from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState
from fluentogram import TranslatorHub
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import load_config
from config.config import Config
from handlers.errors import on_unknown_intent, on_unknown_state
from log.logging_conf import load_log_config
from storage.nats_storage import NatsStorage
from middlewares.i18n import TranslatorRunnerMiddleware
from middlewares.session import DbSessionMiddleware
from middlewares.track_all_users import TrackAllUsersMiddleware
from utils.i18n import create_translator_hub
from utils.nats_connect import connect_to_nats
from utils.faststream_connect import create_app, router, logger
from handlers import get_routers
from dialogs import get_dialog_routers

bot_logger = load_log_config()
bot_logger.info('Инициализация бота')


async def main():
    config: Config = load_config('windows')

    app = create_app(
        servers=str(config.nats.host),
        user=str(config.nats.user.get_secret_value()),
        password=str(config.nats.password.get_secret_value()),
        router=router,
        logger=logger
    )
    nc, js = await connect_to_nats(app.broker)

    storage = await NatsStorage(nc=nc, js=js).create_storage()

    bot = Bot(token=config.bot.token.get_secret_value(),
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(
        storage=storage,
        events_isolation=SimpleEventIsolation())

    async_engine = create_async_engine(
        url=str(config.postgres.dsn),
        echo=config.postgres.is_echo
    )
    sessionmaker = async_sessionmaker(async_engine, expire_on_commit=False)
    translator_hub: TranslatorHub = create_translator_hub(config)

    dp.message.outer_middleware(TrackAllUsersMiddleware())
    dp.update.outer_middleware(DbSessionMiddleware(sessionmaker))
    dp.update.outer_middleware(TranslatorRunnerMiddleware(translator_hub))

    dp.errors.register(on_unknown_intent, ExceptionTypeFilter(UnknownIntent))
    dp.errors.register(on_unknown_state, ExceptionTypeFilter(UnknownState))

    dp.include_routers(*get_routers(config))
    dp.include_routers(*get_dialog_routers())

    setup_dialogs(dp)

    try:
        await asyncio.gather(
            app.run(),
            dp.start_polling(bot, fs_app=app, config=config),
        )
    except Exception as e:
        print(e)
    finally:
        await dp.stop_polling()


import sys
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())
