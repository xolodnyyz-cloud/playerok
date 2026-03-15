from aiogram.fsm.state import StatesGroup, State

class DealCreation(StatesGroup):
    seller_username = State()
    amount = State()
    description = State()
    payment_method = State()  # НОВОЕ: выбор метода оплаты

class WalletStates(StatesGroup):
    # Для TON
    waiting_for_ton = State()
    
    # Для USDT
    waiting_for_usdt = State()
    
    # Для карты
    waiting_for_card_number = State()
    waiting_for_card_holder = State()
    waiting_for_card_bank = State()