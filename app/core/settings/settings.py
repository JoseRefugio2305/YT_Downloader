from PySide6.QtCore import QSettings
from pathlib import Path
from typing import List


class SettingsApp:

    def __init__(self):
        self._settings = QSettings("YTDownloader", "config")

    def get_destination(self) -> str:
        path = self._settings.value("destination", Path.home() / "Downloads", type=str)
        return path

    def get_max_concurrent(self) -> int:
        max_concurrent = self._settings.value("max_concurrent", 2, type=int)
        return max_concurrent

    def get_video_quality(self) -> str:
        max_vid_qual = self._settings.value(
            "max_vid_qual",
            "bestvideo[height<=1080]+bestaudio/best",
        )
        return max_vid_qual

    def get_audio_quality(self) -> str:
        max_aud_qual = self._settings.value("max_aud_qual", "0")
        return max_aud_qual

    def get_speed_limit(self) -> str | None:
        value = self._settings.value(
            "speed_limit", None
        )  # Posibles valores None (sin limite),"1M", "500K", "2M"
        return value if value else None

    def get_download_delay(self) -> int:
        # Segundos de espera entre descargas, 0 = sin espera
        return self._settings.value(
            "download_delay", 0, type=int
        )  # Lo entrega en segundos

    def get_player_client(self) -> List[str]:
        # Valores en la lista  "web", "android", "tv_embedded"
        #android_vr", "web_safari"
        return self._settings.value("player_client", ["web_safari"], type=list)

    def get_theme(self) -> str:
        return self._settings.value("theme", "system", type=str)


Settings = SettingsApp()
