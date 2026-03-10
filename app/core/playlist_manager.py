from PySide6.QtCore import QObject, Signal, QTimer

from .download_worker import DownloadWorker
from ..database.db_manager import DBManager
from ..database.models import Download, PlaylistDownload
from .settings import Settings


class PlaylistManager(QObject):
    item_finished = Signal(int)  # download_id
    item_failed = Signal(int, str)  # download_id, error message
    all_finished = Signal()
    item_started = Signal(
        int, DownloadWorker
    )  # Con este signal controlamos cuando un worker es iniciado en las descargas

    def __init__(self, db: DBManager, max_concurrent: int = 2):
        super().__init__()
        self._db = db
        self._workers: dict[int, DownloadWorker] = {}  # Descargas activas
        self._queue: list[dict] = []  # Lista de espera en descargas
        self.max_concurrent = max_concurrent

    def enqueue(
        self,
        title,
        url,
        format,
        destination,
        yt_id,
        yt_playlist_id=None,
        playlist_url: str = None,
        playlist_title: str = None,
        playlist_t_items: int = 0,
    ) -> int:

        # Si hay un id de playlist, revisamos en DB si ya existe, de no ser asi, la insertamos
        playlist_id = None
        if yt_playlist_id:
            playlist = self._db.get_playlist_by_yt_id(yt_playlist_id)
            if not playlist:
                playlist_id = self._db.insert_playlist(
                    PlaylistDownload(
                        url=playlist_url,
                        title=playlist_title,
                        format=format,
                        status="pending",
                        destination_path=destination,
                        yt_id=yt_playlist_id,
                        total_items=playlist_t_items,
                    )
                )
            else:
                playlist_id = playlist.id

        download_id = self._db.insert_download(
            Download(
                url=url,
                title=title,
                format=format,
                status="pending",
                destination_path=destination,
                playlist_id=playlist_id,
                yt_id=yt_id,
            )
        )
        self._queue.append(
            {
                "id": download_id,
                "yt_id": yt_id,
                "playlist_id": yt_playlist_id,
                "url": url,
                "destination": destination,
                "format": format,
                "status": "pending",
            }
        )
        return download_id

    def start_enqueue(self):
        self._start_next()  # Iniciamos la descarga

    def cancel_item(self, download_id: int) -> None:
        if (
            download_id in self._workers
        ):  # Si el item esta en proceso de descarga lo buscamos en _workers
            self._workers[download_id].cancel()
            return

        for eq in range(0, len(self._queue)):  # Buscamos si esta en la cola de espera
            if self._queue[eq]["id"] == download_id:
                self._queue.pop(eq)
                self._db.update_downloaded_status(download_id, "cancelled")

    def cancel_all(self) -> None:
        # Cancelamos descargas en proceso
        for _, worker in self._workers.items():
            worker.cancel()
        # vaciamos lista de espera
        for el in self._queue:
            self._db.update_downloaded_status(
                el["id"], "cancelled"
            )  # Actualizamos todos los pendientes a cancelados
        self._queue = []

    def get_worker(self, download_id: int) -> DownloadWorker | None:
        return self._workers.get(download_id)

    def _start_next(self):
        # Revisamos primero si no se esta excedieno el limiete de concurrencia
        if len(self._workers) >= self.max_concurrent:
            return

        if len(self._queue) == 0:  # Si ya no hay elementos en cola
            if not self._workers:  # Si tampoco hay elementos en proceso de descarga
                self.all_finished.emit()  # Como no recibe argumentos solo se emite la se;al
            return
        new_worker = self._queue[0]  # Tomamos el prmiero
        self._workers[new_worker["id"]] = DownloadWorker(
            new_worker["url"],
            new_worker["format"],
            new_worker["destination"],
            new_worker["id"],
            video_quality=Settings.get_video_quality(),
            audio_quality=Settings.get_audio_quality(),
        )
        self._queue.pop(0)  # Quitamos de la cola de espera
        self._workers[new_worker["id"]].status_changed.connect(
            lambda status: self._db.update_downloaded_status(new_worker["id"], status)
        )
        self._workers[new_worker["id"]].error.connect(
            lambda error: self._db.update_downloaded_status(
                new_worker["id"], "failed", error
            )
        )
        self._workers[new_worker["id"]].finished.connect(self._on_work_finished)
        self._workers[new_worker["id"]].start()

        self.item_started.emit(new_worker["id"], self._workers[new_worker["id"]])

    def _on_work_finished(self, download_id: int):
        self.item_finished.emit(download_id)
        self._workers.pop(download_id, None)  # Si no existe no da error

        # Revisamos si hay una playlist asiciada a la descarga
        playlist_id = self._db.get_playlist_id(download_id)
        if playlist_id:
            playlist = self._db.get_playlist_by_id(playlist_id)
            downloads = self._db.get_downloads_by_playlist(playlist_id)
            # Calculamos fallos y completadas con exito
            failures = len(
                [d for d in downloads if d.status in ("failed", "cancelled")]
            )
            completed = len([d for d in downloads if d.status == "completed"])
            if (
                playlist.total_items > 0
                and (failures + completed) >= playlist.total_items
            ):  # Si la suma de fallos y completados no es igual al total, entonces aun no termina, pero si es igual o mayor es que termino ya
                final_status = "completed" if failures == 0 else "partial"
                self._db.update_playlist_status(playlist_id, final_status)

        # Revisamos primero si hay delay aplicado, de haberlo se aplica antes de llamar a la seguiente descarga
        delay_ms = Settings.get_download_delay() * 1000
        if delay_ms > 0:
            QTimer.singleShot(delay_ms, self._start_next)
        else:
            self._start_next()  # Revisamos si hay algun otro elemento en la cola
