import asyncio
import os
from tempfile import mkstemp

import aiogram.utils.exceptions
from aiogram.types import Message
from vsbot.misc import db, dp
from vsbot.log import logger
from vsbot.convert import process_video
from aiogram.utils.exceptions import Throttled


async def start(message: Message):
    if not db.get_user(message.from_user.id):
        db.new_user(
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.username if message.from_user.username else ""
        )
        logger.info(f"New user {message.from_user.id} | {message.from_user.full_name} | {message.from_user.username}")

    try:
        await dp.throttle('send_message', rate=.3)
    except Throttled:
        logger.warning(f"Send message FloodWait for {message.from_user.id}")
        return

    await message.reply(
        "Hello!\nI can help you to convert video files into the required for @stickers bot format!\n"
        "Send me a video file and I'll do the magic!"
    )


async def _send_upload_task(bot, chat_id):
    while True:
        await bot.send_chat_action(chat_id, "upload_video")
        await asyncio.sleep(4.5)


async def handle_video(message: Message):
    proc_hash = None
    completed_fd = None
    handled_vid_temp_path = None
    completed_vid_temp_path = None

    if not db.get_user(message.from_user.id):
        db.new_user(
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.username if message.from_user.username else ""
        )
        logger.info(f"New user {message.from_user.id} | {message.from_user.full_name} | {message.from_user.username}")

    try:
        await dp.throttle('send_message', rate=.3)
    except Throttled:
        logger.warning(f"Send message FloodWait for {message.from_user.id}")
        return

    if not message.video and (not message.document or "video" not in message.document.mime_type):
        await message.reply("Incorrect video file")
    else:
        try:
            await dp.throttle('handle_video', rate=5)
        except Throttled:
            logger.warning(f"Send video FloodWait for {message.from_user.id}")
            await message.reply("Are you throttled. You can use 1 request in 5 seconds")
            return

        pr_message = await message.reply("Processing...")
        typing_task = asyncio.get_event_loop().create_task(_send_upload_task(message.bot, message.from_user.id))

        try:
            if message.video:
                file_name = message.video.file_name
            else:
                file_name = message.document.file_name

            if not file_name:
                file_name = "WITHOUT_NAME"

            handled_fd, handled_vid_temp_path = mkstemp(prefix='HANDLED_VID', suffix="."+file_name.split(".")[-1])
            completed_fd, completed_vid_temp_path = mkstemp(prefix='COMPLETED_VID', suffix=".webm")

            proc_hash = hash((handled_vid_temp_path, completed_vid_temp_path))

            logger.info(f"{proc_hash} | {message.from_user.id} | Processing video")
            logger.debug(f"{proc_hash} | Downloading")

            try:
                if message.document:
                    await message.document.download(destination_file=handled_vid_temp_path)
                elif message.video:
                    await message.video.download(destination_file=handled_vid_temp_path)
            except aiogram.utils.exceptions.FileIsTooBig:
                await message.answer("File is too big (>20MB)")
                return

            os.close(handled_fd)

            await process_video(handled_vid_temp_path, completed_vid_temp_path)
            logger.debug(f"{proc_hash} | Uploading")

            with open(completed_vid_temp_path, "rb") as completed_file:
                await message.reply_document(completed_file)

        except Exception as err:
            logger.error(f"{proc_hash if proc_hash else 'UNKNOWN PH'} | Unknown error while converting video: "
                         f"{err.__class__}: {err}")
            return

        finally:
            typing_task.cancel()
            logger.debug(f"{proc_hash} | Deleting temp files")
            os.close(completed_fd) if completed_fd else ...
            os.remove(handled_vid_temp_path) if handled_vid_temp_path else ...
            os.remove(completed_vid_temp_path) if completed_vid_temp_path else ...
            await pr_message.delete()


async def stickers(message: Message):
    if not db.get_user(message.from_user.id):
        db.new_user(
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.username if message.from_user.username else ""
        )
        logger.info(f"New user {message.from_user.id} | {message.from_user.full_name} | {message.from_user.username}")

    try:
        await dp.throttle('send_message', rate=.3)
    except Throttled:
        logger.warning(f"Send message FloodWait for {message.from_user.id}")
        return

    await message.reply("Not me, in @stickers :)")
