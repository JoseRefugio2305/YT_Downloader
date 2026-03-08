from PySide6.QtCore import QThread, Signal
from typing import Optional, Any, Dict

from .downloader import Downloader


class ExtractInfoWorker(QThread):
    error = Signal(str)  # mensaje de error
    finished = Signal(
        dict, list
    )  # lista de dicts con la infor de cada video, cuando sea un solo video esta lista sera de un solo elemento

    def __init__(self, url: str, url_type: str, format: str):
        super().__init__()
        self.url = url
        self.format = format
        self.url_type = url_type

    def run(self):
        try:
            downloader = Downloader(destination="", format=self.format)
            if self.url_type == "playlist":
                playlist_info, videos = downloader.extract_playlist_info(self.url)
                self.finished.emit(playlist_info, videos)
            else:
                info = downloader.extract_video_info(self.url)
                self.finished.emit(None, [info])

        except Exception as e:
            self.error.emit(str(e))
