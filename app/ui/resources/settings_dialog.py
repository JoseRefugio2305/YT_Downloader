from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
    Signal,
    QSettings,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QComboBox,
    QSpinBox,
    QComboBox,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QProgressBar,
    QWidget,
    QMessageBox,
)
from pathlib import Path


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = QSettings("YTDownloader", "config")
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        self.setWindowTitle("Configuraciones")
        self.layoutPrinc = QVBoxLayout()  # Layout General
        font1 = QFont()
        font1.setPointSize(20)
        font1.setBold(True)
        font1.setItalic(False)
        self.lbl_title = QLabel("Configuraciones")
        self.lbl_title.setFont(font1)
        self.layoutPrinc.addWidget(self.lbl_title)
        # Destino de descargas
        self.horizontalDestL = QHBoxLayout()
        self.horizontalDestL.setObjectName("horizontalDestL")
        self.horizontalDestL.setContentsMargins(0, 0, 0, 0)
        self.layoutPrinc.addLayout(self.horizontalDestL)
        font2 = QFont()
        font2.setPointSize(13)
        font2.setBold(False)
        font2.setItalic(False)
        self.lbl_dest_ind = QLabel("Carpeta de descargas: ")
        self.lbl_dest_ind.setFont(font2)
        self.lbl_dest_sel = QLabel(str(self.get_destination()))
        self.lbl_dest_sel.setFont(font2)
        self.btn_select_route = QPushButton()
        self.btn_select_route.setObjectName("btnSelRoute")
        self.btn_select_route.setText("Seleccionar Carpeta...")
        self.btn_select_route.setFont(font2)
        self.btn_select_route.clicked.connect(self._browse_destination)
        self.horizontalDestL.addWidget(self.lbl_dest_ind)
        self.horizontalDestL.addWidget(self.lbl_dest_sel)
        self.horizontalDestL.addWidget(self.btn_select_route)
        # Maximo de descargas simultaneas
        self.horizontalMaxDL = QHBoxLayout()
        self.horizontalMaxDL.setObjectName("horizontalMaxDL")
        self.horizontalMaxDL.setContentsMargins(0, 0, 0, 0)
        self.layoutPrinc.addLayout(self.horizontalMaxDL)
        self.lbl_max_desc = QLabel("Max. Descargas simultaneas: ")
        self.lbl_max_desc.setFont(font2)
        self.spin_num_descargas = QSpinBox()
        self.spin_num_descargas.setObjectName("spinDescargas")
        self.spin_num_descargas.setRange(1, 5)
        self.spin_num_descargas.lineEdit().setReadOnly(True)
        self.spin_num_descargas.setFont(font2)
        self.spin_num_descargas.setValue(self.get_max_concurrent())
        self.horizontalMaxDL.addWidget(self.lbl_max_desc)
        self.horizontalMaxDL.addWidget(self.spin_num_descargas)
        # Calidad de video
        self.horizontalVQualL = QHBoxLayout()
        self.horizontalVQualL.setObjectName("horizontalVQualL")
        self.horizontalVQualL.setContentsMargins(0, 0, 0, 0)
        self.layoutPrinc.addLayout(self.horizontalVQualL)
        self.lbl_vid_qual = QLabel("Calidad de Video: ")
        self.lbl_vid_qual.setFont(font2)
        self.combo_vid_qual = QComboBox()
        self.combo_vid_qual.setObjectName("combo_vid_qual")
        self.combo_vid_qual.setFont(font2)
        self.combo_vid_qual.addItem("Mejor Calidad", "bestvideo+bestaudio/best")
        self.combo_vid_qual.addItem("1080", "bestvideo[height<=1080]+bestaudio/best")
        self.combo_vid_qual.addItem("720", "bestvideo[height<=720]+bestaudio/best")
        self.combo_vid_qual.addItem("480", "bestvideo[height<=480]+bestaudio/best")
        self.combo_vid_qual.addItem("360", "bestvideo[height<=360]+bestaudio/best")
        self.horizontalVQualL.addWidget(self.lbl_vid_qual)
        self.horizontalVQualL.addWidget(self.combo_vid_qual)
        # Calidad de Audio
        self.horizontalAudioQualL = QHBoxLayout()
        self.horizontalAudioQualL.setObjectName("horizontalAudioQualL")
        self.horizontalAudioQualL.setContentsMargins(0, 0, 0, 0)
        self.layoutPrinc.addLayout(self.horizontalAudioQualL)
        self.lbl_audio_qual = QLabel("Calidad de Video: ")
        self.lbl_audio_qual.setFont(font2)
        self.combo_aud_qual = QComboBox()
        self.combo_aud_qual.setObjectName("combo_aud_qual")
        self.combo_aud_qual.setFont(font2)
        self.combo_aud_qual.addItem("Mejor Calidad", "0")
        self.combo_aud_qual.addItem("Ata", "2")
        self.combo_aud_qual.addItem("Media", "5")
        self.combo_aud_qual.addItem("Baja", "7")
        self.horizontalAudioQualL.addWidget(self.lbl_audio_qual)
        self.horizontalAudioQualL.addWidget(self.combo_aud_qual)

        # Botones Aplicar/Cancelar
        self.horizontalBtnFooterL = QHBoxLayout()
        self.horizontalBtnFooterL.setObjectName("horizontalBtnFooterL")
        self.horizontalBtnFooterL.setContentsMargins(0, 0, 0, 0)
        self.layoutPrinc.addLayout(self.horizontalBtnFooterL)
        self.btn_apply = QPushButton()
        self.btn_apply.setObjectName("btnApply")
        self.btn_apply.setText("Aplicar")
        self.btn_apply.setFont(font2)
        self.btn_apply.clicked.connect(self._apply_settings)
        self.btn_cancel = QPushButton()
        self.btn_cancel.setObjectName("btnCancel")
        self.btn_cancel.setText("Cancelar")
        self.btn_cancel.setFont(font2)
        self.btn_cancel.clicked.connect(self._cancel_dialog)
        self.horizontalBtnFooterL.addWidget(self.btn_apply)
        self.horizontalBtnFooterL.addWidget(self.btn_cancel)

        self.setLayout(self.layoutPrinc)

    def get_destination(self) -> str:
        path = self._settings.value("destination", Path.home() / "Downloads", type=str)
        return path

    def get_max_concurrent(self) -> int:
        max_concurrent = self._settings.value("max_concurrent", 2, type=int)
        return max_concurrent

    def get_video_quality(self) -> str:
        max_vid_qual = self._settings.value(
            "max_vid_qual", "bestvideo[height<=1080]+bestaudio/best"
        )
        return max_vid_qual

    def get_audio_quality(self) -> str:
        max_aud_qual = self._settings.value("max_aud_qual", "0")
        return max_aud_qual

    def _browse_destination(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
        if folder:
            self.lbl_dest_sel.setText(folder)

    def _apply_settings(self):
        self._settings.setValue("destination", self.lbl_dest_sel.text())
        self._settings.setValue("max_concurrent", self.spin_num_descargas.value())
        self._settings.setValue("max_vid_qual", self.combo_vid_qual.currentData())
        self._settings.setValue("max_aud_qual", self.combo_aud_qual.currentData())
        self.accept()

    def _load_settings(self):
        self.lbl_dest_sel.setText(str(self.get_destination()))
        self.spin_num_descargas.setValue(self.get_max_concurrent())

        idx = self.combo_vid_qual.findData(self.get_video_quality())
        if idx >= 0:
            self.combo_vid_qual.setCurrentIndex(idx)
        idx = self.combo_aud_qual.findData(self.get_audio_quality())
        if idx >= 0:
            self.combo_aud_qual.setCurrentIndex(idx)

    def _cancel_dialog(self):
        self.close()
