from vsbot.db import BotDB
from aiogram import Bot, Dispatcher
import json

db = BotDB()
with open("config.json", "r", encoding="utf-8") as _cfg_file:
    config = json.load(_cfg_file)

bot = Bot(token=config["TOKEN"])
dp = Dispatcher(bot=bot)