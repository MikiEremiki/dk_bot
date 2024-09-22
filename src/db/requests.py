from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User, SupplyRequest


async def upsert_user(
        session: AsyncSession,
        user_id: int,
        chat_id: int,
        first_name: str,
        last_name: str | None = None,
        username: str | None = None,
):
    """
    Добавление или обновление пользователя в таблице users
    :param session: сессия СУБД
    :param user_id: айди пользователя
    :param chat_id: айди чата
    :param first_name: имя пользователя
    :param last_name: фамилия пользователя
    :param username: никнейм пользователя
    """
    stmt = insert(User).values(
        {
            'user_id': user_id,
            'chat_id': chat_id,
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
        }
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=['user_id'],
        set_=dict(
            chat_id=chat_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
        ),
    )
    await session.execute(stmt)
    await session.commit()


async def create_supply_request(
        session: AsyncSession,
        creator_id: int,
        comment: str | None,
        media_id: str,
        media_content_type: str,
):
    supply_request = SupplyRequest(
        creator_id=creator_id,
        comment=comment,
        media_id=media_id,
        media_content_type=media_content_type,
    )
    session.add(supply_request)
    await session.commit()
    return supply_request


async def attach_supply_request_to_user(
        session: AsyncSession,
        user_ids: [int],
        supply_request_id: int,
):
    supply_request = await session.get(SupplyRequest, supply_request_id)
    if isinstance(supply_request, SupplyRequest):
        await session.refresh(supply_request)
        for user_id in user_ids:
            user = await session.get(User, user_id)
            if user:
                supply_request.users.append(user)
        await session.commit()


async def get_supply_request_by_user(
        session: AsyncSession,
        user_id: int,
):
    stmt = select(SupplyRequest).where(SupplyRequest.creator_id == user_id)
    res = await session.execute(stmt)
    supply_requests = res.scalars().all()

    return supply_requests
