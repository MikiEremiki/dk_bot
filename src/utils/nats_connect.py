from nats.aio.client import Client
from nats.js import JetStreamContext
from faststream.nats import NatsBroker


async def connect_to_nats(broker: NatsBroker) -> tuple[Client, JetStreamContext]:
    nc: Client = await broker.connect()
    js: JetStreamContext = nc.jetstream()
    return nc, js
