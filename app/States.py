from aiogram.fsm.state import StatesGroup, State


class pbr_cl(StatesGroup):
    user_id = State()
    summ = State()

class ibr_cl(StatesGroup):
    user_id = State()
    summ = State()

class posting_id_accept(StatesGroup):
    posting_id = State()
    posting_text = State()

class posting_accept_cost(StatesGroup):
    life_time_accept = State()

class date_accept_cost(StatesGroup):
    weeks = State()

class sca(StatesGroup):
    set_cost = State()
    k_dscnt = State()
    week = State()

class posting_accept_text(StatesGroup):
    npt = State()
    posting_id = State()

class posting_id_date(StatesGroup):
    posting_id = State()
    posting_text = State()

class posting_date_text(StatesGroup):
    npt = State()
    posting_id = State()

class prodlite(StatesGroup):
    posting_id1 = State()
    posting_value1 = State()
    fcost1 = State()
    current_date1 = State()

class prodlit1(StatesGroup):
    posting_id = State()
    posting_value = State()
    fcost = State()
    current_date = State()