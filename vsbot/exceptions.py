class FFprobeError(Exception):
    def __init__(self, stdout, stderr, code):
        self.stdout = stdout
        self.stderr = stderr
        self.code   = code


class NoVideoStreamError(Exception):
    pass


class FFmpegError(Exception):
    def __init__(self, stdout, stderr, code):
        self.stdout = stdout
        self.stderr = stderr
        self.code   = code
