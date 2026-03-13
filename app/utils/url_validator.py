import re
from urllib.parse import urlparse, parse_qs

DOMINIO_YOUTUBE_REGEX = re.compile(
    r"^https?:\/\/([\w-]+\.)?(youtube\.com|youtu\.be)\/.+$"
)
SOCIAL_VID_DOMAIN_REGEX = re.compile(
    r"^https?:\/\/([\w-]+\.)?(facebook\.com|fb\.watch|twitter\.com|x\.com|tiktok\.com)\/.+$"
)
# YouTube
VID_YT_COMP_REGEX = re.compile(
    r"^https?:\/\/(www\.)?youtube\.com\/watch\?v=[A-Za-z0-9_-]{11}(&.*)?$"
)
VID_YT_MUSIC_REGEX = re.compile(
    r"^https?:\/\/(www\.|music\.)?youtube\.com\/watch\?v=[A-Za-z0-9_-]{11}(&.*)?$"
)
VID_YT_CORTO_REGEX = re.compile(
    r"^https?:\/\/(www\.)?youtu\.be\/[A-Za-z0-9_-]{11}(\?.*)?$"
)
# Esta es para cuando es el link de un video dentro de una playlist
VID_YT_PLAYLIST_REGEX = re.compile(
    r"^https?:\/\/(www\.)?youtube\.com\/watch\?v=[A-Za-z0-9_-]{11}&list=[A-Za-z0-9_-]+(&.*)?$"
)
SHORT_YT_REGEX = re.compile(
    r"^https?:\/\/(www\.)?youtube\.com\/shorts\/[A-Za-z0-9_-]{11}(\?.*)?$"
)
PLAYLIST_REGEX = re.compile(
    r"^https?:\/\/(www\.)?youtube\.com\/playlist\?list=[A-Za-z0-9_-]+(&.*)?$"
)
# TikTok
TIKTOK_VIDEO_REGEX = re.compile(
    r"^https?:\/\/(www\.)?tiktok\.com\/("
    r"@[\w.-]+\/video\/\d+|"
    r"t\/[A-Za-z0-9]+|"
    r"v\/\d+"
    r")(\?.*)?$"
)
# Twitter
TWITTER_VIDEO_REGEX = re.compile(
    r"^https?:\/\/(www\.)?(twitter\.com|x\.com)\/[A-Za-z0-9_]+\/status\/\d+(\?.*)?$"
)
# Facebook
FACEBOOK_VIDEO_REGEX = re.compile(
    r"^https?:\/\/(www\.)?(facebook\.com|fb\.watch)\/("
    r"watch\/?\?v=\d+|"
    r"reel\/\d+|"
    r".+\/videos\/\d+|"
    r"[A-Za-z0-9._-]+"
    r")(\?.*)?$"
)

# Ordenacion por tipo
_PLAYLIST_PATTERNS = [
    PLAYLIST_REGEX,
]
_VIDEO_PATTERNS = [
    VID_YT_COMP_REGEX,
    VID_YT_MUSIC_REGEX,
    VID_YT_CORTO_REGEX,
    SHORT_YT_REGEX,
    TIKTOK_VIDEO_REGEX,
    TWITTER_VIDEO_REGEX,
    FACEBOOK_VIDEO_REGEX,
]

_TYPE_PATTERNS: list[tuple[str, list]] = [
    ("video/playlist", [VID_YT_PLAYLIST_REGEX]),
    ("video", _VIDEO_PATTERNS),
    ("playlist", _PLAYLIST_PATTERNS),
]


# Revisamos si es de youtube o de alguna otra red aceptada
def is_valid_url(url: str) -> bool:
    is_valid_youtube = is_valid_youtube_url(url)
    is_valid_social = SOCIAL_VID_DOMAIN_REGEX.match(url)

    return is_valid_youtube is not None or is_valid_social is not None


# Revisamos si es valido de yotube
def is_valid_youtube_url(url: str) -> bool:
    is_valid = DOMINIO_YOUTUBE_REGEX.match(url)
    return is_valid is not None


def detect_url_type(url: str) -> str:
    if VID_YT_PLAYLIST_REGEX.match(url):
        return "video/playlist"
    elif (
        VID_YT_COMP_REGEX.match(url)
        or VID_YT_MUSIC_REGEX.match(url)
        or VID_YT_CORTO_REGEX.match(url)
        or SHORT_YT_REGEX.match(url)
        or TIKTOK_VIDEO_REGEX.match(url)
        or TWITTER_VIDEO_REGEX.match(url)
        or FACEBOOK_VIDEO_REGEX.match(url)
    ):
        return "video"
    elif PLAYLIST_REGEX.match(url):
        return "playlist"

    return "unknown"


def detect_url_type(url: str) -> str:
    for url_type, patterns in _TYPE_PATTERNS:
        if any(p.match(url) for p in patterns):
            return url_type
    return "unknown"


def clean_yt_url(url: str) -> tuple[str, int]:
    base_url = "https://www.youtube.com/"
    parsed_url = urlparse(url)  # parseamos para obtener la query string

    parametros = parse_qs(parsed_url.query)  # Parseamos a diccionario

    playlist_url = f"{base_url}playlist?list={parametros.get("list")[0]}"
    vid_YT_url = f"{base_url}watch?v={parametros.get("v")[0]}"

    return playlist_url, vid_YT_url
