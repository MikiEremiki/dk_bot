from typing import Optional, List

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import BaseModelTimed


class SupplyRequest(BaseModelTimed):
    __tablename__ = 'supply_requests'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    creator_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('users.user_id'), nullable=False)
    comment: Mapped[Optional[str]]
    media_id: Mapped[str]
    media_content_type: Mapped[str]

    users: Mapped[List['User']] = relationship(
        secondary='users_supply_requests',
        back_populates='supply_requests',
        lazy='selectin')


class UserSupplyRequest(BaseModelTimed):
    __tablename__ = 'users_supply_requests'

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.user_id'), primary_key=True)
    supply_request_id: Mapped[int] = mapped_column(
        ForeignKey('supply_requests.id'), primary_key=True)
