from PySide6.QtCore import QRect, QSize, Qt, Signal
from PySide6.QtGui import QFont, QCursor
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QHBoxLayout,
    QProgressBar,
    QDialog,
    QMessageBox,
    QWidget,
)
from pathlib import Path
from pathvalidate import sanitize_filename

from ....utils.text_helpers import get_status_color
from ....core.workers.download_worker import DownloadWorker
from ....database.db_manager import DBManager
from ...resources.dialogs.rename_dialog import RenameDialog
from ....core.logging.logger import get_logger

logger = get_logger(__name__)


class DownloadItem(QWidget):
    # Accion de cancelar y de reintentar
    cancel_requested = Signal(int)
    retry_requested = Signal(int)
    remove_requested = Signal(
        int
    )  # Removerlo de la lista una vez esta complatado, cancelado o fallo

    STYLE_NORMAL = "background: #B0B0B0; border-radius: 10px;"
    STYLE_HOVER = "background: #909090; border-radius: 10px;"

    def __init__(self, download_id: int, title: str, db: DBManager, parent=None):
        super().__init__(parent)
        self._db = db
        self._download_id = download_id
        self._worker = None
        self._title = title
        self._status = "pending"
        self._setup_ui()

    @property
    def current_status(self) -> str:
        return self._status

    def _setup_ui(self):
        self.resize(700, 650)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background: #B0B0B0; border-radius: 10px;")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QSize(950, 90))
        self.setMaximumSize(QSize(950, 90))

        # Vertical Layout Principal
        self.verticalPrincL = QVBoxLayout(self)
        self.verticalPrincL.setObjectName("verticalPrincL")
        self.verticalPrincL.setContentsMargins(5, 5, 5, 5)
        # Titulo
        font1 = QFont()
        font1.setPointSize(13)
        font1.setBold(True)
        font1.setItalic(False)
        self.lblTitulo = QLabel()
        self.lblTitulo.setObjectName("lblTitulo")
        self.lblTitulo.setFont(font1)
        self.lblTitulo.setText(self._title)
        self.verticalPrincL.addWidget(self.lblTitulo)
        # Laylout horizontal para area de estado de descarga y para area de botones
        self.horizontalInfoBtnL = QHBoxLayout()
        self.horizontalInfoBtnL.setObjectName("horizontalInfoBtnL")
        self.horizontalInfoBtnL.setGeometry(QRect(0, 0, 950, 30))
        self.horizontalInfoBtnL.setContentsMargins(0, 0, 0, 0)
        self.verticalPrincL.addLayout(self.horizontalInfoBtnL)
        # Layout para area de estado de descarga
        self.verticalStatusDwnL = QVBoxLayout()
        self.verticalStatusDwnL.setObjectName("verticalStatusDwnL")
        self.verticalStatusDwnL.setGeometry(QRect(0, 0, 950, 30))
        self.verticalStatusDwnL.setContentsMargins(0, 0, 0, 0)
        self.horizontalInfoBtnL.addLayout(self.verticalStatusDwnL)

        # Segunda linea Barra de progreso
        # Barra de progreso
        self.progressBar = QProgressBar()
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setFont(font1)
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(False)  # <- oculta el texto dentro de la barra
        self.horizontalProgL = QHBoxLayout()
        self.horizontalProgL.setContentsMargins(0, 0, 0, 0)
        self.horizontalProgL.addWidget(self.progressBar)

        # Label de porcentaje a la derecha
        self.lblPercent = QLabel("0%")
        self.lblPercent.setObjectName("lblPercent")
        self.lblPercent.setFont(font1)
        self.lblPercent.setFixedWidth(45)
        self.horizontalProgL.addWidget(self.lblPercent)
        self.verticalStatusDwnL.addLayout(self.horizontalProgL)
        # Tercera linea de informacion de progreso
        self.horizontalInfoL = QHBoxLayout()
        self.horizontalInfoL.setObjectName("horizontalInfoL")
        self.horizontalInfoL.setGeometry(QRect(0, 60, 950, 30))
        self.horizontalInfoL.setContentsMargins(0, 0, 0, 0)
        self.verticalStatusDwnL.addLayout(self.horizontalInfoL)
        font2 = QFont()
        font2.setPointSize(10)
        font2.setBold(True)
        font2.setItalic(False)
        font2.setUnderline(True)
        self.lblSpeed = QLabel()
        self.lblSpeed.setObjectName("lblSpeed")
        self.lblSpeed.setFont(font2)
        self.lblSpeed.setText("- MB/s")
        self.horizontalInfoL.addWidget(self.lblSpeed)
        self.lblETA = QLabel()
        self.lblETA.setObjectName("lblETA")
        self.lblETA.setFont(font2)
        self.lblETA.setText("00:00")
        self.horizontalInfoL.addWidget(self.lblETA)
        self.lblFileSize = QLabel()
        self.lblFileSize.setObjectName("lblFileSize")
        self.lblFileSize.setFont(font2)
        self.lblFileSize.setText("Tamaño estimado: 00 KB")
        self.horizontalInfoL.addWidget(self.lblFileSize)
        self.lblStatus = QLabel()
        self.lblStatus.setObjectName("lblStatus")
        font3 = QFont()
        font3.setPointSize(13)
        font3.setBold(True)
        font3.setItalic(False)
        font3.setUnderline(True)
        self.lblStatus.setFont(font3)
        self.lblStatus.setText("...")
        self.lblStatus.setStyleSheet(f"color:{get_status_color('pending')};")
        self.horizontalInfoL.addWidget(self.lblStatus)

        # Layout vertical de botones
        self.horizontalBtnActionsL = QHBoxLayout()
        self.horizontalBtnActionsL.setObjectName("horizontalBtnActionsL")
        self.horizontalBtnActionsL.setGeometry(QRect(0, 0, 950, 30))
        self.horizontalBtnActionsL.setContentsMargins(30, 0, 30, 0)
        self.horizontalInfoBtnL.addLayout(self.horizontalBtnActionsL)

        # Boton Cancelar
        self.btnCancel = QPushButton()
        self.btnCancel.setObjectName("btnCancel")
        self.btnCancel.setText("Cancelar")
        self.btnCancel.setFont(font1)
        self.btnCancel.setStyleSheet(
            "background-color : #E01616; color : white; padding:5px; border-radius:10px;"
        )
        self.btnCancel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btnCancel.clicked.connect(self._on_cancel_clicked)
        self.horizontalBtnActionsL.addWidget(self.btnCancel)
        # Boton de Reintentar
        self.btnRetry = QPushButton()
        self.btnRetry.setObjectName("btnRetry")
        self.btnRetry.setText("Reintentar")
        self.btnRetry.setFont(font1)
        self.btnRetry.setStyleSheet(
            "background-color : #FC8A00; color : white; padding:5px; border-radius:10px;"
        )
        self.btnRetry.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btnRetry.setVisible(False)
        self.btnRetry.clicked.connect(
            lambda: self.retry_requested.emit(self._download_id)
        )
        self.horizontalBtnActionsL.addWidget(self.btnRetry)
        # Boton de renombrar archivo desde app
        self.btnRename = QPushButton()
        self.btnRename.setObjectName("btnRename")
        self.btnRename.setText("Renombrar")
        self.btnRename.setFont(font1)
        self.btnRename.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btnRename.setStyleSheet(
            "background-color : #064E6F; color : white; padding:5px; border-radius:10px;"
        )
        self.btnRename.setVisible(False)
        self.btnRename.clicked.connect(self._on_rename_clicked)
        self.horizontalBtnActionsL.addWidget(self.btnRename)
        # Boton de eliminar de la lista
        self.btnRemove = QPushButton()
        self.btnRemove.setObjectName("btnRemove")
        self.btnRemove.setText("X")
        self.btnRemove.setFont(font1)
        self.btnRemove.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btnRemove.setStyleSheet(
            "background-color : #6B7280; color : white; padding:10px; border-radius:10px;"
        )
        self.btnRemove.setVisible(False)
        self.btnRemove.clicked.connect(
            lambda: self.remove_requested.emit(self._download_id)
        )
        self.horizontalBtnActionsL.addWidget(self.btnRemove)

    def update_download_id(self, new_id: int):
        self._download_id = new_id

    def update_progress(self, percent: int):
        self.progressBar.setValue(percent)
        self.lblPercent.setText(f"{percent}%")

    def update_file_size(self, size: str):
        self.lblFileSize.setText(size)

    def update_speed(self, speed: str):
        self.lblSpeed.setText(speed)

    def update_eta(self, eta: str):
        self.lblETA.setText(eta)

    def update_status(self, status: str):
        self._status = status
        self.lblStatus.setText(status)
        self.lblStatus.setStyleSheet(f"color:{get_status_color(status)};")
        self.btnCancel.setVisible(status in ("downloading", "pending"))
        self.btnRetry.setVisible(status in ("failed", "cancelled"))
        self.btnRemove.setVisible(status in ("failed", "cancelled", "completed"))
        self.btnRename.setVisible(status == "completed")

        if status in ("completed", "failed", "cancelled"):
            self._worker = None  # liberamos la referencia

    def assign_worker(self, worker: DownloadWorker):
        self._worker = worker
        self._connect_worker_signals()

    def _connect_worker_signals(self):
        self._worker.progress.connect(self.update_progress)
        self._worker.speed.connect(self.update_speed)
        self._worker.eta.connect(self.update_eta)
        self._worker.status_changed.connect(self.update_status)
        self._worker.file_size.connect(self.update_file_size)

    def _on_rename_clicked(self):
        download = self._db.get_download_by_id(self._download_id)
        current_path = Path(download.destination_path)
        dialog = RenameDialog(
            current_path.stem, self
        )  # Con stem obtenemos el nombre sin extension

        if dialog.exec() != QDialog.Accepted:  # Si no acepto
            return
        new_name = sanitize_filename(dialog.get_title(), "")
        new_path = current_path.parent / f"{new_name}{current_path.suffix}"
        if new_path.exists():
            # Avisamos que ya existe un archivo con ese nombre
            logger.error(
                "Ya existe un archivo con ese nombre en la carpeta de destino."
            )
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("Ya existe un archivo con ese nombre en la carpeta de destino.")
            msg.exec()
            return

        try:
            current_path.rename(new_path)
            self._title = new_name
            self.lblTitulo.setText(new_name)
            self._db.update_download_info(
                self._download_id, title=new_name, destination_path=str(new_path)
            )
        except Exception as e:
            logger.error(f"No se pudo renombrar el archivo: {str(e)}")
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText(f"No se pudo renombrar el archivo: {str(e)}")
            msg.exec()

    def _on_cancel_clicked(self):
        msgBox = QMessageBox(self)
        msgBox.setIcon(QMessageBox.Icon.Question)
        msgBox.setStyleSheet("QLineEdit { background-color: palette(base);}")
        msgBox.setWindowTitle("Confirmar Cancelación")
        msgBox.setText(
            f"¿Estás seguro de que deseas CANCELAR la descarga de {self._title}?"
        )
        msgBox.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        buttonY = msgBox.button(QMessageBox.StandardButton.Yes)
        buttonY.setText("Si")
        buttonY.setStyleSheet(
            "background-color : #064E6F; color : white; padding:5px; border-radius:10px;"
        )

        buttonN = msgBox.button(QMessageBox.StandardButton.No)
        buttonN.setText("No")
        buttonN.setStyleSheet(
            "background-color : #525252; color : white; padding:5px; border-radius:10px;"
        )

        ret = msgBox.exec()

        if msgBox.clickedButton() == buttonY:
            self.cancel_requested.emit(self._download_id)

    # Eventos para simular el hover
    def enterEvent(self, event):
        self.setStyleSheet("background: #909090; border-radius: 10px;")
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet("background: #B0B0B0; border-radius: 10px;")
        super().leaveEvent(event)
