from typing import Optional, Self, Any

import msgpack
from aiogram.filters.state import StateType
from aiogram.fsm.state import State
from aiogram.fsm.storage.base import (
    BaseStorage,
    StorageKey,
    DefaultKeyBuilder,
    KeyBuilder
)

from nats.aio.client import Client
from nats.js import JetStreamContext
from nats.js.api import KeyValueConfig, StorageType
from nats.js.errors import NotFoundError
from nats.js.kv import KeyValue


class NatsStorage(BaseStorage):
    def __init__(
            self,
            nc: Client,
            js: JetStreamContext,
            key_builder: Optional[KeyBuilder] = None,
            fsm_states_bucket: str = 'fsm_states_aiogram',
            fsm_data_bucket: str = 'fsm_data_aiogram'
    ) -> None:
        if key_builder is None:
            key_builder = DefaultKeyBuilder(with_destiny=True)

        self.nc = nc
        self.js = js
        self._key_builder = key_builder
        self.fsm_states_bucket = fsm_states_bucket
        self.fsm_data_bucket = fsm_data_bucket
        self.kv_states: Optional[KeyValue] = None
        self.kv_data: Optional[KeyValue] = None

    async def create_storage(self) -> Self:
        self.kv_states = await self._get_kv_states()
        self.kv_data = await self._get_kv_data()
        return self

    async def _get_kv_states(self) -> KeyValue:
        return await self.js.create_key_value(
            config=KeyValueConfig(
                bucket=self.fsm_states_bucket,
                history=5,
                storage=StorageType.FILE
            )
        )

    async def _get_kv_data(self) -> KeyValue:
        return await self.js.create_key_value(
            config=KeyValueConfig(
                bucket=self.fsm_data_bucket,
                history=5,
                storage=StorageType.FILE
            )
        )

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        state = state.state if isinstance(state, State) else state
        await self.kv_states.put(
            key=self._key_builder.build(key),
            value=msgpack.packb(state or None)
        )

    async def get_state(self, key: StorageKey) -> Optional[str]:
        state = None
        try:
            entry = await self.kv_states.get(key=self._key_builder.build(key))
            state = msgpack.unpackb(entry.value)
        except NotFoundError:
            pass
        return state

    async def set_data(self, key: StorageKey, data: StateType) -> None:
        await self.kv_data.put(
            key=self._key_builder.build(key),
            value=msgpack.packb(data)
        )

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        data = {}
        try:
            entry = await self.kv_data.get(key=self._key_builder.build(key))
            data = msgpack.unpackb(entry.value)
        except NotFoundError:
            pass
        return data

    async def close(self) -> None:
        await self.nc.close()
