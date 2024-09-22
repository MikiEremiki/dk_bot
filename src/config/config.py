from typing import Optional

from dynaconf import Dynaconf
from pydantic import PostgresDsn, BaseModel, SecretStr, NatsDsn, RedisDsn
from pydantic_settings import BaseSettings


class BotSettings(BaseModel):
    token: SecretStr
    developer_chat_id: Optional[int]


class PostgresSettings(BaseModel):
    dsn: PostgresDsn
    is_echo: bool


class RedisSettings(BaseModel):
    dsn: RedisDsn


class NatsSettings(BaseModel):
    host: NatsDsn
    user: SecretStr
    password: SecretStr


class PathsSettings(BaseModel):
    locales: str


class Config(BaseSettings):
    bot: BotSettings
    postgres: PostgresSettings
    redis: RedisSettings
    nats: NatsSettings
    paths: PathsSettings


def load_config(env=None) -> Config:
    dyna_settings = Dynaconf(
        envvar_prefix='DYNACONF',
        settings_files=['settings.toml', '.secrets.toml'],
        environments=True,
        env=env
    )
    config = Config(
        bot=BotSettings(token=dyna_settings.bot.token,
                        developer_chat_id=dyna_settings.bot.developer_chat_id),
        postgres=PostgresSettings(dsn=dyna_settings.postgres.dsn,
                                  is_echo=dyna_settings.postgres.is_echo),
        redis=RedisSettings(dsn=dyna_settings.redis.dsn),
        nats=NatsSettings(host=dyna_settings.nats.host,
                          user=dyna_settings.nats.user,
                          password=dyna_settings.nats.password),
        paths=PathsSettings(locales=dyna_settings.path.locales)
    )

    return config
