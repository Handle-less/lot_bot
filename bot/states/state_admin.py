from aiogram.dispatcher.filters.state import StatesGroup, State


class StateUser(StatesGroup):
    name_or_id = State()


class StateDist(StatesGroup):
    text = State()
    preview = State()


class StateReport(StatesGroup):
    answer = State()


class StateLotAdd(StatesGroup):
    location = State()
    task = State()
    deadline = State()
    first_price = State()
    state_action = State()
    state_edit = State()
