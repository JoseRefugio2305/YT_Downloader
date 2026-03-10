from PySide6.QtCore import QThread, Signal
from typing import Optional, Any, Dict

from .downloader import Downloader


class ExtractInfoWorker(QThread):
    error = Signal(str)  # mensaje de error
    finished = Signal(
        dict, list
    )  # lista de dicts con la infor de cada video, cuando sea un solo video esta lista sera de un solo elemento

    def __init__(
        self,
        url: str,
        url_type: str,
        format: str,
        video_quality=None,
        audio_quality=None,
    ):
        super().__init__()
        self.url = url
        self.format = format
        self.url_type = url_type

        self.video_quality = video_quality or "bestvideo[height<=1080]+bestaudio/best"
        self.audio_quality = audio_quality or "0"

    def run(self):
        try:
            downloader = Downloader(
                destination="",
                format=self.format,
                video_quality=self.video_quality,
                audio_quality=self.audio_quality,
            )
            if self.url_type == "playlist":
                playlist_info, videos = downloader.extract_playlist_info(self.url)
                self.finished.emit(playlist_info, videos)
            else:
                info = downloader.extract_video_info(self.url)
                self.finished.emit(None, [info])

        except Exception as e:
            self.error.emit(str(e))
