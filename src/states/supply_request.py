from aiogram.fsm.state import State, StatesGroup


class SupplyRequest(StatesGroup):
    START = State()
    RESPONSIBLE = State()
    COMMENT = State()
    PREVIEW_REQUEST = State()
    GET_REQUESTS = State()
    GET_REQUEST = State()