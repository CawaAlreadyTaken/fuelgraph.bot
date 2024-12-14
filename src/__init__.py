import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

# Percorso per salvare i dati
DATA_FILE = "/data/odg.json"

# Funzione per caricare i dati
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return []

# Funzione per salvare i dati
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Creazione del bot
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("La variabile di ambiente TELEGRAM_BOT_TOKEN non è impostata.")

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Comando per mostrare l'ordine del giorno
@dp.message(Command(commands=["odg"]))
async def show_odg(message: Message, state: FSMContext):
    args = message.text.split(maxsplit=1)
    if len(args) == 1:
        data = load_data()
        if data:
            odg_message = "Contenuto ordine del giorno:\n\n"
            for entry in data:
                odg_message += f"📋 {entry['item']}\n👤 {entry['user']}\n\n"
            await message.reply(odg_message)
        else:
            await message.reply("L'ordine del giorno è vuoto.")
    else:
        item = args[1]
        if item == "reset":
            save_data([])
            await message.reply(f"odg reset effettuato")
        else:
            data = load_data()
            user = message.from_user
            if user.last_name is not None:
                data.append({"item": item, "user": f"{user.first_name} {user.last_name}"})
            else:
                data.append({"item": item, "user": f"{user.first_name}"})
            save_data(data)
            await message.reply(f"Aggiunto all'ordine del giorno: '{item}'")

# Funzione principale per avviare il bot
async def main():
    print("Bot avviato...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

