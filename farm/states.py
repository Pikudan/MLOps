from aiogram.fsm.state import State, StatesGroup, default_state
class FSMStates(StatesGroup):
    '''states for bot'''
    wait_calendar_name = State()
    # waiting to receive information about available events for confirmation
    selected_calendar = State()
    waiting_for_start_comment = State()
    # waiting end comment
    waiting_for_end_comment = State()
    # waiting comments are deleted
    waiting_for_end_cancel_comment = State()
    waiting_for_end_loading_message = State()
    waiting_for_end_start = State()
    waiting_for_end_confirm = State()
    wait_menu_click = State()
    waiting_more_info = State()
    # waiting for problem assessment
    set_grade = State()
    clear_msg_with_grade = State()

class FSMStatus(StatesGroup):
    support = State()
    create_problem = State()
    start_chating = State()
    wait_describe = State()
    chating = State()

class FSMAddRecord(StatesGroup):
    wait_name = State()
    wait_date = State()
    wait_describe = State()
