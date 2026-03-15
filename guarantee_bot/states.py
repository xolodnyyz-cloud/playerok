from aiogram.fsm.state import StatesGroup, State

class DealCreation(StatesGroup):
    seller_username = State()
    amount = State()
    description = State()
    payment_method = State()  # Эта строка ОБЯЗАТЕЛЬНО должна быть!

class WalletStates(StatesGroup):
    waiting_for_ton = State()
    waiting_for_usdt = State()
    waiting_for_card_number = State()
    waiting_for_card_holder = State()
    waiting_for_card_bank = State()