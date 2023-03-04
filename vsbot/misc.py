import json

from vsbot.db import BotDB
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.bot.api import TelegramAPIServer

storage = MemoryStorage()
db = BotDB()
with open("volumes/config.json", "r", encoding="utf-8") as _cfg_file:
    config = json.load(_cfg_file)

bot = Bot(
    token=config["TOKEN"],
    server=TelegramAPIServer.from_base(f"http://botapi:8081/")
)
dp = Dispatcher(bot=bot, storage=storage)
