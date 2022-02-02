import asyncio
import json
from datetime import datetime
from vsbot.exceptions import FFprobeError, NoVideoStreamError, FFmpegError
from vsbot.log import logger

CMD = """ffmpeg -hide_banner -i "{input_path}" \
-vf "scale=w=512:h=512:force_original_aspect_ratio=decrease,fps=30" \
-c:v libvpx-vp9 -pix_fmt yuva420p -deadline good -row-mt 1 -b:v 500K -maxrate 500K \
-an -t 3  -y "{output_video}\""""

CHECK_CMD = """ffprobe -hide_banner -print_format json -show_format -show_streams -i "{input_video}\""""
MAX_HEIGHT = 512
MAX_WIDTH = 512
MAX_FPS = 30


async def parse_vid(input_video):
    proc = await asyncio.create_subprocess_shell(cmd=CHECK_CMD.format(input_video=input_video),
                                                 stdout=asyncio.subprocess.PIPE,
                                                 stderr=asyncio.subprocess.PIPE)
    await proc.wait()
    stdout = (await proc.stdout.read()).decode(encoding='utf-8')
    stderr = (await proc.stderr.read()).decode(encoding='utf-8')

    if proc.returncode == 0:
        try:
            json_vid = json.loads(stdout)
            if json_vid:
                return json_vid, proc
            else:
                raise FFprobeError(stdout, stderr, proc.returncode)
        except json.JSONDecodeError:
            raise FFprobeError(stdout, stderr, proc.returncode)
    else:
        raise FFprobeError(stdout, stderr, proc.returncode)


def get_video_info(vid_json: dict):
    video_stream = None
    for stream in vid_json["streams"]:
        try:
            if stream["codec_type"] == "video":
                video_stream = stream
                break
        except KeyError:
            continue

    if not video_stream:
        raise NoVideoStreamError

    if "duration" not in video_stream.keys():
        try:
            duration = video_stream["tags"]["DURATION"]
        except KeyError:
            duration = None
    else:
        duration = video_stream["duration"]

    return {
        "height": video_stream["coded_height"],
        "width": video_stream["coded_width"],
        "duration": duration,
        "fps": int(str(video_stream["avg_frame_rate"]).split("/")[0])
    }


async def process_video(input_video, output_video):
    proc_hash = hash((input_video, output_video))
    start = datetime.now()

    logger.info(f"{proc_hash} | Processing {input_video}")
    logger.debug(f"{proc_hash} | Parsing info")
    _vid_json, _proc = await parse_vid(input_video)
    vid_info = get_video_info(_vid_json)
    cmd = CMD.format(
            input_path=input_video,
            fps=30,
            output_video=output_video
        )
    logger.debug(f"{proc_hash} | Processing ffmpeg | {'; '.join([f'{key}: {val}' for key, val in vid_info.items()])}")
    ff_proc = await asyncio.create_subprocess_shell(
        cmd=cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    await ff_proc.wait()
    stdout = (await ff_proc.stdout.read()).decode('utf-8')
    stderr = (await ff_proc.stderr.read()).decode('utf-8')

    if ff_proc.returncode != 0:
        raise FFmpegError(stdout, stderr, ff_proc.returncode)

    else:
        logger.debug(f"{proc_hash} | Done. {round((datetime.now()-start).total_seconds(), 3)} seconds")
