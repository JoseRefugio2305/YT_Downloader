from PySide6.QtCore import Qt
from pathlib import Path

THEME_SCHEME = {
    "light": Qt.ColorScheme.Light,
    "dark": Qt.ColorScheme.Dark,
    "system": Qt.ColorScheme.Unknown,
}

# Estados de descarga
STATUS_PENDING = "pending"
STATUS_DOWNLOADING = "downloading"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
STATUS_CANCELLED = "cancelled"
STATUS_PARTIAL = "partial"

# Agrupaciones de estados
STATUS_ACTIVE = (STATUS_DOWNLOADING, STATUS_PENDING)
STATUS_FINISHED = (STATUS_COMPLETED, STATUS_FAILED, STATUS_CANCELLED)
STATUS_RETRYABLE = (STATUS_FAILED, STATUS_CANCELLED)


STATUS_COLORS = {
    STATUS_DOWNLOADING: "#3B82F6",
    STATUS_COMPLETED: "#2C9F4B",
    STATUS_FAILED: "#EF4444",
    STATUS_CANCELLED: "#F59E0B",
    STATUS_PENDING: "#000000",
}

# Settings Default
DEFAULT_DESTINATION = Path.home() / "Downloads" / "YTDownloads"
DEFAULT_MAX_CONCURRENT = 2
DEFAULT_VIDEO_QUALITY = "bestvideo[height<=1080]+bestaudio/best"
DEFAULT_AUDIO_QUALITY = "0"
DEFAULT_DOWNLOAD_DELAY = 0
DEFAULT_SPEED_LIMIT = None
DEFAULT_PLAYER_CLIENT = ["web_safari"]
DEFAULT_THEME = "system"

# Nombres de las propiedades en configuracion
SETTING_DESTINATION = "destination"
SETTING_MAX_CONCURRENT = "max_concurrent"
SETTING_VIDEO_QUALITY = "max_vid_qual"
SETTING_AUDIO_QUALITY = "max_aud_qual"
SETTING_SPEED_LIMIT = "speed_limit"
SETTING_DOWNLOAD_DELAY = "download_delay"
SETTING_PLAYER_CLIENT = "player_client"
SETTING_THEME = "theme"

# Formatos soportados
FORMAT_MP4 = "mp4"
FORMAT_MP3 = "mp3"
SUPPORTED_FORMATS = (FORMAT_MP4, FORMAT_MP3)

# Constante para grado de similitud al borrar archivos residuales de cancelacion de descarga
CLEANUP_SIMILARITY_THRESHOLD = 0.6

# Gifs de loading
LOADING_GIFS_LIST = [
    "loading.gif",
    "l_1.gif",
    "l_2.gif",
    "l_3.gif",
    "l_4.gif",
    "l_5.gif",
    "l_6.gif",
]
