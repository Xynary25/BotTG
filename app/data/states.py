from aiogram.dispatcher.filters.state import State, StatesGroup

"""
	Все это стоит проигнорировать, это стейты - такая штука
	Которая переводит из одного состояния отношений с юзером в другое
"""


class Calculator(StatesGroup):
    main = State()


class AdminPanel(StatesGroup):
    main = State()
    qiwi_out = State()
    notify = State()
    change_balance_id = State()
    change_balance_amount = State()


class Out(StatesGroup):
    main = State()
    req = State()
