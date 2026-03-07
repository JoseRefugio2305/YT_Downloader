from PySide6.QtCore import QThread, Signal
from .downloader import Downloader


class ExtractInfoWorker(QThread):
    error = Signal(str)  # mensaje de error
    finished = Signal(
        list
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
                info = downloader.extract_playlist_info(self.url)
                self.finished.emit(info)
            else:
                info = downloader.extract_video_info(self.url)
                self.finished.emit([info])

        except Exception as e:
            self.error.emit(str(e))
