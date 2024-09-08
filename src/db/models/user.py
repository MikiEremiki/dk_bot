from typing import List

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import BaseModelTimed


class User(BaseModelTimed):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=False, name='user_id')
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str | None] = mapped_column(String, nullable=True)

    supply_requests: Mapped[List['SupplyRequest']] = relationship(
        secondary='users_supply_requests',
        back_populates='users',
        lazy='selectin')
