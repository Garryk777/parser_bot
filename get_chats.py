import asyncio
from telethon import TelegramClient
from config import API_ID, API_HASH, PHONE_NUMBER

async def main():
    client = TelegramClient("session", API_ID, API_HASH)
    await client.start(phone=PHONE_NUMBER)

    print("📋 Список чатов, в которых состоит аккаунт:\n")

    async for dialog in client.iter_dialogs():
        print(f"{dialog.name} — {dialog.id}")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())