import os

from tempfile import mkstemp
from aiogram.types import Message
from vsbot.misc import db, bot
from vsbot.log import logger
from vsbot.convert import process_video


async def start(message: Message):
    if not db.get_user(message.from_user.id):
        db.new_user(
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.username if message.from_user.username else ""
        )
        logger.info(f"New user {message.from_user.id} | {message.from_user.full_name} | {message.from_user.username}")

    await message.reply(
        "Hello!\nI'm help you convert video to required format for @stickers!\nSend me a video and I do the magic!")


async def handle_video(message: Message):
    if not message.video and (not message.document or "video" not in message.document.mime_type):
        await message.reply("Incorrect video file")
    else:
        pr_message = await message.reply("Processing...")
        if message.video:
            file_name = message.video.file_name
        else:
            file_name = message.document.file_name

        if not file_name:
            file_name = "WITHOUT_NAME"

        handled_fd, handled_vid_temp_path = mkstemp(prefix='HANDLED_VID', suffix="."+file_name.split(".")[-1])
        completed_fd, completed_vid_temp_path = mkstemp(prefix='COMPLETED_VID', suffix=".webm")

        proc_hash = hash((handled_vid_temp_path, completed_vid_temp_path))

        logger.debug(f"{proc_hash} | Downloading")

        if message.document:
            await message.document.download(handled_vid_temp_path)
        elif message.video:
            await message.video.download(handled_vid_temp_path)
        os.close(handled_fd)

        await process_video(handled_vid_temp_path, completed_vid_temp_path)
        logger.debug(f"{proc_hash} | Uploading")

        with open(completed_vid_temp_path, "rb") as completed_file:
            await message.answer_document(completed_file)

        logger.debug(f"{proc_hash} | Deleting temp files")
        os.close(completed_fd)
        os.remove(handled_vid_temp_path)
        os.remove(completed_vid_temp_path)
        await pr_message.delete()






