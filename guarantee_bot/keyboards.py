from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ГЛАВНОЕ МЕНЮ
def main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ Создать сделку", callback_data="create_deal"))
    builder.row(InlineKeyboardButton(text="👛 Добавить/изменить кошелёк", callback_data="wallet_settings"))
    builder.row(InlineKeyboardButton(text="🆘 Поддержка", callback_data="support"))
    return builder.as_markup()

# МЕНЮ ВЫБОРА МЕТОДА ОПЛАТЫ (БЕЗ ЗВЕЗД)
def payment_method_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="На TON-кошелек 🏠", callback_data="pay_ton"))
    builder.row(InlineKeyboardButton(text="Карта (РФ) 📄", callback_data="pay_card"))
    builder.row(InlineKeyboardButton(text="USDT 💰", callback_data="pay_usdt"))
    builder.row(InlineKeyboardButton(text="◀️ В меню", callback_data="back_to_main"))
    return builder.as_markup()

# МЕНЮ ВЫБОРА КОШЕЛЬКА (БЕЗ ЗВЕЗД)
def wallet_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="На TON-кошелек 🏠", callback_data="wallet_ton"))
    builder.row(InlineKeyboardButton(text="Карта (РФ) 📄", callback_data="wallet_card"))
    builder.row(InlineKeyboardButton(text="USDT 💰", callback_data="wallet_usdt"))
    builder.row(InlineKeyboardButton(text="◀️ В меню", callback_data="back_to_main"))
    return builder.as_markup()

# МЕНЮ ПРОСМОТРА КОШЕЛЬКОВ (БЕЗ ЗВЕЗД)
def wallet_view_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🏠 TON", callback_data="view_ton"))
    builder.row(InlineKeyboardButton(text="📄 Карта", callback_data="view_card"))
    builder.row(InlineKeyboardButton(text="💰 USDT", callback_data="view_usdt"))
    builder.row(
        InlineKeyboardButton(text="✏️ Редактировать", callback_data="wallet_settings"),
        InlineKeyboardButton(text="◀️ В меню", callback_data="back_to_main")
    )
    return builder.as_markup()

# АДМИН МЕНЮ
def admin_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📋 Активные сделки", callback_data="admin_active_deals"))
    builder.add(InlineKeyboardButton(text="📜 История всех сделок", callback_data="admin_history"))
    builder.adjust(1)
    return builder.as_markup()

# КЛАВИАТУРЫ ДЛЯ СДЕЛОК
def payment_confirmation_keyboard(deal_id):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"paid_{deal_id}"))
    return builder.as_markup()

def admin_payment_check_keyboard(deal_id):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Деньги получены", callback_data=f"admin_confirm_payment_{deal_id}"))
    builder.add(InlineKeyboardButton(text="❌ Деньги не получены", callback_data=f"admin_decline_payment_{deal_id}"))
    builder.adjust(1)
    return builder.as_markup()

def seller_confirm_receipt_keyboard(deal_id):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="👍 Подтвердить получение товара", callback_data=f"seller_confirm_{deal_id}"))
    return builder.as_markup()