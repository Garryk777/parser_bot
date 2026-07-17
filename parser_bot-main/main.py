import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

import database

import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

database.init_db()

# --- Клавиатура для клиентов (главное меню) ---
def client_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Меню")],
            [KeyboardButton(text="📊 Статус")],
            [KeyboardButton(text="💳 Оплата")],
            [KeyboardButton(text="💬 Поддержка")]
        ],
        resize_keyboard=True
    )

# --- Админ-клавиатура ---
def admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Все клиенты")],
            [KeyboardButton(text="➕ Добавить клиента")],
            [KeyboardButton(text="✏️ Добавить слово")],
            [KeyboardButton(text="🗑 Удалить клиента")],
            [KeyboardButton(text="📋 Список чатов")],
            [KeyboardButton(text="🔙 Выйти из админки")]
        ],
        resize_keyboard=True
    )

# --- Клиентский /start ---
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать в бот *Мониторинг чатов*!\n\n"
        "🔍 Я отслеживаю сообщения в чатах по ключевым словам и мгновенно присылаю уведомления.\n\n"
        "📍 *На данный момент:*\n"
        "— Мониторинг чатов по острову *Пхукет* (Таиланд)\n"
        "— В ближайшее время будут добавляться *новые города и страны*!\n\n"
        "📌 *Как подключиться:*\n"
        "1. Напиши администратору: @suppmonitorchats\n"
        "2. Он добавит твой Telegram ID и настроит подписку\n"
        "3. Ты начнёшь получать уведомления по выбранным темам\n\n"
        "📌 *Возможности:*\n"
        "— Мгновенные уведомления по ключевым словам\n"
        "— Индивидуальные подписки\n"
        "— Мониторинг 50+ чатов\n\n"
        "🔒 *Безопасно и конфиденциально*\n"
        "— Данные не передаются третьим лицам\n"
        "— Можно отписаться в любой момент\n\n"
        "🌍 *Присоединяйтесь — мы расширяемся!*\n"
        "💬 По вопросам: @suppmonitorchats",
        reply_markup=client_keyboard(),
        parse_mode="Markdown"
    )

# --- Главное меню (/menu) ---
@dp.message(Command("menu"))
async def menu(message: types.Message):
    await message.answer(
        "✅ Вы в главном меню.\n\n"
        "📋 *Доступные команды:*\n"
        "/start — приветствие\n"
        "/menu — главное меню\n"
        "/status — статус подписки\n"
        "/pay — оплата\n"
        "/help — поддержка\n\n"
        "💬 По вопросам: @suppmonitorchats",
        parse_mode="Markdown"
    )


# --- Статус подписки (/status) ---
@dp.message(Command("status"))
async def status(message: types.Message):
    user_id = message.from_user.id
    subs = database.get_user_subs(user_id)

    if not subs:
        await message.answer("У тебя нет активных подписок.")
        return

    text = "📊 *Твои подписки:*\n\n"
    for sub in subs:
        status_text = "✅ Активна" if sub["days_left"] > 0 else "❌ Истекла"
        text += (
            f"📌 *{sub['topic']}*\n"
            f"   🔑 Слова: {', '.join(sub['keywords']) if sub['keywords'] else 'нет'}\n"
            f"   ⏳ Осталось: {sub['days_left']} дней\n"
            f"   📊 Статус: {status_text}\n\n"
        )

    await message.answer(text, parse_mode="Markdown")

# --- Поддержка (/help) ---
@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "💬 <b>Поддержка</b>\n\n"
        "Если у вас возникли вопросы или трудности, напишите в службу поддержки:\n"
        "@suppmonitorchats\n\n"
        "📌 <b>Команды:</b>\n"
        "/start — приветствие\n"
        "/menu — главное меню\n"
        "/status — статус подписки\n"
        "/help — поддержка",
        parse_mode="HTML"
    )

@dp.message(Command("pay"))
async def pay(message: types.Message):
    await message.answer(
        "💳 *Оплата подписки*\n\n"
        "📌 *Почему USDT?*\n"
        "Из-за нестабильности курсов и для удобства международных переводов, "
        "оплата принимается только в *USDT* (сеть TRC-20 или BEP-20).\n\n"
        "🎁 *Бесплатный период:*\n"
        "— 3 дня бесплатно (тестовый доступ)\n\n"
        "💰 *Тарифы:*\n"
        "🔹 1 месяц — *10 USDT*\n"
        "🔹 2 месяца — *18 USDT* (экономия 2 USDT)\n"
        "🔹 3 месяца — *25 USDT* (экономия 5 USDT)\n\n"
        "📌 *Что вы получаете:*\n"
        "✅ Мгновенные уведомления по ключевым словам\n"
        "✅ Индивидуальные подписки\n"
        "✅ Мониторинг 50+ чатов\n"
        "✅ Приоритетная поддержка\n\n"
        "🌍 *Расширение географии:*\n"
        "В ближайшее время будут добавляться *новые города и страны*! "
        "Стоимость подписки окупится с *одного клиента*.\n\n"
        "📌 *Как оплатить:*\n"
        "Напишите администратору: @suppmonitorchats\n"
        "Он отправит вам кошелёк для оплаты и активирует подписку после подтверждения.\n\n"
        "💬 По вопросам: @suppmonitorchats",
        parse_mode="Markdown"
    )


# --- Обработка кнопок клиентского меню ---
@dp.message(lambda msg: msg.text == "📋 Меню")
async def menu_btn(message: types.Message):
    await menu(message)

@dp.message(lambda msg: msg.text == "📊 Статус")
async def status_btn(message: types.Message):
    await status(message)

@dp.message(lambda msg: msg.text == "💬 Поддержка")
async def help_btn(message: types.Message):
    await help_command(message)

@dp.message(lambda msg: msg.text == "💳 Оплата")
async def pay_btn(message: types.Message):
    await pay(message)

# --- Админ-меню ---
@dp.message(Command("admin"))
async def admin_menu(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У вас нет прав.")
        return
    await message.answer(
        "👋 Админ-панель\n\n"
        "Используй кнопки ниже для управления",
        reply_markup=admin_keyboard()
    )

# --- Админ: список чатов ---
@dp.message(lambda msg: msg.text == "📋 Список чатов")
async def admin_list_chats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    chats = database.get_all_chats()
    if not chats:
        await message.answer("📭 Чаты пока не добавлены.")
        return
    await message.answer("📋 Чаты Пхукета:\n" + "\n".join(f"- {chat}" for chat in chats))

@dp.message(lambda msg: msg.text == "📋 Все клиенты")
async def admin_all_clients(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    clients = database.get_all_users_with_subs_detailed()

    if not clients:
        await message.answer("📭 Клиентов с подписками пока нет.")
        return

    text = "📋 *Все клиенты:*\n\n"
    for user_id, subs in clients.items():
        text += f"👤 ID: `{user_id}`\n"
        for sub in subs:
            status = "✅" if sub["days_left"] > 0 else "❌"
            text += f"   {status} {sub['topic']} — {sub['days_left']} дн.\n"
        text += "\n"

    await message.answer(text, parse_mode="Markdown")


# --- Админ: добавить клиента ---
@dp.message(lambda msg: msg.text == "➕ Добавить клиента")
async def admin_add_prompt(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(
        "Введите данные в формате:\n"
        "`ID_пользователя Тема`\n\n"
        "Пример:\n"
        "`123456789 обмен валюты`",
        reply_markup=ReplyKeyboardRemove()
    )

# --- Админ: добавить слово ---
@dp.message(lambda msg: msg.text == "✏️ Добавить слово")
async def admin_add_word_prompt(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(
        "Введите данные в формате:\n"
        "`ID_пользователя Номер_подписки Слово`\n\n"
        "Пример:\n"
        "`123456789 1 обмен`",
        reply_markup=ReplyKeyboardRemove()
    )

# --- Админ: удалить клиента ---
@dp.message(lambda msg: msg.text == "🗑 Удалить клиента")
async def admin_delete_prompt(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(
        "Введите ID пользователя для удаления всех его подписок:\n"
        "Пример: `123456789`",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(Command("admin_add_days"))
async def admin_add_days(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()
    if len(parts) < 4:
        await message.answer("Пример: /admin_add_days 123456789 обмен валюты 30")
        return

    try:
        user_id = int(parts[1])
        days = int(parts[-1])  # последнее слово — это дни
    except ValueError:
        await message.answer("ID и количество дней должны быть числами")
        return

    # Все слова с 2-го по предпоследнее — это тема
    topic = " ".join(parts[2:-1])

    if not topic:
        await message.answer("Введите тему подписки")
        return

    database.create_subscription(user_id, topic, days)

    subs = database.get_user_subs(user_id)
    sub_id = subs[-1]["id"]

    await message.answer(
        f"✅ Подписка создана для пользователя {user_id}\n"
        f"📌 Тема: {topic}\n"
        f"📅 Дней: {days}\n"
        f"🆔 Номер подписки: {sub_id}"
    )

@dp.message(Command("admin_set_days"))
async def admin_set_days(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()
    if len(parts) < 4:
        await message.answer("Пример: /admin_set_days 123456789 1 30")
        return

    try:
        user_id = int(parts[1])
        sub_id = int(parts[2])
        days = int(parts[3])
    except ValueError:
        await message.answer("ID, номер подписки и дни должны быть числами")
        return

    subs = database.get_user_subs(user_id)
    if not any(s["id"] == sub_id for s in subs):
        await message.answer("❌ Подписка не найдена")
        return

    import time
    new_expires = int(time.time()) + days * 86400
    conn = sqlite3.connect("subscriptions.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE subscriptions SET expires_at = ? WHERE id = ?", (new_expires, sub_id))
    conn.commit()
    conn.close()

    await message.answer(f"✅ Для подписки {sub_id} установлено {days} дней")


@dp.message(Command("admin_list"))
async def admin_list(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Пример: /admin_list 123456789")
        return

    try:
        user_id = int(parts[1])
    except ValueError:
        await message.answer("ID должен быть числом")
        return

    subs = database.get_user_subs(user_id)

    if not subs:
        await message.answer(f"У пользователя {user_id} нет подписок.")
        return

    text = f"📋 *Подписки пользователя {user_id}:*\n\n"
    for sub in subs:
        status_text = "✅ Активна" if sub["days_left"] > 0 else "❌ Истекла"
        text += (
            f"📌 *{sub['topic']}*\n"
            f"   🔑 Слова: {', '.join(sub['keywords']) if sub['keywords'] else 'нет'}\n"
            f"   ⏳ Осталось: {sub['days_left']} дней\n"
            f"   📊 Статус: {status_text}\n"
            f"   🆔 Номер: {sub['id']}\n\n"
        )

    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("admin_remove_word"))
async def admin_remove_word(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split(maxsplit=3)
    if len(parts) < 4:
        await message.answer("Пример: /admin_remove_word 123456789 1 обмен")
        return

    try:
        user_id = int(parts[1])
        sub_id = int(parts[2])
    except ValueError:
        await message.answer("ID и номер подписки должны быть числами")
        return

    keyword = parts[3].strip()

    subs = database.get_user_subs(user_id)
    if not any(s["id"] == sub_id for s in subs):
        await message.answer("❌ Подписка не найдена")
        return

    # Проверяем, есть ли такое слово
    sub = next(s for s in subs if s["id"] == sub_id)
    if keyword not in sub["keywords"]:
        await message.answer(f"❌ Слово '{keyword}' не найдено в этой подписке")
        return

    database.delete_keyword(sub_id, keyword)
    await message.answer(f"✅ Слово '{keyword}' удалено из подписки {sub_id}")


@dp.message(Command("admin_edit_topic"))
async def admin_edit_topic(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split(maxsplit=3)
    if len(parts) < 4:
        await message.answer("Пример: /admin_edit_topic 123456789 1 новая тема")
        return

    try:
        user_id = int(parts[1])
        sub_id = int(parts[2])
    except ValueError:
        await message.answer("ID и номер подписки должны быть числами")
        return

    new_topic = parts[3].strip()

    subs = database.get_user_subs(user_id)
    if not any(s["id"] == sub_id for s in subs):
        await message.answer("❌ Подписка не найдена")
        return

    database.update_subscription_topic(sub_id, new_topic)
    await message.answer(f"✅ Тема изменена на: {new_topic}")


@dp.message(Command("admin_delete_all"))
async def admin_delete_all(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Пример: /admin_delete_all 123456789")
        return

    try:
        user_id = int(parts[1])
    except ValueError:
        await message.answer("ID должен быть числом")
        return

    subs = database.get_user_subs(user_id)
    if not subs:
        await message.answer(f"У пользователя {user_id} нет подписок.")
        return

    for sub in subs:
        database.delete_subscription(sub["id"])

    await message.answer(f"✅ Все подписки пользователя {user_id} удалены.")

@dp.message(Command("admin_add_full"))
async def admin_add_full(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("Пример: /admin_add_full 123456789 обмен, валюта, баты")
        return

    try:
        user_id = int(parts[1])
    except ValueError:
        await message.answer("ID должен быть числом")
        return

    keywords = [kw.strip() for kw in parts[2].split(",")]

    # Создаём подписку
    database.create_subscription(user_id, "Индивидуальный запрос")
    subs = database.get_user_subs(user_id)
    sub_id = subs[-1]["id"]

    # Добавляем все ключевые слова
    for kw in keywords:
        database.add_keyword(sub_id, kw)

    await message.answer(
        f"✅ Подписка создана для пользователя {user_id}\n"
        f"🔑 Слова: {', '.join(keywords)}"
    )

# --- Обработчик инлайн-кнопок ---
@dp.callback_query()
async def handle_inline_buttons(call: types.CallbackQuery):
    await call.answer()  # убирает "часики" на кнопке

    if call.data == "info":
        await call.message.edit_text("ℹ️ Информация о боте будет здесь.")
    elif call.data == "subscribe":
        await call.message.edit_text("✅ Вы подписаны на обновления!")
    else:
        await call.message.edit_text("⚠️ Неизвестная команда.")


# --- Админ: выйти ---
@dp.message(lambda msg: msg.text == "🔙 Выйти из админки")
async def admin_exit(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(
        "👋 Вы вышли из админ-панели.",
        reply_markup=ReplyKeyboardRemove()
    )

# --- Обработка текстового ввода (админ) ---
@dp.message()
async def handle_admin_input(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.strip()
    parts = text.split()

    # Формат: ID Тема → создание подписки
    if len(parts) == 2 and parts[0].isdigit():
        user_id = int(parts[0])
        topic = parts[1]
        subs = database.get_user_subs(user_id)
        for sub in subs:
            if sub["topic"].lower() == topic.lower():
                await message.answer(f"❌ У пользователя уже есть подписка на тему '{topic}'", reply_markup=admin_keyboard())
                return
        database.create_subscription(user_id, topic)
        await message.answer(f"✅ Подписка на тему '{topic}' добавлена пользователю {user_id}", reply_markup=admin_keyboard())
        return

    # Формат: ID Номер Слово → добавление слова
    if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
        user_id = int(parts[0])
        sub_id = int(parts[1])
        keyword = parts[2]
        subs = database.get_user_subs(user_id)
        if not any(s["id"] == sub_id for s in subs):
            await message.answer("❌ Подписка с таким номером не найдена.", reply_markup=admin_keyboard())
            return
        database.add_keyword(sub_id, keyword)
        await message.answer(f"✅ Слово '{keyword}' добавлено к подписке {sub_id}", reply_markup=admin_keyboard())
        return

    # Формат: ID → удаление всех подписок пользователя
    if len(parts) == 1 and parts[0].isdigit():
        user_id = int(parts[0])
        subs = database.get_user_subs(user_id)
        if not subs:
            await message.answer("У этого пользователя нет подписок.", reply_markup=admin_keyboard())
            return
        for sub in subs:
            database.delete_subscription(sub["id"])
        await message.answer(f"✅ Все подписки пользователя {user_id} удалены.", reply_markup=admin_keyboard())
        return

    await message.answer("Неверный формат. Попробуйте снова.", reply_markup=admin_keyboard())

# --- Запуск ---
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())