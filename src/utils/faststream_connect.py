import logging

import msgpack
from faststream import FastStream, Logger
from faststream.nats import NatsBroker, NatsRouter
from nats.js.api import StorageType

logger = logging.getLogger('broker')
router = NatsRouter(prefix='prefix_')


def create_app(servers, user, password, router, logger):
    broker = NatsBroker(
        servers=servers,
        user=user,
        password=password,
        logger=logger
    )
    broker.include_router(router)
    app = FastStream(broker, logger=logger)

    @app.after_startup
    async def setup_broker():
        key_value = await broker.key_value(
            bucket='bucket',
            history=5,
            storage=StorageType.FILE
        )
        await key_value.put('key', b'Hello!')
        await key_value.put('key', msgpack.packb('hello привет'))

    return app


@router.subscriber('test')
async def base_handler(body, logger: Logger):
    logger.info(body)
    print(body)


async def get_kv_from_dialog_manager(dialog_manager):
    fs_app: FastStream = dialog_manager.middleware_data['fs_app']
    broker: NatsBroker = fs_app.broker
    key_value = await broker.key_value('bucket')
    return key_value
