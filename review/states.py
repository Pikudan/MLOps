from aiogram.fsm.state import State, StatesGroup, default_state
class FSMStates(StatesGroup):
    '''states for bot'''
    # waiting to receive information about available events for confirmation
    waiting_for_end_start = State()
    waiting_for_get = State()
    # messages are sent from the farmer
    waiting_for_end_get = State()
    # record refusal/confirm
    waiting_for_confirmation = State()
    # waiting end comment for refusal/confirm
    waiting_for_end_comment = State()
    # waiting comments are deleted
    waiting_for_end_cancel_comment = State()
    waiting_for_end_loading_message = State()
    wait_menu_click = State()
    waiting_for_start_comment = State()
