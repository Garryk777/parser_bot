import asyncio
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from config import API_ID, API_HASH, PHONE_NUMBER, BOT_TOKEN  # ← добавлен BOT_TOKEN
from database import get_all_subscriptions
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from chats import CHATS

bot = Bot(token=BOT_TOKEN)

# --- НАСТРОЙКИ ---
DELAY_BETWEEN_CHATS = 2
DELAY_BETWEEN_CYCLES = 5
LIMIT = 5

async def main():
    client = TelegramClient("session", API_ID, API_HASH)
    await client.start(phone=PHONE_NUMBER)
    print(f"✅ Парсер запущен. Мониторинг {len(CHATS)} чатов...")
    print(f"⏱️ Проверяем по {LIMIT} сообщений за раз")

    last_ids = {chat: 0 for chat in CHATS}

    while True:
        try:
            for chat in CHATS:
                try:
                    messages = await client.get_messages(chat, limit=LIMIT)

                    for msg in messages:
                        if msg.id <= last_ids.get(chat, 0):
                            continue

                        text = msg.text or ""

                        # --- ПОЛУЧЕНИЕ ОТПРАВИТЕЛЯ ---
                        if not msg.sender_id:
                            print("⚠️ Пропущено: нет отправителя")
                            last_ids[chat] = msg.id
                            continue

                        try:
                            sender = await client.get_entity(msg.sender_id)
                            sender_name = sender.first_name or "Пользователь"
                            sender_username = sender.username
                        except:
                            sender_name = "Неизвестный пользователь"
                            sender_username = None
                            print(f"⚠️ Неизвестный отправитель (ID: {msg.sender_id})")

                        # --- НАЗВАНИЕ ЧАТА ---
                        try:
                            chat_entity = await client.get_entity(chat)
                            chat_title = chat_entity.title or str(chat)
                        except:
                            chat_title = str(chat)

                        # --- ССЫЛКА НА СООБЩЕНИЕ ---
                        try:
                            chat_entity = await client.get_entity(chat)
                            if chat_entity.username:
                                message_link = f"https://t.me/{chat_entity.username}/{msg.id}"
                            else:
                                message_link = f"https://t.me/c/{chat_entity.id}/{msg.id}"
                        except:
                            message_link = f"https://t.me/c/{chat}/{msg.id}"

                        # --- ИМЯ (кликабельно, если есть username) ---
                        if sender_username:
                            sender_display = f"[{sender_name}](tg://user?id={msg.sender_id})"
                        else:
                            sender_display = sender_name

                        print(f"📩 [{chat_title}] {sender_name}: {text[:60]}...")

                        # --- ПРОВЕРКА ПОДПИСОК ---
                        subscriptions = get_all_subscriptions()

                        for user_id, topic, keyword in subscriptions:
                            if not keyword:
                                continue
                            if keyword.lower() in text.lower():
                                # --- УВЕДОМЛЕНИЕ ---
                                await bot.send_message(
                                    user_id,
                                    f"🔔 *Новое сообщение*\n\n"
                                    f"👤 *От кого:* {sender_display}\n"
                                    f"📎 *К сообщению:* [Перейти]({message_link})\n"
                                    f"📂 *Откуда:* {chat_title}\n"
                                    f"🔑 *Пресет:* {topic}\n\n"
                                    f"📝 *Текст:*\n{text[:500]}",
                                    parse_mode="Markdown",
                                    reply_markup=InlineKeyboardMarkup(
                                        inline_keyboard=[
                                            [
                                                InlineKeyboardButton(
                                                    text="📂 Перейти в чат",
                                                    url=message_link
                                                ),
                                            ],
                                            [
                                                InlineKeyboardButton(
                                                    text="ℹ️ Инфо",
                                                    callback_data="info"
                                                )
                                            ]
                                        ]
                                    )
                                )
                                print(f"✅ Уведомление отправлено пользователю {user_id}")

                        if msg.id > last_ids.get(chat, 0):
                            last_ids[chat] = msg.id

                except FloodWaitError as e:
                    print(f"⏳ Telegram просит подождать {e.seconds} секунд...")
                    await asyncio.sleep(e.seconds)
                except Exception as e:
                    print(f"⚠️ Ошибка в чате {chat}: {e}")

                await asyncio.sleep(DELAY_BETWEEN_CHATS)

            await asyncio.sleep(DELAY_BETWEEN_CYCLES)

        except Exception as e:
            print(f"⚠️ Ошибка в основном цикле: {e}")
            await asyncio.sleep(10)

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())