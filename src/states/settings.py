from aiogram.fsm.state import State, StatesGroup


class Settings(StatesGroup):
    MAIN = State()


class SupplyRequestSettings(StatesGroup):
    START = State()
    RESPONSIBLE = State()
