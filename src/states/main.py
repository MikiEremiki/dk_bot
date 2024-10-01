from aiogram.fsm.state import State, StatesGroup


class Main(StatesGroup):
    MAIN = State()


class Register(StatesGroup):
    PHONE = State()
    REAL_NAME = State()
