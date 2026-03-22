import urllib.request
from pathlib import Path
from PySide6.QtCore import QThread, Signal

from ..logging.logger import get_logger
from ...utils.format_helper import format_file_size
from ..updates.updater import get_updates_dir

logger = get_logger(__name__)


# Aqui es donde se lleva a cbao el proceso de descarga de la actualizacion en segundo plano, para no parar la ejecucion de la aplicacion
class UpdateWorker(QThread):
    progress = Signal(int)
    speed = Signal(str)
    finished = Signal(str)  # Ruta del archivo descargado
    error = Signal(str)

    def __init__(self, url: str, filename: str):
        super().__init__()
        self._url = url
        self._filename = filename
        self._cancelled = False
        self._destination: Path = get_updates_dir() / filename

    def run(self):
        try:
            logger.info(f"Iniciando descarga de actualización desde: {self._url}")
            req = urllib.request.Request(
                self._url, headers={"User-Agent": "YTDownloader"}
            )

            with urllib.request.urlopen(req) as response:
                total = int(response.headers.get("Content-Length", 0))
                downloaded = 0
                chunk_size = 1024 * 64  # 64 KB por chunk_size

                with open(self._destination, "wb") as f:
                    while True:
                        # Si fue cancelado
                        if self._cancelled:
                            logger.info(
                                "Descarga de actualización  cancelada por el usuario"
                            )
                            f.close()

                            self._cleanup_partial()
                            return  # Cerramos ciclo

                        chunk = response.read(chunk_size)
                        # Si no se descargo un chunk se termina el ciclo de descarga, porque ya no hay mas chunks por descargar
                        if not chunk:
                            break

                        f.write(chunk)

                        downloaded += len(chunk)

                        if total:
                            percent = int(downloaded * 100 / total)
                            self.progress.emit(percent)

                        # Calculamos velocidad aproximada (bytes descargados del chunk actual)
                        self.speed.emit(f"{format_file_size(len(chunk) * 10)}/s")
            logger.info(
                f"Actualización descargada correctamente en: {self._destination}"
            )
            self.finished.emit(str(self._destination))
        except urllib.error.URLError as e:
            logger.error(f"Error de red al descargar actualización: {str(e)}")
            self._cleanup_partial()
            self.error.emit(
                "Error de conexion. Verifica tu red internet e intenta de nuevo."
            )
        except OSError as e:
            logger.error(f"Erro de escritura al descargar la actualización: {str(e)}")
            self._cleanup_partial()
            self.error.emit(
                "Error al guarda el archivo de la actualización. Verifica los permisos de la carpeta."
            )
        except Exception as e:
            logger.error(f"Error inesperado en UpdateWorker: {str(e)}")
            self._cleanup_partial()
            self.error.emit(f"Error nesperado: {str(e)}")

    def cancel(self):
        logger.info("Cancelando descarga de actualización.")
        self._cancelled = True

    def get_destination(self) -> Path:
        return self._destination

    def _cleanup_partial(self):
        if self._destination.exists():
            try:
                self._destination.unlink()
                logger.info("Archivo parcial eliminado correctamente.")
            except Exception as e:
                logger.error(f"No se pudo eliminar el archivo parcial: {str(e)}")
