from vsbot.misc import bot, dp
from vsbot.log import logger
import aiogram
from aiogram.types import ContentType
from .handlers import start, handle_video, stickers


def set_bot():
    dp.register_message_handler(start, commands=["start"])
    dp.register_message_handler(stickers, commands=["newvideo"])
    dp.register_message_handler(handle_video, content_types=ContentType.ANY)


async def starter(*args, **kwargs):
    await bot.send_message(704477361, "Bot started")


def run():
    set_bot()
    logger.info("Starting pooling")
    aiogram.executor.start_polling(dp, skip_updates=True, on_startup=starter)
