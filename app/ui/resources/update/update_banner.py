from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QStackedWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QDialog,
)
from PySide6.QtCore import QObject, Qt, QTimer, Signal
from PySide6.QtGui import QFont, QCursor
from pathlib import Path

from ..dialogs.extract_update_dialog import ExtractUpdateDialog
from ..dialogs.update_confirm_dialog import UpdateConfirmDialog
from ....core.workers.update_worker import UpdateWorker
from ....core.updates.updater import get_download_url, get_app_dir
from ....core.logging.logger import get_logger
from ....core.updates.installer import (
    extract_update,
    create_update_script,
    ExtractUpdateWorker,
)
import app.utils.version as V

logger = get_logger(__name__)


class UpdateBanner(QObject):

    install_requested = Signal(str)

    def __init__(self, container: QWidget, parent: None):
        super().__init__(parent)
        self._container = container
        self._release = None
        self._worker = None
        self._extract_worker = None
        self._downloaded_path = None
        self._setup_ui()

    def _setup_ui(self):
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(10, 5, 10, 5)
        self._stacked_status = QStackedWidget()
        # Pagina 1: actualizacion disponible
        self._page1_available = QWidget()
        layout_p1 = QHBoxLayout(self._page1_available)
        font1 = QFont()
        font1.setPointSize(13)
        font1.setBold(True)
        font1.setItalic(False)
        self._lbl_available = QLabel(
            "Parece que hay una nueva versión disponible de la aplicación ¿Deseas descargarla?"
        )
        self._lbl_available.setFont(font1)
        self._btn_download = QPushButton()
        self._btn_download.setText("Descargar")
        self._btn_download.setStyleSheet(
            "background-color: rgb(108, 9, 200);\n" "color: rgb(255, 255, 255);"
        )
        self._btn_download.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._btn_download.setFont(font1)
        self._btn_download.clicked.connect(self._on_download_clicked)
        layout_p1.addWidget(self._lbl_available)
        layout_p1.addWidget(self._btn_download)
        # Pagina 2: Estado de descarga
        font2 = QFont()
        font2.setPointSize(10)
        font2.setBold(True)
        font2.setItalic(False)
        self._page2_down = QWidget()
        layout_princ_p2 = QHBoxLayout(self._page2_down)
        layout_prog_p2 = QVBoxLayout()
        self._lbl_down_status = QLabel("Descargando Actualización")
        self._lbl_down_status.setFont(font1)
        self._progress_bar = QProgressBar()
        self._progress_bar.setValue(0)
        self._progress_bar.setFont(font1)
        layout_prog_p2.addWidget(self._lbl_down_status)
        layout_prog_p2.addWidget(self._progress_bar)
        layoutV_speed_p2 = QVBoxLayout()
        self._lbl_speed = QLabel("0 MB/s")
        self._lbl_speed.setFont(font2)
        self._btn_cancel_down = QPushButton()
        self._btn_cancel_down.setText("Cancelar")
        self._btn_cancel_down.setStyleSheet(
            "background-color: #E01616;\n" "color: rgb(255, 255, 255);"
        )
        self._btn_cancel_down.setFont(font1)
        self._btn_cancel_down.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._btn_cancel_down.clicked.connect(self._on_cancel_clicked)
        layoutV_speed_p2.addWidget(self._lbl_speed)
        layoutV_speed_p2.addWidget(self._btn_cancel_down)
        layout_princ_p2.addLayout(layout_prog_p2)
        layout_princ_p2.addLayout(layoutV_speed_p2)
        # Pagina 3: Descarga terminada con exito
        self._page3_done = QWidget()
        layout_p3 = QHBoxLayout(self._page3_done)
        self._lbl_done = QLabel("Descarga Terminada con Éxito")
        self._btn_install = QPushButton()
        self._btn_install.setText("Instalar")
        self._btn_install.setStyleSheet(
            "background-color: rgb(108, 9, 200);\n" "color: rgb(255, 255, 255);"
        )
        self._btn_install.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._btn_install.setFont(font1)
        self._btn_install.clicked.connect(self._on_install_clicked)
        layout_p3.addWidget(self._lbl_done)
        layout_p3.addWidget(self._btn_install)
        # Pagina 4: Descarga en error
        self._page4_error = QWidget()
        layout_p4 = QHBoxLayout(self._page4_error)
        font3 = QFont()
        font3.setPointSize(8)
        font3.setBold(True)
        font3.setItalic(False)
        self._lbl_error = QLabel("Error al descargar la actualización")
        self._lbl_error.setFont(font3)
        self._btn_retry = QPushButton()
        self._btn_retry.setText("Reintentar")
        self._btn_retry.setStyleSheet(
            "background-color: #FC8A00;\n" "color: rgb(255, 255, 255);"
        )
        self._btn_retry.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._btn_retry.setFont(font1)
        self._btn_retry.clicked.connect(self._on_retry_clicked)
        layout_p4.addWidget(self._lbl_error)
        layout_p4.addWidget(self._btn_retry)

        self._stacked_status.addWidget(self._page1_available)
        self._stacked_status.addWidget(self._page2_down)
        self._stacked_status.addWidget(self._page3_done)
        self._stacked_status.addWidget(self._page4_error)
        self._layout.addWidget(self._stacked_status)

    def _on_download_clicked(self):
        upd_conf_dialog = UpdateConfirmDialog(
            f"Actualmente tienes la versión {V.APP_VERSION}. ¿Quieres instalar la versión {self._release.get('tag_name', 'desconocida')}?",
            self._container,
        )
        if upd_conf_dialog.exec() != QDialog.Accepted:  # Si no acepto
            return

        self._show_downloading()

        url_download = get_download_url(self._release)
        if not url_download:
            self._show_error(
                "Ocurrió un error al obtener el link de descarga de la actualización. Inténtalo de nuevo más tarde."
            )
            return

        file_name = url_download.split("/")[
            -1
        ]  # Obtenemos el nombre del archivo, que sera el ultimo elemento

        self._worker = UpdateWorker(url_download, file_name)

        # Conectamos las Signals
        self._worker.progress.connect(
            lambda progress: self._progress_bar.setValue(progress)
        )
        self._worker.speed.connect(lambda speed: self._lbl_speed.setText(speed))
        self._worker.finished.connect(self._on_download_finished)
        self._worker.error.connect(self._show_error)

        self._worker.start()

    def _on_cancel_clicked(self):
        if not self._worker:
            return
        self._worker.cancel()
        self._lbl_down_status.setText("Descarga cancelada...")
        QTimer.singleShot(1500, lambda: self._set_page(self._page1_available))

    def _on_install_clicked(self):
        inst_conf_dialog = UpdateConfirmDialog(
            f"¿Deseas instalar la actualización {self._release.get('tag_name', 'desconocida')}? La aplicación se cerrará y tus descargas activas se cancelarán.",
            self._container,
        )
        if inst_conf_dialog.exec() != QDialog.Accepted:  # Si no acepto
            return

        if not self._downloaded_path:
            logger.error("No existe un archivo de actualización descargado.")
            self._show_error("No existe un archivo de actualización descargado.")
            return

        self._extract_dialog = ExtractUpdateDialog(self._container)

        self._extract_worker = ExtractUpdateWorker(self._downloaded_path)
        self._extract_worker.extract_finished.connect(self._start_extract)
        self._extract_worker.extract_finished.connect(self._extract_dialog.accept)
        self._extract_worker.extract_failed.connect(self._show_error)
        self._extract_worker.extract_failed.connect(self._extract_dialog.reject)
        self._extract_worker.progress.connect(self._extract_dialog.update_progress_bar)
        self._extract_worker.message_status.connect(
            self._extract_dialog.update_progress_msg
        )
        QTimer.singleShot(
            500, self._extract_worker.start
        )  # Despues de 500 mls ejecutamos extractworker para dar tiempo a que se muestre el dialog de carga
        self._extract_dialog.show()
        self._extract_dialog.exec()

    def _start_extract(self, extracted_dir: str):
        script_path = create_update_script(Path(extracted_dir), get_app_dir())
        self.install_requested.emit(str(script_path))

    def _on_retry_clicked(self):
        pass

    def _on_download_finished(self, filename: str):
        self._downloaded_path = filename
        self._show_done()

    def _set_page(self, widget: QWidget):
        self._stacked_status.setCurrentWidget(widget)

    def _show_downloading(self):
        self._lbl_down_status.setText("Descargando actualización")
        self._lbl_speed.setText("0 MB/s")
        self._progress_bar.setValue(0)
        self._set_page(self._page2_down)

    def _show_done(self):
        self._set_page(self._page3_done)

    def _show_error(self, message: str):
        self._lbl_error.setText(message)
        self._set_page(self._page4_error)

    def show_update_available(self, release: dict):
        self._release = release
        self._lbl_available.setText(
            f"Parece que hay una nueva versión disponible ({release.get('tag_name','desconocida')}) de la aplicación ¿Deseas descargarla?"
        )
        self._set_page(self._page1_available)

    def hide_banner(self):
        self._container.setVisible(False)
