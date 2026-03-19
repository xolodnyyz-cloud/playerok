from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import ADMIN_IDS
from database import (
    create_deal, get_deal_by_id, update_deal_status, 
    set_seller_id, get_active_deals, get_all_deals,
    get_deal_by_buyer_code, get_user_wallets, 
    update_ton_wallet, update_usdt_wallet, update_card_wallet,
    get_user_balance, add_rub, add_stars, add_usdt, add_ton,
    update_sbp_wallet
)
import sqlite3
import re

router = Router()

# ============== СОСТОЯНИЯ ==============
class DealCreation(StatesGroup):
    payment_method = State()
    seller_username = State()
    amount = State()
    description = State()

class WalletStates(StatesGroup):
    waiting_for_ton = State()
    waiting_for_usdt = State()
    waiting_for_card_number = State()
    waiting_for_card_holder = State()
    waiting_for_card_bank = State()
    waiting_for_sbp_number = State()
    waiting_for_sbp_name = State()

# ============== КЛАВИАТУРЫ ==============
def main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ Создать сделку", callback_data="create_deal"))
    builder.row(InlineKeyboardButton(text="👛 Добавить/изменить кошелёк", callback_data="wallet_settings"))
    builder.row(InlineKeyboardButton(text="👤 Профиль", callback_data="profile"))
    builder.row(InlineKeyboardButton(text="☑️ Наш сайт", url="https://playerok.com"))
    builder.row(InlineKeyboardButton(text="🆘 Поддержка", callback_data="support"))
    return builder.as_markup()

def profile_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ В меню", callback_data="back_to_main"))
    return builder.as_markup()

def payment_method_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="На TON-кошелек 🏠", callback_data="pay_ton"))
    builder.row(InlineKeyboardButton(text="Карта (РФ) 📄", callback_data="pay_card"))
    builder.row(InlineKeyboardButton(text="СБП 📱", callback_data="pay_sbp"))
    builder.row(InlineKeyboardButton(text="Звезды ⭐️", callback_data="pay_stars"))
    builder.row(InlineKeyboardButton(text="USDT 💰", callback_data="pay_usdt"))
    builder.row(InlineKeyboardButton(text="◀️ В меню", callback_data="back_to_main"))
    return builder.as_markup()

def wallet_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="На TON-кошелек 🏠", callback_data="wallet_ton"))
    builder.row(InlineKeyboardButton(text="Карта (РФ) 📄", callback_data="wallet_card"))
    builder.row(InlineKeyboardButton(text="СБП 📱", callback_data="wallet_sbp"))
    builder.row(InlineKeyboardButton(text="Звезды ⭐️", callback_data="wallet_stars"))
    builder.row(InlineKeyboardButton(text="USDT 💰", callback_data="wallet_usdt"))
    builder.row(InlineKeyboardButton(text="◀️ В меню", callback_data="back_to_main"))
    return builder.as_markup()

def wallet_view_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🏠 TON", callback_data="view_ton"))
    builder.row(InlineKeyboardButton(text="📄 Карта", callback_data="view_card"))
    builder.row(InlineKeyboardButton(text="📱 СБП", callback_data="view_sbp"))
    builder.row(InlineKeyboardButton(text="⭐️ Звезды", callback_data="view_stars"))
    builder.row(InlineKeyboardButton(text="💰 USDT", callback_data="view_usdt"))
    builder.row(
        InlineKeyboardButton(text="✏️ Редактировать", callback_data="wallet_settings"),
        InlineKeyboardButton(text="◀️ В меню", callback_data="back_to_main")
    )
    return builder.as_markup()

def admin_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📋 Активные сделки", callback_data="admin_active_deals"))
    builder.add(InlineKeyboardButton(text="📜 История всех сделок", callback_data="admin_history"))
    builder.adjust(1)
    return builder.as_markup()

def seller_confirm_receipt_keyboard(deal_id):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="👍 Подтвердить получение товара", callback_data=f"seller_confirm_{deal_id}"))
    return builder.as_markup()

def gift_transferred_keyboard(deal_id):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Подарок передан", callback_data=f"gift_transferred_{deal_id}"))
    return builder.as_markup()

# ============== ОСНОВНЫЕ ОБРАБОТЧИКИ ==============
@router.message(CommandStart())
async def cmd_start(message: Message):
    args = message.text.split()
    
    if len(args) > 1 and args[1].startswith("deal_"):
        deal_id = args[1].replace("deal_", "")
        deal = get_deal_by_id(deal_id)
        
        if deal:
            seller_username = deal[3]
            method = deal[10] if len(deal) > 10 and deal[10] else "card"
            
            if method == "stars":
                currency_display = "⭐️ stars"
            elif method == "ton":
                currency_display = "🪙 TON"
            elif method == "usdt":
                currency_display = "💰 USDT"
            elif method == "sbp":
                currency_display = "📱 СБП"
            else:
                currency_display = "₽"
            
            await message.answer(
                f"🔍 Информация о сделке #{deal_id}\n\n"
                f"💰 Сумма: {deal[5]} {currency_display}\n"
                f"📝 Описание: {deal[6]}\n"
                f"👤 Продавец: {seller_username}\n\n"
                f"📌 Ожидайте подтверждения оплаты от администратора."
            )
        else:
            await message.answer("❌ Сделка не найдена.")
    else:
        welcome_text = (
            "👋 Добро пожаловать!\n\n"
            "🎮 Playerok - надёжный сервис для безопасных сделок!\n"
            "Автоматизировано, быстро и без лишних хлопот!\n"
            "Теперь ваши сделки под защитой! 🎉\n\n"
            "Выберите действие:"
        )
        
        await message.answer(
            welcome_text,
            reply_markup=main_menu_keyboard()
        )

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer(
            "🔐 Панель администратора",
            reply_markup=admin_menu_keyboard()
        )
    else:
        await message.answer("⛔ Доступ запрещен.")

# ============== ПРОФИЛЬ ==============
@router.callback_query(F.data == "profile")
async def show_profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    balance = get_user_balance(user_id)
    
    rub = balance[1] if balance else 0
    stars = balance[2] if balance else 0
    usdt = balance[3] if balance else 0
    ton = balance[4] if balance else 0
    
    profile_text = (
        f"👤 Ваш профиль\n\n"
        f"💰 Рубли: {rub} ₽\n"
        f"⭐️ Звезды: {stars} ⭐️\n"
        f"💵 USDT: {usdt} 💰\n"
        f"🪙 TON: {ton} 🪙\n\n"
        f"Баланс обновляется автоматически после сделок"
    )
    
    await callback.message.edit_text(
        profile_text,
        reply_markup=profile_keyboard()
    )

# ============== СЕКРЕТНЫЕ КОМАНДЫ ==============
@router.message(Command("addrub"))
async def add_rub_command(message: Message):
    args = message.text.split()
    if len(args) != 2:
        await message.answer("❌ Использование: /addrub [сумма]\nПример: /addrub 100")
        return
    
    try:
        amount = float(args[1])
        if amount <= 0:
            await message.answer("❌ Сумма должна быть положительной")
            return
    except ValueError:
        await message.answer("❌ Введите корректное число")
        return
    
    user_id = message.from_user.id
    add_rub(user_id, amount)
    
    balance = get_user_balance(user_id)
    rub = balance[1]
    
    await message.answer(f"✅ Добавлено {amount} ₽\n💰 Текущий баланс: {rub} ₽")

@router.message(Command("addstars"))
async def add_stars_command(message: Message):
    args = message.text.split()
    if len(args) != 2:
        await message.answer("❌ Использование: /addstars [сумма]\nПример: /addstars 100")
        return
    
    try:
        amount = float(args[1])
        if amount <= 0:
            await message.answer("❌ Сумма должна быть положительной")
            return
    except ValueError:
        await message.answer("❌ Введите корректное число")
        return
    
    user_id = message.from_user.id
    add_stars(user_id, amount)
    
    balance = get_user_balance(user_id)
    stars = balance[2]
    
    await message.answer(f"✅ Добавлено {amount} ⭐️\n⭐️ Текущий баланс: {stars} ⭐️")

@router.message(Command("addusdt"))
async def add_usdt_command(message: Message):
    args = message.text.split()
    if len(args) != 2:
        await message.answer("❌ Использование: /addusdt [сумма]\nПример: /addusdt 100")
        return
    
    try:
        amount = float(args[1])
        if amount <= 0:
            await message.answer("❌ Сумма должна быть положительной")
            return
    except ValueError:
        await message.answer("❌ Введите корректное число")
        return
    
    user_id = message.from_user.id
    add_usdt(user_id, amount)
    
    balance = get_user_balance(user_id)
    usdt = balance[3]
    
    await message.answer(f"✅ Добавлено {amount} 💰\n💰 Текущий баланс: {usdt} USDT")

@router.message(Command("addton"))
async def add_ton_command(message: Message):
    args = message.text.split()
    if len(args) != 2:
        await message.answer("❌ Использование: /addton [сумма]\nПример: /addton 100")
        return
    
    try:
        amount = float(args[1])
        if amount <= 0:
            await message.answer("❌ Сумма должна быть положительной")
            return
    except ValueError:
        await message.answer("❌ Введите корректное число")
        return
    
    user_id = message.from_user.id
    add_ton(user_id, amount)
    
    balance = get_user_balance(user_id)
    ton = balance[4]
    
    await message.answer(f"✅ Добавлено {amount} 🪙\n🪙 Текущий баланс: {ton} TON")

@router.message(Command("balance"))
async def show_balance_command(message: Message):
    user_id = message.from_user.id
    balance = get_user_balance(user_id)
    
    rub = balance[1] if balance else 0
    stars = balance[2] if balance else 0
    usdt = balance[3] if balance else 0
    ton = balance[4] if balance else 0
    
    await message.answer(
        f"👤 Ваш баланс\n\n"
        f"💰 Рубли: {rub} ₽\n"
        f"⭐️ Звезды: {stars} ⭐️\n"
        f"💵 USDT: {usdt} 💰\n"
        f"🪙 TON: {ton} 🪙"
    )

# ============== КОМАНДА FASTBUY ==============
@router.message(Command("fastbuy"))
async def fast_buy(message: Message):
    args = message.text.split()
    if len(args) != 2:
        await message.answer("❌ Использование: /fastbuy [ID сделки]\nПример: /fastbuy ABC123")
        return
    
    deal_id = args[1]
    deal = get_deal_by_id(deal_id)
    
    if not deal:
        await message.answer("❌ Сделка не найдена.")
        return
    
    if deal[9] != "waiting_for_payment":
        await message.answer("❌ Эта сделка уже оплачена или завершена.")
        return
    
    seller_id = deal[4]
    seller_username = deal[3]
    amount = float(deal[5]) if deal[5] else 0
    description = deal[6] if deal[6] else "Не указано"
    method = deal[10] if len(deal) > 10 and deal[10] else "card"
    
    if method == "stars":
        currency_symbol = "⭐️"
        currency_text = "stars"
    elif method == "ton":
        currency_symbol = "🪙"
        currency_text = "TON"
    elif method == "usdt":
        currency_symbol = "💰"
        currency_text = "USDT"
    elif method == "sbp":
        currency_symbol = "📱"
        currency_text = "СБП"
    else:
        currency_symbol = "₽"
        currency_text = "рублей"
    
    update_deal_status(deal_id, "payment_confirmed")
    
    await message.answer(
        f"✅ Оплата подтверждена для сделки #{deal_id}!\n\n"
        f"💳 С вашего аккаунта списано: {amount} {currency_symbol} {currency_text}\n"
        f"💰 Сумма сделки: {amount} {currency_symbol} {currency_text}\n\n"
        f"Продавец уже получил уведомление."
    )

    if seller_id:
        try:
            await message.bot.send_message(
                seller_id,
                f"✅ Оплата подтверждена для сделки #{deal_id}\n\n"
                f"📜 Описание: \n"
                f"{description}\n\n"
                f"📦 NFT ожидает отправки на официальный аккаунт менеджера - @playerok_supportz\n\n"
                f"❗❗❗ ВАЖНО ❗❗❗\n\n"
                f"Ваш подарок нужно обязательно передать ИМЕННО МЕНЕДЖЕРУ, а не человеку, с которым вы договорились о сделке.\n\n"
                f"❌ Если вы передадите подарок напрямую покупателю, сделка будет ОТКЛОНЕНА, и вы НЕ ПОЛУЧИТЕ свои средства!\n\n"
                f"✅ Только после передачи менеджеру вы получите оплату.\n\n"
                f"⚠️ ВАЖНО:\n"
                f"➤ Подарок необходимо передать менеджеру.\n"
                f"➤ Средства будут зачислены после проверки.\n\n"
                f"👇 После того как передадите подарок, нажмите кнопку ниже:",
                reply_markup=gift_transferred_keyboard(deal_id)
            )
            print(f"✅ Сообщение отправлено продавцу {seller_id}")
        except Exception as e:
            print(f"❌ Не удалось отправить уведомление продавцу {seller_id}: {e}")

    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(
                admin_id,
                f"💰 Пользователь оплатил сделку!\n\n"
                f"🔹 Номер сделки: #{deal_id}\n"
                f"🔹 Продавец: {seller_username}\n"
                f"🔹 Покупатель: @{message.from_user.username or 'нет username'}\n"
                f"🔹 Сумма: {amount} {currency_symbol} {currency_text}\n"
                f"🔹 Метод оплаты: {method}\n"
                f"🔹 Описание: {description}"
            )
        except Exception as e:
            print(f"Ошибка отправки админу: {e}")

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    welcome_text = (
        "👋 Добро пожаловать!\n\n"
        "🎮 Playerok - надёжный сервис для безопасных сделок!\n"
        "Автоматизировано, быстро и без лишних хлопот!\n"
        "Теперь ваши сделки под защитой! 🎉\n\n"
        "Выберите действие:"
    )
    
    await callback.message.edit_text(
        welcome_text,
        reply_markup=main_menu_keyboard()
    )

@router.callback_query(F.data == "support")
async def support(callback: CallbackQuery):
    support_username = "playerok_supportz"
    support_link = f"https://t.me/{support_username}"
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📨 Написать администратору", url=support_link))
    builder.row(InlineKeyboardButton(text="◀️ В меню", callback_data="back_to_main"))
    
    await callback.message.edit_text(
        "🆘 Поддержка\n\nЕсли у вас возникли вопросы или проблемы, свяжитесь с администратором:",
        reply_markup=builder.as_markup()
    )

# ============== СОЗДАНИЕ СДЕЛКИ ==============
@router.callback_query(F.data == "create_deal")
async def create_deal_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "💳 Выберите метод оплаты:\n\nУкажите, как покупатель будет переводить деньги:",
        reply_markup=payment_method_keyboard()
    )
    await state.set_state(DealCreation.payment_method)

@router.callback_query(DealCreation.payment_method, F.data.startswith("pay_"))
async def process_payment_method_first(callback: CallbackQuery, state: FSMContext):
    method = callback.data.replace("pay_", "")
    
    wallets = get_user_wallets(callback.from_user.id)
    
    if method == "card" and (not wallets or not wallets[3]):
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="💳 Добавить карту", callback_data="wallet_card"))
        builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main"))
        
        await callback.message.edit_text(
            "❌ У вас не добавлена банковская карта!\n\n"
            "Для создания сделки с оплатой на карту необходимо добавить карту в кошелек.\n\n"
            "Нажмите кнопку ниже, чтобы добавить карту:",
            reply_markup=builder.as_markup()
        )
        return
    
    if method == "ton" and (not wallets or not wallets[1]):
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="🪙 Добавить TON кошелек", callback_data="wallet_ton"))
        builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main"))
        
        await callback.message.edit_text(
            "❌ У вас не добавлен TON кошелек!\n\n"
            "Для создания сделки с оплатой в TON необходимо добавить TON кошелек.\n\n"
            "Нажмите кнопку ниже, чтобы добавить кошелек:",
            reply_markup=builder.as_markup()
        )
        return
    
    if method == "usdt" and (not wallets or not wallets[2]):
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="💰 Добавить USDT кошелек", callback_data="wallet_usdt"))
        builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main"))
        
        await callback.message.edit_text(
            "❌ У вас не добавлен USDT кошелек!\n\n"
            "Для создания сделки с оплатой в USDT необходимо добавить USDT кошелек.\n\n"
            "Нажмите кнопку ниже, чтобы добавить кошелек:",
            reply_markup=builder.as_markup()
        )
        return
    
    if method == "sbp" and (not wallets or not wallets[6] or not wallets[7]):
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="📱 Добавить СБП", callback_data="wallet_sbp"))
        builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main"))
        
        await callback.message.edit_text(
            "❌ У вас не добавлен номер СБП!\n\n"
            "Для создания сделки с оплатой через СБП необходимо добавить номер телефона.\n\n"
            "Нажмите кнопку ниже, чтобы добавить номер:",
            reply_markup=builder.as_markup()
        )
        return
    
    await state.update_data(payment_method=method)
    
    text = ""
    if method == "stars":
        text = "💰 Создание сделки с оплатой в звездах\n\n🏦 Получатель звезд\nУкажите свой @username"
    elif method == "card":
        text = "💰 Создание сделки с оплатой на карту\n\n💳 Ваша карта готова к использованию\nУкажите свой @username"
    elif method == "ton":
        text = "💰 Создание сделки с оплатой в TON\n\n🏦 Получатель TON\nУкажите свой @username"
    elif method == "usdt":
        text = "💰 Создание сделки с оплатой в USDT\n\n🏦 Получатель USDT\nУкажите свой @username"
    elif method == "sbp":
        text = "💰 Создание сделки с оплатой через СБП\n\n📱 Ваш номер СБП готов к использованию\nУкажите свой @username"
    
    await callback.message.edit_text(text)
    
    await state.set_state(DealCreation.seller_username)

@router.message(DealCreation.seller_username)
async def process_seller_username(message: Message, state: FSMContext):
    username = message.text.strip()
    
    if not username.startswith("@"):
        await message.answer("❌ Username должен начинаться с @. Попробуйте снова.")
        return
    
    username_without_at = username[1:]
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username_without_at):
        await message.answer(
            "❌ Username может содержать только буквы, цифры и символ подчеркивания (_).\n"
            "Пожалуйста, введите корректный @username."
        )
        return
    
    await state.update_data(seller_username=username)
    
    data = await state.get_data()
    method = data.get("payment_method")
    
    text = ""
    if method == "stars":
        text = f"✅ Получатель: {username}\n\n💰 Минимальная сумма: 100 звезд\n\nВведите сумму в звездах:"
    elif method == "card":
        text = f"✅ Получатель: {username}\n\n💰 Мимальная сумма: 100 рублей\n\nВведите сумму в рублях:"
    elif method == "ton":
        text = f"✅ Получатель: {username}\n\n💰 Минимальная сумма: 1 TON\n\nВведите сумму в TON:"
    elif method == "usdt":
        text = f"✅ Получатель: {username}\n\n💰 Минимальная сумма: 10 USDT\n\nВведите сумму в USDT:"
    elif method == "sbp":
        text = f"✅ Получатель: {username}\n\n💰 Минимальная сумма: 100 рублей\n\nВведите сумму в рублях:"
    
    await message.answer(text)
    
    await state.set_state(DealCreation.amount)

@router.message(DealCreation.amount)
async def process_amount(message: Message, state: FSMContext):
    try:
        amount_text = message.text.replace(',', '.')
        amount = float(amount_text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введите корректное положительное число.")
        return
    
    data = await state.get_data()
    method = data.get("payment_method")
    
    min_amounts = {"stars": 100, "card": 100, "ton": 1, "usdt": 10, "sbp": 100}
    min_amount = min_amounts.get(method, 0)
    
    if method in min_amounts and amount < min_amount:
        currency_names = {"stars": "звезд", "card": "рублей", "ton": "TON", "usdt": "USDT", "sbp": "рублей"}
        currency = currency_names.get(method, "")
        await message.answer(f"❌ Минимальная сумма - {min_amount} {currency}. Введите сумму еще раз:")
        return

    await state.update_data(amount=amount)
    
    await message.answer(
        "📝 Укажите, что вы предлагаете в этой сделке\n\n"
        "Пример: 10 Кепок и Пепочка\n\n"
        "Отправьте описание товара или услуги:"
    )
    
    await state.set_state(DealCreation.description)

@router.message(DealCreation.description)
async def process_description(message: Message, state: FSMContext):
    description = message.text
    data = await state.get_data()
    
    seller_username = data["seller_username"]
    amount = data["amount"]
    method = data["payment_method"]
    
    wallets = get_user_wallets(message.from_user.id)
    
    deal_id, buyer_code, seller_code = create_deal(
        buyer_id=message.from_user.id,
        seller_username=seller_username,
        amount=amount,
        description=description,
        method=method
    )
    
    bot_username = "pIayerokofcbot"
    deal_link = f"https://t.me/{bot_username}?start=deal_{deal_id}"
    
    if method == "stars":
        await message.answer(
            f"✅ Сделка успешно создана!\n\n"
            f"💰 Сумма: {amount} ⭐️ stars\n"
            f"📜 Описание: {description}\n"
            f"💳 Ваши реквизиты: {seller_username}\n"
            f"🔗 Ссылка для покупателя: {deal_link}\n"
            f"🔑 ID сделки: {deal_id}",
            reply_markup=main_menu_keyboard()
        )
    elif method == "card":
        card_info = ""
        if wallets and wallets[3]:
            card_number = ' '.join([wallets[3][i:i+4] for i in range(0, 16, 4)])
            card_info = f"📄 Карта: {card_number}\n👤 Владелец: {wallets[4]}\n🏦 Банк: {wallets[5]}"
        else:
            card_info = "❌ Карта не добавлена. Сначала добавьте её в настройках."
        
        await message.answer(
            f"✅ Сделка успешно создана!\n\n"
            f"💰 Сумма: {amount} ₽\n"
            f"📜 Описание: {description}\n"
            f"💳 Ваши реквизиты:\n{card_info}\n"
            f"🔗 Ссылка для покупателя: {deal_link}\n"
            f"🔑 ID сделки: {deal_id}",
            reply_markup=main_menu_keyboard()
        )
    elif method == "ton":
        ton_info = f"🏠 TON кошелек: {wallets[1]}" if wallets and wallets[1] else "❌ TON кошелек не добавлен."
        
        await message.answer(
            f"✅ Сделка успешно создана!\n\n"
            f"💰 Сумма: {amount} 🪙 TON\n"
            f"📜 Описание: {description}\n"
            f"💳 Ваши реквизиты:\n{ton_info}\n"
            f"🔗 Ссылка для покупателя: {deal_link}\n"
            f"🔑 ID сделки: {deal_id}",
            reply_markup=main_menu_keyboard()
        )
    elif method == "usdt":
        usdt_info = f"💰 USDT кошелек: {wallets[2]}" if wallets and wallets[2] else "❌ USDT кошелек не добавлен."
        
        await message.answer(
            f"✅ Сделка успешно создана!\n\n"
            f"💰 Сумма: {amount} 💰 USDT\n"
            f"📜 Описание: {description}\n"
            f"💳 Ваши реквизиты:\n{usdt_info}\n"
            f"🔗 Ссылка для покупателя: {deal_link}\n"
            f"🔑 ID сделки: {deal_id}",
            reply_markup=main_menu_keyboard()
        )
    elif method == "sbp":
        sbp_info = ""
        if wallets and wallets[6] and wallets[7]:
            sbp_info = f"📱 Номер: {wallets[6]}\n👤 Получатель: {wallets[7]}"
        else:
            sbp_info = "❌ СБП не добавлен. Сначала добавьте номер в настройках."
        
        await message.answer(
            f"✅ Сделка успешно создана!\n\n"
            f"💰 Сумма: {amount} ₽\n"
            f"📜 Описание: {description}\n"
            f"💳 Ваши реквизиты СБП:\n{sbp_info}\n"
            f"🔗 Ссылка для покупателя: {deal_link}\n"
            f"🔑 ID сделки: {deal_id}",
            reply_markup=main_menu_keyboard()
        )
    
    seller_id = message.from_user.id
    set_seller_id(deal_id, seller_id)
    print(f"✅ Сохранен seller_id {seller_id} для сделки {deal_id}")
    
    await state.clear()

# ============== ОБРАБОТЧИК ПЕРЕДАЧИ ПОДАРКА ==============
@router.callback_query(F.data.startswith("gift_transferred_"))
async def gift_transferred(callback: CallbackQuery):
    deal_id = callback.data.replace("gift_transferred_", "")
    deal = get_deal_by_id(deal_id)
    if not deal:
        await callback.answer("Сделка не найдена.")
        return

    update_deal_status(deal_id, "awaiting_verification")

    seller_id = deal[4]
    seller_username = deal[3]
    amount = float(deal[5]) if deal[5] else 0
    description = deal[6] if deal[6] else "Не указано"
    
    await callback.message.edit_text(
        f"✅ Спасибо! Подарок отмечен как переданный.\n\n"
        f"Ожидайте проверки выполнения всех условий менеджером.\n"
        f"Средства будут зачислены после подтверждения."
    )

    for admin_id in ADMIN_IDS:
        try:
            await callback.bot.send_message(
                admin_id,
                f"📦 Продавец передал подарок по сделке!\n\n"
                f"🔹 Номер сделки: #{deal_id}\n"
                f"🔹 Продавец: {seller_username}\n"
                f"🔹 Сумма: {amount} {'⭐️' if deal[8] == 'stars' else '₽'}\n"
                f"🔹 Описание: {description}\n\n"
                f"Необходимо проверить выполнение условий и подтвердить получение."
            )
        except Exception as e:
            print(f"Ошибка отправки админу: {e}")

    await callback.answer()

# ============== КОМАНДА CONFIRM ==============
@router.message(Command("confirm"))
async def confirm_code(message: Message):
    args = message.text.split()
    if len(args) != 2:
        await message.answer("❌ Использование: /confirm <код>")
        return

    code = args[1]
    deal = get_deal_by_buyer_code(code)

    if not deal:
        await message.answer("❌ Неверный код.")
        return
    
    if deal[9] != "payment_confirmed":
        await message.answer("❌ Сделка не в статусе ожидания подтверждения.")
        return

    update_deal_status(deal[1], "awaiting_seller_confirmation")

    if deal[4]:
        try:
            await message.bot.send_message(
                deal[4],
                f"🔔 Покупатель ввел код по сделке #{deal[1]}!\n\n"
                f"Пожалуйста, подтвердите, что товар передан покупателю.",
                reply_markup=seller_confirm_receipt_keyboard(deal[1])
            )
        except:
            pass

    await message.answer(
        "✅ Код принят! Продавец получил запрос на подтверждение.\n"
        "Ожидайте, пока продавец подтвердит получение товара."
    )

# ============== ПОДТВЕРЖДЕНИЕ ПРОДАВЦА ==============
@router.callback_query(F.data.startswith("seller_confirm_"))
async def seller_confirm_receipt(callback: CallbackQuery):
    deal_id = callback.data.replace("seller_confirm_", "")
    deal = get_deal_by_id(deal_id)
    if not deal:
        await callback.answer("Сделка не найдена.")
        return

    update_deal_status(deal_id, "completed")

    if deal[2]:
        try:
            await callback.bot.send_message(
                deal[2],
                f"✅ Сделка #{deal_id} успешно завершена!\n\nСпасибо за использование нашего сервиса!"
            )
        except:
            pass

    for admin_id in ADMIN_IDS:
        try:
            await callback.bot.send_message(
                admin_id,
                f"🏁 Сделка #{deal_id} завершена!\n\n"
                f"🔹 Продавец: {deal[3]}\n"
                f"🔹 Сумма: {deal[5]} {'⭐️' if len(deal) > 10 and deal[10] == 'stars' else '₽'}\n"
                f"🔹 Описание: {deal[6]}\n\n"
                f"💰 Отправьте {'звезды' if len(deal) > 10 and deal[10] == 'stars' else 'деньги'} продавцу."
            )
        except:
            pass

    await callback.message.edit_text(
        "✅ Спасибо! Сделка завершена. Ожидайте перевода от администратора."
    )

# ============== ОБРАБОТЧИКИ ДЛЯ КОШЕЛЬКОВ ==============
@router.callback_query(F.data == "wallet_settings")
async def wallet_settings(callback: CallbackQuery):
    await callback.message.edit_text(
        "👛 Выберите способ оплаты:\n\nВы можете добавить или изменить ваши кошельки для получения платежей:",
        reply_markup=wallet_menu_keyboard()
    )

@router.callback_query(F.data == "wallet_ton")
async def add_ton_wallet(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("⏱ Добавление TON кошелька\n\nВведите адрес вашего TON кошелька:")
    await state.set_state(WalletStates.waiting_for_ton)

@router.message(WalletStates.waiting_for_ton)
async def process_ton_wallet(message: Message, state: FSMContext):
    ton_wallet = message.text.strip()
    
    if len(ton_wallet) < 20 or not (ton_wallet.startswith('EQ') or ton_wallet.startswith('UQ')):
        await message.answer("❌ Неверный формат TON кошелька. Попробуйте снова:")
        return
    
    update_ton_wallet(message.from_user.id, ton_wallet)
    await message.answer(f"✅ TON кошелек успешно сохранен!\n\nАдрес: {ton_wallet}", reply_markup=wallet_menu_keyboard())
    await state.clear()

@router.callback_query(F.data == "wallet_usdt")
async def add_usdt_wallet(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("💳 Добавление USDT кошелька\n\nВведите адрес вашего USDT кошелька (TRC20):")
    await state.set_state(WalletStates.waiting_for_usdt)

@router.message(WalletStates.waiting_for_usdt)
async def process_usdt_wallet(message: Message, state: FSMContext):
    usdt_wallet = message.text.strip()
    
    if len(usdt_wallet) < 30 or not usdt_wallet.startswith('T'):
        await message.answer("❌ Неверный формат USDT кошелька. Попробуйте снова:")
        return
    
    update_usdt_wallet(message.from_user.id, usdt_wallet)
    await message.answer(f"✅ USDT кошелек успешно сохранен!\n\nАдрес: {usdt_wallet}", reply_markup=wallet_menu_keyboard())
    await state.clear()

@router.callback_query(F.data == "wallet_card")
async def add_card_wallet(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📄 Добавление банковской карты\n\nВведите номер карты (16 цифр):\n(например: 1234567890123456)")
    await state.set_state(WalletStates.waiting_for_card_number)

@router.message(WalletStates.waiting_for_card_number)
async def process_card_number(message: Message, state: FSMContext):
    card_number = message.text.strip().replace(' ', '').replace('-', '')
    
    if not card_number.isdigit() or len(card_number) != 16:
        await message.answer("❌ Неверный формат номера карты. Введите 16 цифр без пробелов:")
        return
    
    await state.update_data(card_number=card_number)
    await message.answer("Введите имя владельца карты (как на карте):")
    await state.set_state(WalletStates.waiting_for_card_holder)

@router.message(WalletStates.waiting_for_card_holder)
async def process_card_holder(message: Message, state: FSMContext):
    card_holder = message.text.strip().upper()
    
    if len(card_holder) < 3:
        await message.answer("❌ Слишком короткое имя. Введите полное имя владельца:")
        return
    
    await state.update_data(card_holder=card_holder)
    await message.answer("Введите название банка:")
    await state.set_state(WalletStates.waiting_for_card_bank)

@router.message(WalletStates.waiting_for_card_bank)
async def process_card_bank(message: Message, state: FSMContext):
    card_bank = message.text.strip()
    data = await state.get_data()
    
    update_card_wallet(message.from_user.id, data['card_number'], data['card_holder'], card_bank)
    
    card_number_formatted = ' '.join([data['card_number'][i:i+4] for i in range(0, 16, 4)])
    
    await message.answer(
        f"✅ Банковская карта успешно сохранена!\n\n"
        f"💳 Номер: {card_number_formatted}\n"
        f"👤 Владелец: {data['card_holder']}\n"
        f"🏦 Банк: {card_bank}",
        reply_markup=wallet_menu_keyboard()
    )
    await state.clear()

# ============== ОБРАБОТЧИКИ ДЛЯ СБП ==============
@router.callback_query(F.data == "wallet_sbp")
async def add_sbp_wallet(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📱 Добавление СБП\n\nВведите номер телефона для СБП (в формате 79991234567 или +79991234567):"
    )
    await state.set_state(WalletStates.waiting_for_sbp_number)

@router.message(WalletStates.waiting_for_sbp_number)
async def process_sbp_number(message: Message, state: FSMContext):
    phone = message.text.strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    phone_pattern = re.compile(r'^(\+7|7|8)?[\d]{10}$')
    if not phone_pattern.match(phone):
        await message.answer(
            "❌ Неверный формат номера телефона.\n\n"
            "Введите номер в формате:\n"
            "• 79991234567\n"
            "• +79991234567\n"
            "• 89991234567\n\n"
            "Попробуйте снова:"
        )
        return
    
    if phone.startswith('+'):
        phone = phone[1:]
    if phone.startswith('8') and len(phone) == 11:
        phone = '7' + phone[1:]
    
    await state.update_data(sbp_number=phone)
    await message.answer("Введите имя получателя для СБП (как в банке):")
    await state.set_state(WalletStates.waiting_for_sbp_name)

@router.message(WalletStates.waiting_for_sbp_name)
async def process_sbp_name(message: Message, state: FSMContext):
    sbp_name = message.text.strip().upper()
    data = await state.get_data()
    
    if len(sbp_name) < 3:
        await message.answer("❌ Слишком короткое имя. Введите полное имя получателя:")
        return
    
    update_sbp_wallet(message.from_user.id, data['sbp_number'], sbp_name)
    
    await message.answer(
        f"✅ СБП успешно сохранен!\n\n"
        f"📱 Номер: {data['sbp_number']}\n"
        f"👤 Получатель: {sbp_name}",
        reply_markup=wallet_menu_keyboard()
    )
    await state.clear()

@router.callback_query(F.data == "wallet_stars")
async def stars_info(callback: CallbackQuery):
    await callback.message.edit_text(
        "⭐️ Звезды Telegram\n\nДля получения оплаты звездами:\n"
        "1. Покупатель отправляет звезды через @stars_bot\n"
        "2. Вы получаете уведомление о переводе\n"
        "3. Звезды автоматически конвертируются в рубли\n\nКомиссия Telegram: 5%",
        reply_markup=wallet_menu_keyboard()
    )

@router.callback_query(F.data.startswith("view_"))
async def view_wallet(callback: CallbackQuery):
    wallet_type = callback.data.split("_")[1]
    wallets = get_user_wallets(callback.from_user.id)
    
    if not wallets or all(v is None for v in wallets[1:]):
        await callback.message.edit_text(
            "❌ У вас пока нет сохраненных кошельков.",
            reply_markup=wallet_menu_keyboard()
        )
        return
    
    text = ""
    if wallet_type == "ton" and wallets[1]:
        text = f"⏱ Ваш TON кошелек:\n\n{wallets[1]}"
    elif wallet_type == "usdt" and wallets[2]:
        text = f"💳 Ваш USDT кошелек:\n\n{wallets[2]}"
    elif wallet_type == "card" and wallets[3]:
        card_number = ' '.join([wallets[3][i:i+4] for i in range(0, 16, 4)])
        text = f"📄 Ваша банковская карта:\n\n💳 Номер: {card_number}\n👤 Владелец: {wallets[4]}\n🏦 Банк: {wallets[5]}"
    elif wallet_type == "sbp" and wallets[6] and wallets[7]:
        text = f"📱 Ваш СБП:\n\n📱 Номер: {wallets[6]}\n👤 Получатель: {wallets[7]}"
    elif wallet_type == "stars":
        text = "⭐️ Звезды Telegram\n\nДля получения оплаты звездами ничего добавлять не нужно."
    else:
        text = f"❌ {wallet_type.upper()} кошелек не добавлен."
    
    await callback.message.edit_text(text, reply_markup=wallet_view_keyboard())

# ============== АДМИН ПАНЕЛЬ ==============
@router.callback_query(F.data == "admin_active_deals")
async def admin_active_deals(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет доступа.")
        return

    deals = get_active_deals()
    if not deals:
        await callback.message.edit_text("📭 Нет активных сделок.")
        return

    text = "📋 Активные сделки:\n\n"
    for deal in deals:
        status_emoji = {
            "waiting_for_payment": "⏳",
            "payment_confirmed": "✅",
            "awaiting_verification": "⏱️",
            "awaiting_seller_confirmation": "🔑",
            "completed": "🎉"
        }.get(deal[9], "📌")
        
        text += f"{status_emoji} #{deal[1]}\n"
        text += f"   Сумма: {deal[5]} {'⭐️' if len(deal) > 10 and deal[10] == 'stars' else '₽'}\n"
        text += f"   Статус: {deal[9]}\n"
        text += f"   Покупатель: {deal[2]}\n"
        text += f"   Продавец: {deal[3]}\n\n"

    await callback.message.edit_text(text)

@router.callback_query(F.data == "admin_history")
async def admin_history(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Нет доступа.")
        return

    deals = get_all_deals()
    if not deals:
        await callback.message.edit_text("📭 История сделок пуста.")
        return

    text = "📜 История всех сделок:\n\n"
    for deal in deals[:10]:
        status_emoji = "✅" if deal[9] == "completed" else "❌"
        text += f"{status_emoji} #{deal[1]}\n"
        text += f"   Сумма: {deal[5]} {'⭐️' if len(deal) > 10 and deal[10] == 'stars' else '₽'}\n"
        text += f"   Статус: {deal[9]}\n"
        text += f"   Дата: {deal[0]}\n\n"

    await callback.message.edit_text(text)
