from PySide6.QtCore import QThread, Signal
from difflib import SequenceMatcher
from pathlib import Path
import time

from ..downloader import Downloader
from ...utils.format_helper import (
    format_file_size,
    format_duration,
    get_only_path,
    is_media_file,
)
from ..logging.logger import get_logger
import app.utils.constants as C
from ...database.db_manager import DBManager

logger = get_logger(__name__)


class DownloadWorker(QThread):

    file_size = Signal(str)
    progress = Signal(int)  # porcentaje 0-100
    speed = Signal(str)  # "1.2 MB/s"
    eta = Signal(str)  # "0:45"
    status_changed = Signal(str)  # 'downloading' | 'completed' | 'failed' | 'cancelled'
    error = Signal(str)  # mensaje de error
    finished = Signal(int, str)  # emite el download_id y la ruta final al terminar

    def __init__(
        self,
        db: DBManager,
        url: str,
        format: str,
        destination: str,
        download_id: int = None,
        video_quality=None,
        audio_quality=None,
    ):
        super().__init__()

        self._db = db

        self._cancelled = False
        self.url = url
        self.format = format
        self.destination = destination
        self.download_id = download_id

        self.video_quality = video_quality or C.DEFAULT_VIDEO_QUALITY
        self.audio_quality = audio_quality or C.DEFAULT_AUDIO_QUALITY

        self._size_emited = False

        self._final_filepath = ""

    def run(self):
        try:
            downloader = Downloader(
                self.destination,
                self.format,
                self._on_progress,
                self._on_post_process,
                video_quality=self.video_quality,
                audio_quality=self.audio_quality,
            )
            downloader.download(self.url)
            logger.info(
                f"Iniciando DownloadWorker con id {self.download_id} y url {self.url}"
            )
            if not self._cancelled:
                logger.info(
                    f"DownloadWorker con id {self.download_id} y url {self.url} completado en ruta {self._final_filepath}"
                )
                self.status_changed.emit(C.STATUS_COMPLETED)
                self.finished.emit(self.download_id, self._final_filepath)
            else:  # Si esta cancelado emitimos el estado
                logger.info(
                    f"DownloadWorker con id {self.download_id} y url {self.url} cancelado"
                )
                self._cleanup_partial_files()  # Se hace la limpieza de posibles archivos residuales
                self.status_changed.emit(C.STATUS_CANCELLED)
                self.finished.emit(self.download_id, "")
        except Exception as e:
            logger.error(
                f"DownloadWorker con id {self.download_id} y url {self.url} error: {str(e)}"
            )
            if self._cancelled:
                self._cleanup_partial_files()  # Se hace la limpieza de posibles archivos residuales
                self.status_changed.emit(
                    C.STATUS_CANCELLED
                )  # <- cancelación no es fallo
            else:
                self.error.emit(str(e))
                self.status_changed.emit(C.STATUS_FAILED)
            self.finished.emit(self.download_id, "")

    def _on_progress(self, data: dict):
        try:
            if self._cancelled:
                raise Exception("Descarga Cancelada")

            # Mapeamos los status de yt-dlp a los nuestros
            status_map = {
                "downloading": C.STATUS_DOWNLOADING,
                "finished": C.STATUS_DOWNLOADING,  # fragmento terminado, aun no es completed
                "error": C.STATUS_FAILED,
            }
            status = status_map.get(data.get("status", ""), C.STATUS_DOWNLOADING)

            total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
            if total:
                self.file_size.emit(f"Tamaño estimado: {format_file_size(int(total))}")
                porcentaje = int(data.get("downloaded_bytes", 1000) * 100 / total)
                self.progress.emit(porcentaje)
            if data.get("speed"):
                self.speed.emit(f"{format_file_size(data['speed'])}/s")
            if data.get("eta"):
                self.eta.emit(format_duration(data["eta"]))
            self.status_changed.emit(status)
        except Exception as e:
            self.error.emit("Error al descargar.")
            self.status_changed.emit(C.STATUS_FAILED)
            logger.error(
                f"DownloadWorker con id {self.download_id} y url {self.url} con error el _on_progress error: {str(e)}"
            )
            raise  # Relanzamos la excepcion para que run( ) la tome y el emita el finished

    def _on_post_process(self, data: dict):
        if data.get("status") != "finished":
            return

        if data.get("postprocessor") == "MoveFiles":
            logger.info(
                f"Postprocesamiento de DownloadWorker con id {self.download_id} y url {self.url} terminado"
            )
            self._final_filepath = data["info_dict"].get("filepath", "")

    def _cleanup_partial_files(self):
        logger.info(
            f"Eliminando archivos residuales del video con id: {self.download_id}"
        )
        time.sleep(5)
        try:
            download = self._db.get_download_by_id(self.download_id)
            download_title = download.title
            is_med_file = is_media_file(self.destination)
            destination = Path(self.destination)
            if is_med_file:
                _, folder, _, _ = get_only_path(destination)
                destination = Path(folder)
            partial_extensions = {
                ".part",
                ".ytdl",
                ".mp4",
                ".webm",".webp",
                ".m4a",
                ".mp3",
            }  # Posibles extensiones de archivos parciales residuales despues de cancelacion

            for file in destination.iterdir():
                if file.suffix not in partial_extensions:
                    continue
                coincidencia = SequenceMatcher(
                    None, file.stem.lower(), download_title.lower()
                ).ratio()
                if coincidencia >= C.CLEANUP_SIMILARITY_THRESHOLD:
                    try:
                        file.unlink()
                        logger.info(
                            f"Borrando el archivo residual: {str(file)} (similitud: {coincidencia:.2f}), de la descarga: {download_title} {self.download_id}"
                        )
                    except PermissionError:
                        logger.warning(
                            f"No se pudo eliminar {file.name}, archivo en uso. Se omite."
                        )

        except Exception as e:
            logger.error(
                f"Error al intentar eliminar archivos residuales del video con id: {self.download_id} {str(e)}"
            )

    def cancel(self):
        self._cancelled = True
