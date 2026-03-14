from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from .download_item import DownloadItem
from ....database.db_manager import DBManager
from ....core.playlist_manager import PlaylistManager
from ....core.workers.download_worker import DownloadWorker
from ....core.logging.logger import get_logger

logger = get_logger(__name__)


class DownloadQueue(QObject):
    def __init__(
        self, scroll_area: QScrollArea, playlist_manager: PlaylistManager, db: DBManager
    ):
        super().__init__()
        self._playlist_manager = playlist_manager
        self._db = db
        self._items: dict[int, DownloadItem] = (
            {}
        )  # Todos los items de cada descarga, el id sera el download_id
        self._playlist_manager.item_started.connect(
            self._on_item_started
        )  # Conectamos a la se;al de cuando se inicia un worker
        self._setup_scroll(scroll_area)

    def _setup_scroll(self, scroll_area: QScrollArea):
        self.container = QWidget()
        self.layoutVItems = QVBoxLayout(self.container)
        self.layoutVItems.setAlignment(Qt.AlignTop)  # items se apilan desde arriba
        scroll_area.setWidget(self.container)

    def add_item(self, download_id: int, title: str) -> None:
        new_item = DownloadItem(download_id, title, self._db, self.container)
        new_item.cancel_requested.connect(
            lambda download_id: self._on_cancel_requested(download_id)
        )
        new_item.retry_requested.connect(
            lambda download_id: self._on_retry_requested(download_id)
        )
        new_item.remove_requested.connect(
            lambda download_id: self._on_remove_requested(download_id)
        )

        self._items[download_id] = new_item
        self.layoutVItems.addWidget(new_item)

    def _on_cancel_requested(self, download_id: int):
        self._playlist_manager.cancel_item(download_id)

    def _on_retry_requested(self, download_id: int):
        download = self._db.get_download_by_id(download_id)
        if not download:
            return

        new_download_id = self._playlist_manager.enqueue(
            download.title,
            download.url,
            download.format,
            download.destination_path,
            download.yt_id,
            None,
            None,
            None,
            0,
        )

        item = self._items.pop(download_id)  # quitamos con el id viejo
        item.update_download_id(new_download_id)  # actualizamos su id
        self._items[new_download_id] = item

        self._playlist_manager.start_enqueue()

    def retry_from_history(self, download_id: int, title: str):
        if download_id in self._items:
            logger.warning(
                f"[DownloadQueue] Ya existe un item activo para id {download_id}"
            )
            self._on_remove_requested(download_id)
            
        self.add_item(download_id, title)
        self._on_retry_requested(download_id)

    def _on_remove_requested(self, download_id: int):
        if download_id not in self._items:
            logger.warning(f"Remove ignorado, id {download_id} no existe")
            return
        item = self._items.pop(download_id)
        self.layoutVItems.removeWidget(item)
        item.deleteLater()  # libera el widget de memoria

    def _on_item_started(self, download_id: int, worker: DownloadWorker):
        if download_id in self._items:
            self._items[download_id].assign_worker(worker)
