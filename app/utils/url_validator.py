import re

DOMINIO_REGEX = re.compile(r"^https?:\/\/([\w-]+\.)?(youtube\.com|youtu\.be)\/.+$")
VIDEO_COMP_REGEX = re.compile(
    r"^https?:\/\/(www\.)?youtube\.com\/watch\?v=[A-Za-z0-9_-]{11}(&.*)?$"
)
VIDEO_CORTO_REGEX = re.compile(
    r"^https?:\/\/(www\.)?youtu\.be\/[A-Za-z0-9_-]{11}(\?.*)?$"
)
VIDEO_PLAYLIST_REGEX = re.compile(
    r"^https?:\/\/(www\.)?youtube\.com\/watch\?v=[A-Za-z0-9_-]{11}&list=[A-Za-z0-9_-]+(&.*)?$"
)
SHORT_REGEX = re.compile(
    r"^https?:\/\/(www\.)?youtube\.com\/shorts\/[A-Za-z0-9_-]{11}(\?.*)?$"
)
PLAYLIST_REGEX = re.compile(
    r"^https?:\/\/(www\.)?youtube\.com\/playlist\?list=[A-Za-z0-9_-]+(&.*)?$"
)


def is_valid_youtube_url(url: str) -> bool:
    is_valid = DOMINIO_REGEX.match(url)
    return is_valid is not None


def detect_url_type(url: str) -> str:
    if VIDEO_PLAYLIST_REGEX.match(url):
        return "video/playlist"
    elif (
        VIDEO_COMP_REGEX.match(url)
        or VIDEO_CORTO_REGEX.match(url)
        or SHORT_REGEX.match(url)
    ):
        return "video"
    elif PLAYLIST_REGEX.match(url):
        return "playlist"
    
    return "unknown"

