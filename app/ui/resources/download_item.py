from PySide6.QtCore import QRect, QSize, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QHBoxLayout,
    QProgressBar,
    QWidget,
)

from ...utils.text_helpers import get_status_color
from ...core.download_worker import DownloadWorker


class DownloadItem(QWidget):
    # Accion de cancelar y de reintentar
    cancel_requested = Signal(int)
    retry_requested = Signal(int)
    remove_requested = Signal(
        int
    )  # Removerlo de la lista una vez esta complatado, cancelado o fallo

    STYLE_NORMAL = "background: #B0B0B0; border-radius: 10px;"
    STYLE_HOVER = "background: #909090; border-radius: 10px;"

    def __init__(self, download_id: int, title: str, parent=None):
        super().__init__(parent)
        self._download_id = download_id
        self._worker = None
        self._title = title
        self._setup_ui()

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
        self.verticalPrincLW = QWidget(self)
        self.verticalPrincLW.setObjectName("verticalPrincLW")
        self.verticalPrincLW.setGeometry(QRect(0, 0, 950, 90))
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
        self.btnCancel.clicked.connect(
            lambda: self.cancel_requested.emit(self._download_id)
        )
        self.horizontalBtnActionsL.addWidget(self.btnCancel)
        # Boton de Reintentar
        self.btnRetry = QPushButton()
        self.btnRetry.setObjectName("btnRetry")
        self.btnRetry.setText("Reintentar")
        self.btnRetry.setFont(font1)
        self.btnRetry.setStyleSheet(
            "background-color : #FC8A00; color : white; padding:5px; border-radius:10px;"
        )
        self.btnRetry.setVisible(False)
        self.btnRetry.clicked.connect(
            lambda: self.retry_requested.emit(self._download_id)
        )
        self.horizontalBtnActionsL.addWidget(self.btnRetry)
        # Boton de eliminar de la lista
        self.btnRemove = QPushButton()
        self.btnRemove.setObjectName("btnRemove")
        self.btnRemove.setText("X")
        self.btnRemove.setFont(font1)
        self.btnRemove.setStyleSheet(
            "background-color : #6B7280; color : white; padding:10px; border-radius:10px;"
        )
        self.btnRemove.setVisible(False)
        self.btnRemove.clicked.connect(
            lambda: self.remove_requested.emit(self._download_id)
        )
        self.horizontalBtnActionsL.addWidget(self.btnRemove)

    def update_progress(self, percent: int):
        self.progressBar.setValue(percent)
        self.lblPercent.setText(f"{percent}%")

    def update_speed(self, speed: str):
        self.lblSpeed.setText(speed)

    def update_eta(self, eta: str):
        self.lblETA.setText(eta)

    def update_status(self, status: str):
        self.lblStatus.setText(status)
        self.lblStatus.setStyleSheet(f"color:{get_status_color(status)};")
        self.btnCancel.setVisible(status in ("downloading", "pending"))
        self.btnRetry.setVisible(status in ("failed", "cancelled"))
        self.btnRemove.setVisible(status in ("failed", "cancelled", "completed"))

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

    # Eventos para simular el hover
    def enterEvent(self, event):
        self.setStyleSheet("background: #909090; border-radius: 10px;")
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet("background: #B0B0B0; border-radius: 10px;")
        super().leaveEvent(event)
