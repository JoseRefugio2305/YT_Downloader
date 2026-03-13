import re
from urllib.parse import urlparse, parse_qs

DOMINIO_REGEX = re.compile(r"^https?:\/\/([\w-]+\.)?(youtube\.com|youtu\.be)\/.+$")
VIDEO_COMP_REGEX = re.compile(
    r"^https?:\/\/(www\.)?youtube\.com\/watch\?v=[A-Za-z0-9_-]{11}(&.*)?$"
)
VIDEO_MUSIC_REGEX = re.compile(
    r"^https?:\/\/(www\.|music\.)?youtube\.com\/watch\?v=[A-Za-z0-9_-]{11}(&.*)?$"
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
        or VIDEO_MUSIC_REGEX.match(url)
        or VIDEO_CORTO_REGEX.match(url)
        or SHORT_REGEX.match(url)
    ):
        return "video"
    elif PLAYLIST_REGEX.match(url):
        return "playlist"

    return "unknown"


def clean_url(url: str) -> tuple[str, int]:
    base_url = "https://www.youtube.com/"
    parsed_url = urlparse(url)  # parseamos para obtener la query string

    parametros = parse_qs(parsed_url.query)  # Parseamos a diccionario

    playlist_url = f"{base_url}playlist?list={parametros.get("list")[0]}"
    video_url = f"{base_url}watch?v={parametros.get("v")[0]}"

    return playlist_url, video_url
