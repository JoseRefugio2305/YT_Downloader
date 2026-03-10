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
        self,
        url: str,
        format: str,
        destination: str,
        download_id: int = None,
        video_quality=None,
        audio_quality=None,
    ):
        super().__init__()
        self._cancelled = False
        self.url = url
        self.format = format
        self.destination = destination
        self.download_id = download_id

        self.video_quality = video_quality or "bestvideo[height<=1080]+bestaudio/best"
        self.audio_quality = audio_quality or "0"

    def run(self):
        try:
            downloader = Downloader(
                self.destination,
                self.format,
                self._on_progress,
                video_quality=self.video_quality,
                audio_quality=self.audio_quality,
            )
            downloader.download(self.url)
            if not self._cancelled:
                self.status_changed.emit("completed")
                self.finished.emit(self.download_id)
            else:  # Si esta cancelado emitimos el estado
                self.status_changed.emit("cancelled")
                self.finished.emit(self.download_id)
        except Exception as e:
            if self._cancelled:
                self.status_changed.emit("cancelled")  # <- cancelación no es fallo
            else:
                self.error.emit(str(e))
                self.status_changed.emit("failed")
            self.finished.emit(self.download_id)

    def _on_progress(self, data: dict):
        try:
            if self._cancelled:
                raise Exception("Descarga Cancelada")

            # Mapeamos los status de yt-dlp a los nuestros
            status_map = {
                "downloading": "downloading",
                "finished": "downloading",  # fragmento terminado, aun no es completed
                "error": "failed",
            }
            status = status_map.get(data.get("status", ""), "downloading")

            total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
            if total:
                porcentaje = int(data.get("downloaded_bytes",1000) * 100 / total)
                self.progress.emit(porcentaje)
            if data.get("speed"):
                self.speed.emit(f"{format_file_size(data['speed'])}/s")
            if data.get("eta"):
                self.eta.emit(format_duration(data["eta"]))
            self.status_changed.emit(status)
        except Exception as e:
            self.error.emit("Error al descargar.")
            self.status_changed.emit("failed")
            print(str(e))
            raise  # Relanzamos la excepcion para que run( ) la tome y el emita el finished

    def cancel(self):
        self._cancelled = True
