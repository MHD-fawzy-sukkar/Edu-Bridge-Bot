from aiogram.fsm.state import State, StatesGroup

class RequestForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_branch = State()
    waiting_for_governorate = State()
    waiting_for_address = State()
    waiting_for_content = State()

class SupportForm(StatesGroup):
    waiting_for_content = State()

class AdminReplyForm(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_message = State()