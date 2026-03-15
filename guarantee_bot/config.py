import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Безопасное получение ADMIN_IDS с проверкой
admin_ids_str = os.getenv("ADMIN_IDS")
if admin_ids_str and admin_ids_str.strip():
    try:
        ADMIN_IDS = list(map(int, admin_ids_str.split(",")))
        print(f"✅ ADMIN_IDS загружены: {ADMIN_IDS}")
    except ValueError:
        ADMIN_IDS = []
        print(f"⚠️ Ошибка в формате ADMIN_IDS: {admin_ids_str}")
else:
    ADMIN_IDS = []  # Пустой список, если переменная не задана
    print("⚠️ ADMIN_IDS не задан, функции админа будут недоступны")

# Для отладки (можно удалить после проверки)
print(f"🤖 BOT_TOKEN: {'✅ загружен' if BOT_TOKEN else '❌ не загружен'}")
print(f"👤 ADMIN_IDS: {ADMIN_IDS}")
