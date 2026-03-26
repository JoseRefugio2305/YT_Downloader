from PySide6.QtWidgets import QMainWindow, QMessageBox, QApplication
from PySide6.QtCore import QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QCloseEvent
from typing import Optional
from pathlib import Path

from .resources.tabs.main_ui import UIMainWindow
from .resources.dialogs.settings_dialog import SettingsDialog
from .resources.download.download_queue import DownloadQueue
from .resources.tabs.history_panel import HistoryPanel
from .resources.dialogs.loading_dialog import LoadingDialog
from .resources.update.update_banner import UpdateBanner
from ..database.db_manager import DBManager
from ..core.playlist_manager import PlaylistManager
from ..core.workers.extract_worker import ExtractInfoWorker
from ..utils.url_validator import detect_url_type, clean_yt_url, is_valid_url
from ..core.settings.settings import Settings
from ..core.updates.updater import CheckUpdateWorker
from ..core.updates.installer import launch_update_and_exit
from ..core.logging.logger import get_logger

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = UIMainWindow()
        self.ui.setupUi(self)
        self.ui.btnDownload.clicked.connect(self._on_download_clicked)
        self.ui.btn_settings.clicked.connect(self._open_settings)
        self.ui.btnPasteLink.clicked.connect(self._on_paste_clicked)
        self.ui.btnCancelAll.clicked.connect(self._on_cancel_all_clicked)
        self._settings = SettingsDialog(self)
        self._db = DBManager()
        self._manager = PlaylistManager(
            db=self._db, max_concurrent=Settings.get_max_concurrent()
        )
        self._queue = DownloadQueue(self.ui.scrollDownloads, self._manager, self._db)
        self._update_banner = UpdateBanner(self.ui.widgetUpdate, self)
        self._update_banner.install_requested.connect(self._on_install_requested)
        self.ui.btnCleanAll.clicked.connect(self._queue._on_clear_finished)
        self._history = HistoryPanel(
            self.ui.tableHistorial, self.ui.widgetBusHistorial, self._queue, self._db
        )
        self._extract_worker = None
        self._closing_for_update = False
        self._connect_signals()
        QTimer.singleShot(3000, self._check_for_updates)

    def _connect_signals(self):
        # self._manager.item_finished.connect(self._on_item_finished)
        self._manager.all_finished.connect(self._on_all_finished)

    def _on_all_finished(self):
        self._history.refresh()

    def _on_download_clicked(self):
        url = self.ui.inputLink.text().strip()
        format = self.ui.comboBox.currentText().lower()  # 'mp3' o 'mp4'

        if not is_valid_url(url):
            logger.error(f"url {url} invalido")
            self._show_dialog_error("El link no es un link de una red social valida.")
            return

        type_url = detect_url_type(url)

        if type_url == "unknown":
            logger.error(f"url {url} de tipo desconocido")
            self._show_dialog_error("No se pudo determinar el tipo de URL.")
            return

        if type_url == "video/playlist":
            is_video_sel = self._show_dialog_type_download()
            type_url = "video" if is_video_sel else "playlist"
            playlist_url, video_url = clean_yt_url(url)
            url = video_url if is_video_sel else playlist_url

        self._extract_worker = ExtractInfoWorker(
            url,
            type_url,
            format,
            video_quality=Settings.get_video_quality(),
            audio_quality=Settings.get_audio_quality(),
        )
        # Activamos dialog de carga
        self._loading = LoadingDialog(
            "Obteniendo información, espera un momento...", self
        )
        # Conectamos a funciones para cerrar dialogo
        self._extract_worker.finished.connect(self._loading.accept)
        self._extract_worker.error.connect(self._loading.reject)
        # Conectamos a funcioens para revisar la infor o el error
        self._extract_worker.finished.connect(self._on_info_extracted)
        self._extract_worker.error.connect(self._on_extract_error)
        QTimer.singleShot(
            500, self._extract_worker.start
        )  # Despues de 100 mls ejecutamos extractworker para dar tiempo a que se muestre el dialog de carga
        self._loading.show()
        self._loading.exec()

    def _on_cancel_all_clicked(self):
        msgBox = QMessageBox(self)
        msgBox.setIcon(QMessageBox.Icon.Question)
        msgBox.setWindowTitle("Confirmar Cancelación")
        msgBox.setText(
            "¿Estás seguro de que deseas CANCELAR todas las descargas activas?"
        )
        msgBox.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        buttonY = msgBox.button(QMessageBox.StandardButton.Yes)
        buttonY.setText("Si")

        buttonN = msgBox.button(QMessageBox.StandardButton.No)
        buttonN.setText("No")

        ret = msgBox.exec()

        if msgBox.clickedButton() == buttonY:
            self._manager.cancel_all()

    def _on_info_extracted(self, playlist_info: Optional[dict], videos: list):
        destination = Settings.get_destination()
        format = self.ui.comboBox.currentText().lower()  # 'mp3' o 'mp4'

        if len(videos) == 0:
            logger.error(
                "Ocurrió un error al intentar obtener la información de la plalist"
            )
            self._show_dialog_error(
                "Ocurrió un error al intentar obtener la información de la plalist"
            )
            return
        elif len(videos) == 1 and not videos[0]:
            logger.error(
                "Ocurrió un error al intentar obtener la información del video"
            )
            self._show_dialog_error(
                "Ocurrió un error al intentar obtener la información del video"
            )
            return

        for video in videos:
            if playlist_info:
                new_download_id = self._manager.enqueue(
                    video["title"],
                    video["url"],
                    format,
                    destination,
                    video["id"],
                    playlist_info["id"],
                    playlist_info["url"],
                    playlist_info["title"],
                    playlist_info["playlist_count"],
                )
            else:
                new_download_id = self._manager.enqueue(
                    video["title"], video["url"], format, destination, video["id"]
                )
            self._queue.add_item(new_download_id, video["title"])

        self._manager.start_enqueue()  # Una vez que todos los elementos fuero agregados a la lista de descargas y a la cola de descargas iniciamos las descargas en la cola

    def _on_extract_error(self, error: str):
        self._show_dialog_error(f"Error al obtener información: {error}")

    def _show_dialog_error(self, message: str):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(message)
        msg.setWindowTitle("Mensaje")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    def _show_dialog_type_download(self) -> bool:  # Video True, playlist False

        msgBox = QMessageBox(self)
        msgBox.setIcon(QMessageBox.Icon.Question)
        msgBox.setWindowTitle("URL de Playlist Detectada")
        msgBox.setText(
            "El link que agregaste es de un video extraído desde una playlist ¿Quieres descargar ese video o la playlist completa?"
        )
        msgBox.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        buttonY = msgBox.button(QMessageBox.StandardButton.Yes)
        buttonY.setText("Descargar Video")

        buttonN = msgBox.button(QMessageBox.StandardButton.No)
        buttonN.setText("Descargar Playlist")

        ret = msgBox.exec()
        return msgBox.clickedButton() == buttonY

    def _open_settings(self):
        self._settings.exec()

    def _on_paste_clicked(self):
        clipboard = QApplication.clipboard()
        self.ui.inputLink.setText(clipboard.text().strip())

    def _check_for_updates(self):
        self._check_update_worker = CheckUpdateWorker()
        self._check_update_worker.update_available.connect(self._on_update_available)
        self._check_update_worker.no_update.connect(
            lambda: logger.info("No Existen actualizaciones nuevas disponibles.")
        )
        self._check_update_worker.start()

    def _on_update_available(self, new_release: dict):
        self._update_banner.show_update_available(new_release)
        self._show_update_banner()

    def _show_update_banner(self):
        BANNER_HEIGHT = 80

        # Reducimos scroll
        scroll = self.ui.scrollDownloads
        scroll_bottom = scroll.y() + scroll.height()

        self.ui.tab_3.setFixedHeight(self.ui.tab_3.height() + BANNER_HEIGHT)
        self.ui.verticalLayoutWidget.setFixedHeight(
            self.ui.verticalLayoutWidget.height() + BANNER_HEIGHT
        )

        self.ui.widgetUpdate.setGeometry(10, scroll_bottom, 981, 0)

        # Animcacion para mostrar banner
        self.ui.widgetUpdate.setVisible(True)

        self._anim_widget = QPropertyAnimation(self.ui.widgetUpdate, b"maximumHeight")
        self._anim_widget.setDuration(300)
        self._anim_widget.setStartValue(0)
        self._anim_widget.setEndValue(BANNER_HEIGHT)
        self._anim_widget.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim_widget.start()

        self._anim_widget_min = QPropertyAnimation(
            self.ui.widgetUpdate, b"minimumHeight"
        )
        self._anim_widget_min.setDuration(300)
        self._anim_widget_min.setStartValue(0)
        self._anim_widget_min.setEndValue(BANNER_HEIGHT)
        self._anim_widget_min.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim_widget_min.start()

        # # Animacion de ventana
        current_height = self.height()
        self._anim_window = QPropertyAnimation(self, b"minimumHeight")
        self._anim_window.setDuration(300)
        self._anim_window.setStartValue(current_height)
        self._anim_window.setEndValue(current_height + BANNER_HEIGHT)
        self._anim_window.valueChanged.connect(lambda v: self.setFixedHeight(v))
        self._anim_window.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim_window.start()

    def _on_install_requested(self, script_path: str):
        self._closing_for_update = True
        launch_update_and_exit(Path(script_path))

    def closeEvent(self, event: QCloseEvent):

        if self._closing_for_update:  # Si se cierra por actualizacion
            self._manager.cancel_all()
            self._db.close()
            event.accept()
            return

        msgBox = QMessageBox(self)
        msgBox.setIcon(QMessageBox.Icon.Question)
        msgBox.setWindowTitle("Confirmar salida")
        msgBox.setText(
            "¿Estás seguro de que deseas salir? Se cancelaran las descargas activas."
        )
        msgBox.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        buttonY = msgBox.button(QMessageBox.StandardButton.Yes)
        buttonY.setText("Salir")

        buttonN = msgBox.button(QMessageBox.StandardButton.No)
        buttonN.setText("Cancelar")

        ret = msgBox.exec()

        if msgBox.clickedButton() == buttonY:
            self._manager.cancel_all()
            self._db.close()
            logger.info("Saliendo de aplicacion")
            event.accept()  # Cierra la ventana
        else:
            event.ignore()  # Cancela el cierre

    def close_for_update(self):
        self._closing_for_update = True
        self.close()
