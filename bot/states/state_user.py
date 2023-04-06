from aiogram.dispatcher.filters.state import StatesGroup, State


class StartState(StatesGroup):
    full_name = State()
    phone = State()


class StateReport(StatesGroup):
    text = State()


class StateVerification(StatesGroup):
    uid = State()
    region = State()
    category = State()


class StateUserLot(StatesGroup):
    price = State()
