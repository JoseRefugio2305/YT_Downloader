from PySide6.QtCore import QSettings
from pathlib import Path
from typing import List

import app.utils.constants as C


class SettingsApp:

    def __init__(self):
        self._settings = QSettings("YTDownloader", "config")

    def get_destination(self) -> str:
        path = self._settings.value(
            C.SETTING_DESTINATION, C.DEFAULT_DESTINATION, type=str
        )
        Path(path).mkdir(exist_ok=True)
        return path

    def get_max_concurrent(self) -> int:
        max_concurrent = self._settings.value(
            C.SETTING_MAX_CONCURRENT, C.DEFAULT_MAX_CONCURRENT, type=int
        )
        return max_concurrent

    def get_video_quality(self) -> str:
        max_vid_qual = self._settings.value(
            C.SETTING_VIDEO_QUALITY,
            C.DEFAULT_VIDEO_QUALITY,
        )
        return max_vid_qual

    def get_audio_quality(self) -> str:
        max_aud_qual = self._settings.value(
            C.SETTING_AUDIO_QUALITY, C.DEFAULT_AUDIO_QUALITY
        )
        return max_aud_qual

    def get_speed_limit(self) -> str | None:
        value = self._settings.value(
            C.SETTING_SPEED_LIMIT, C.DEFAULT_SPEED_LIMIT
        )  # Posibles valores None (sin limite),"1M", "500K", "2M"
        return value if value else None

    def get_download_delay(self) -> int:
        # Segundos de espera entre descargas, 0 = sin espera
        return self._settings.value(
            C.SETTING_DOWNLOAD_DELAY, C.DEFAULT_DOWNLOAD_DELAY, type=int
        )  # Lo entrega en segundos

    def get_player_client(self) -> List[str]:
        # Valores en la lista  "web", "android", "tv_embedded"
        # android_vr", "web_safari"
        return self._settings.value(
            C.SETTING_PLAYER_CLIENT, C.DEFAULT_PLAYER_CLIENT, type=list
        )

    def get_theme(self) -> str:
        return self._settings.value(C.SETTING_THEME, C.DEFAULT_THEME, type=str)


Settings = SettingsApp()
