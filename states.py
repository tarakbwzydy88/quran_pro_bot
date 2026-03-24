from aiogram.fsm.state import State, StatesGroup

class SearchStates(StatesGroup):
    waiting_for_keyword = State()

class ReminderStates(StatesGroup):
    waiting_for_time = State()