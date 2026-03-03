from PySide6.QtCore import QObject, Signal
from .download_worker import DownloadWorker


class PlaylistManager(QObject):
    item_finished = Signal(int)  # download_id
    item_failed = Signal(int, str)  # download_id, error message
    all_finished = Signal()

    def __init__(self, max_concurrent: int = 2):
        super().__init__()
        self._workers: dict[int, DownloadWorker] = {}  # Descargas activas
        self._queue: list[dict] = []  # Lista de espera en descargas
        self.max_concurrent = max_concurrent

    def enqueue(self, url, format, destination, download_id):
        self._queue.append(
            {
                "id": download_id,
                "url": url,
                "destination": destination,
                "format": format,
            }
        )
        self._start_next()#Una vez encolado, iniciamos el siguiente

    def cancel_item(self, download_id: int) -> None:
        if (
            download_id in self._workers
        ):  # Si el item esta en proceso de descarga lo buscamos en _workers
            self._workers[download_id].cancel()
            return

        for eq in range(0, len(self._queue)):  # Buscamos si esta en la cola de espera
            if self._queue[eq]["id"] == download_id:
                self._queue.pop(eq)

    def cancel_all(self) -> None:
        # Cancelamos descargas en proceso
        for _, worker in self._workers.items():
            worker.cancel()
        # vaciamos lista de espera
        self._queue = []

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
        )
        self._queue.pop(0)  # Quitamos de la cola de espera
        self._workers[new_worker["id"]].finished.connect(self._on_work_finished)
        self._workers[new_worker["id"]].start()

    def _on_work_finished(self, download_id: int):
        self.item_finished.emit(download_id)
        del self._workers[download_id]
        self._start_next()  # Revisamos si hay algun otro elemento en la cola
