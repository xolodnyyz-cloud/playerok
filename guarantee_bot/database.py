import sqlite3
import random
import string
from datetime import datetime

DB_PATH = "bot_database.db"

# ============== ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ ==============
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Таблица сделок
    c.execute('''
        CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deal_id TEXT UNIQUE,
            buyer_id INTEGER,
            seller_username TEXT,
            seller_id INTEGER,
            amount REAL,
            description TEXT,
            buyer_code TEXT,
            seller_code TEXT,
            status TEXT DEFAULT 'waiting_for_payment',
            payment_method TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица кошельков
    c.execute('''
        CREATE TABLE IF NOT EXISTS wallets (
            user_id INTEGER PRIMARY KEY,
            ton_wallet TEXT,
            usdt_wallet TEXT,
            card_number TEXT,
            card_holder TEXT,
            card_bank TEXT,
            sbp_number TEXT,
            sbp_name TEXT
        )
    ''')
    
    # Таблица балансов
    c.execute('''
        CREATE TABLE IF NOT EXISTS balances (
            user_id INTEGER PRIMARY KEY,
            rub REAL DEFAULT 0,
            stars REAL DEFAULT 0,
            usdt REAL DEFAULT 0,
            ton REAL DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ База данных инициализирована")

# ============== ГЕНЕРАЦИЯ ID ==============
def generate_deal_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# ============== РАБОТА СДЕЛОК ==============
def create_deal(buyer_id, seller_username, amount, description, method):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    deal_id = generate_deal_id()
    buyer_code = generate_code()
    seller_code = generate_code()
    
    c.execute('''
        INSERT INTO deals (deal_id, buyer_id, seller_username, amount, description, buyer_code, seller_code, payment_method)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (deal_id, buyer_id, seller_username, amount, description, buyer_code, seller_code, method))
    
    conn.commit()
    conn.close()
    
    return deal_id, buyer_code, seller_code

def get_deal_by_id(deal_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT * FROM deals WHERE deal_id = ?', (deal_id,))
    result = c.fetchone()
    conn.close()
    
    return result

def get_deal_by_buyer_code(code):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT * FROM deals WHERE buyer_code = ?', (code,))
    result = c.fetchone()
    conn.close()
    
    return result

def update_deal_status(deal_id, status):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('UPDATE deals SET status = ? WHERE deal_id = ?', (status, deal_id))
    
    conn.commit()
    conn.close()
    print(f"✅ Статус сделки {deal_id} обновлен на {status}")

def set_seller_id(deal_id, seller_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('UPDATE deals SET seller_id = ? WHERE deal_id = ?', (seller_id, deal_id))
    
    conn.commit()
    conn.close()
    print(f"✅ seller_id {seller_id} сохранен для сделки {deal_id}")

def get_active_deals():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM deals 
        WHERE status IN ('waiting_for_payment', 'payment_confirmed', 'awaiting_verification', 'awaiting_seller_confirmation')
        ORDER BY created_at DESC
    ''')
    
    result = c.fetchall()
    conn.close()
    
    return result

def get_all_deals():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT * FROM deals ORDER BY created_at DESC')
    result = c.fetchall()
    conn.close()
    
    return result

# ============== РАБОТА С КОШЕЛЬКАМИ ==============
def get_user_wallets(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT ton_wallet, usdt_wallet, card_number, card_holder, card_bank, sbp_number, sbp_name 
        FROM wallets WHERE user_id = ?
    ''', (user_id,))
    
    result = c.fetchone()
    conn.close()
    
    if result:
        # Возвращаем кортеж в порядке: (ton, usdt, card_number, card_holder, card_bank, sbp_number, sbp_name)
        return (None, result[0], result[1], result[2], result[3], result[4], result[5], result[6])
    return None

def update_ton_wallet(user_id, ton_wallet):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO wallets (user_id, ton_wallet)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET ton_wallet = excluded.ton_wallet
    ''', (user_id, ton_wallet))
    
    conn.commit()
    conn.close()
    print(f"✅ TON кошелек сохранен для пользователя {user_id}")

def update_usdt_wallet(user_id, usdt_wallet):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO wallets (user_id, usdt_wallet)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET usdt_wallet = excluded.usdt_wallet
    ''', (user_id, usdt_wallet))
    
    conn.commit()
    conn.close()
    print(f"✅ USDT кошелек сохранен для пользователя {user_id}")

def update_card_wallet(user_id, card_number, card_holder, card_bank):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO wallets (user_id, card_number, card_holder, card_bank)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET 
            card_number = excluded.card_number,
            card_holder = excluded.card_holder,
            card_bank = excluded.card_bank
    ''', (user_id, card_number, card_holder, card_bank))
    
    conn.commit()
    conn.close()
    print(f"✅ Карта сохранена для пользователя {user_id}")

# ============== НОВАЯ ФУНКЦИЯ ДЛЯ СБП ==============
def update_sbp_wallet(user_id, phone_number, recipient_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO wallets (user_id, sbp_number, sbp_name)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            sbp_number = excluded.sbp_number,
            sbp_name = excluded.sbp_name
    ''', (user_id, phone_number, recipient_name))
    
    conn.commit()
    conn.close()
    print(f"✅ СБП сохранен для пользователя {user_id}: {phone_number}, {recipient_name}")

# ============== РАБОТА С БАЛАНСАМИ ==============
def get_user_balance(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('SELECT rub, stars, usdt, ton FROM balances WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return (user_id, result[0], result[1], result[2], result[3])
    return (user_id, 0, 0, 0, 0)

def add_rub(user_id, amount):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO balances (user_id, rub)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET rub = rub + excluded.rub
    ''', (user_id, amount))
    
    conn.commit()
    conn.close()
    print(f"✅ Добавлено {amount} RUB пользователю {user_id}")

def add_stars(user_id, amount):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO balances (user_id, stars)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET stars = stars + excluded.stars
    ''', (user_id, amount))
    
    conn.commit()
    conn.close()
    print(f"✅ Добавлено {amount} STARS пользователю {user_id}")

def add_usdt(user_id, amount):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO balances (user_id, usdt)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET usdt = usdt + excluded.usdt
    ''', (user_id, amount))
    
    conn.commit()
    conn.close()
    print(f"✅ Добавлено {amount} USDT пользователю {user_id}")

def add_ton(user_id, amount):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO balances (user_id, ton)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET ton = ton + excluded.ton
    ''', (user_id, amount))
    
    conn.commit()
    conn.close()
    print(f"✅ Добавлено {amount} TON пользователю {user_id}")

# Инициализация при импорте
init_db()