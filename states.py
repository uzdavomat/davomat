from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_id = State()