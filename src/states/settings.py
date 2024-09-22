from aiogram.fsm.state import State, StatesGroup


class Settings(StatesGroup):
    MAIN = State()


class SupplyRequestSettings(StatesGroup):
    START = State()
    RESPONSIBLE = State()


class RoleSettings(StatesGroup):
    SELECT_USER = State()
    SELECT_ROLE = State()
    CONFIRM = State()
