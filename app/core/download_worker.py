from PySide6.QtCore import QThread, Signal
from .downloader import Downloader
from ..utils.format_helper import format_file_size, format_duration


class DownloadWorker(QThread):

    progress = Signal(int)  # porcentaje 0-100
    speed = Signal(str)  # "1.2 MB/s"
    eta = Signal(str)  # "0:45"
    status_changed = Signal(str)  # 'downloading' | 'completed' | 'failed' | 'cancelled'
    error = Signal(str)  # mensaje de error
    finished = Signal(int)  # emite el download_id al terminar

    def __init__(
        self, url: str, format: str, destination: str, download_id: int = None
    ):
        super().__init__()
        self._cancelled = False
        self.url = url
        self.format = format
        self.destination = destination
        self.download_id = download_id

    def run(self):
        try:
            downloader = Downloader(self.destination, self.format, self._on_progress)
            downloader.download(self.url)
            if not self._cancelled:
                self.status_changed.emit("completed")
                self.finished.emit(self.download_id)
        except Exception as e:
            self.error.emit(str(e))
            self.status_changed.emit("failed")
            self.finished.emit(self.download_id)

    def _on_progress(self, data: dict):
        try:
            if self._cancelled:
                raise Exception("Descarga Cancelada")
            print(data)
            total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
            if total:
                porcentaje = int(data["downloaded_bytes"] * 100 / total)
                self.progress.emit(porcentaje)
            self.speed.emit(f"{format_file_size(data["speed"])}/s")
            self.eta.emit(format_duration(data["eta"]))
            self.status_changed.emit(data["status"])
        except Exception as e:
            self.error.emit("Error al descargar.")
            self.finished.emit(self.download_id)
            self.status_changed.emit("failed")
            print(str(e))

    def cancel(self):
        self._cancelled = True
