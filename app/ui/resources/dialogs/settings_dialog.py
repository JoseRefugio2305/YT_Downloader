from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QComboBox,
    QSpinBox,
    QComboBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)

from ....core.settings.settings import Settings


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        self.setWindowTitle("Configuraciones")
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.MSWindowsFixedSizeDialogHint
        )
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
        self.lbl_dest_sel = QLabel(str(Settings.get_destination()))
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
        self.spin_num_descargas.setValue(Settings.get_max_concurrent())
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
        self.combo_vid_qual.addItem("1080p", "bestvideo[height<=1080]+bestaudio/best")
        self.combo_vid_qual.addItem("720p", "bestvideo[height<=720]+bestaudio/best")
        self.combo_vid_qual.addItem("480p", "bestvideo[height<=480]+bestaudio/best")
        self.combo_vid_qual.addItem("360p", "bestvideo[height<=360]+bestaudio/best")
        self.horizontalVQualL.addWidget(self.lbl_vid_qual)
        self.horizontalVQualL.addWidget(self.combo_vid_qual)
        # Calidad de Audio
        self.horizontalAudioQualL = QHBoxLayout()
        self.horizontalAudioQualL.setObjectName("horizontalAudioQualL")
        self.horizontalAudioQualL.setContentsMargins(0, 0, 0, 0)
        self.layoutPrinc.addLayout(self.horizontalAudioQualL)
        self.lbl_audio_qual = QLabel("Calidad de Audio: ")
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

        # Límite de velocidad
        self.horizontalSpeedL = QHBoxLayout()
        self.lbl_speed = QLabel("Límite de velocidad: ")
        self.lbl_speed.setFont(font2)
        self.combo_speed = QComboBox()
        self.combo_speed.setFont(font2)
        self.combo_speed.addItem("Sin límite", None)
        self.combo_speed.addItem("512 KB/s", 512000)
        self.combo_speed.addItem("1 MB/s", 1024000)
        self.combo_speed.addItem("2 MB/s", 2048000)
        self.combo_speed.addItem("5 MB/s", 5120000)
        self.horizontalSpeedL.addWidget(self.lbl_speed)
        self.horizontalSpeedL.addWidget(self.combo_speed)
        self.layoutPrinc.addLayout(self.horizontalSpeedL)

        # Delay entre descargas
        self.horizontalDelayL = QHBoxLayout()
        self.lbl_delay = QLabel("Espera entre descargas (seg): ")
        self.lbl_delay.setFont(font2)
        self.spin_delay = QSpinBox()
        self.spin_delay.setFont(font2)
        self.spin_delay.setRange(0, 60)
        self.spin_delay.setValue(Settings.get_download_delay())
        self.horizontalDelayL.addWidget(self.lbl_delay)
        self.horizontalDelayL.addWidget(self.spin_delay)
        self.layoutPrinc.addLayout(self.horizontalDelayL)

        # Límite de velocidad
        self.horizontalClientL = QHBoxLayout()
        self.lbl_client = QLabel("Cliente (Player Client): ")
        self.lbl_client.setFont(font2)
        self.combo_player_client = QComboBox()
        self.combo_player_client.setFont(font2)
        self.combo_player_client.addItem(
            "TV (Mejor calidad de descarga)", ["tv_embedded"]
        )
        self.combo_player_client.addItem("Web/Android", ["web", "android"])
        self.combo_player_client.addItem("Todos", ["tv_embedded" "web", "android"])
        self.horizontalClientL.addWidget(self.lbl_client)
        self.horizontalClientL.addWidget(self.combo_player_client)
        self.layoutPrinc.addLayout(self.horizontalClientL)

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

    def _browse_destination(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
        if folder:
            self.lbl_dest_sel.setText(folder)

    def _apply_settings(self):
        Settings._settings.setValue("destination", self.lbl_dest_sel.text())
        Settings._settings.setValue("max_concurrent", self.spin_num_descargas.value())
        Settings._settings.setValue("max_vid_qual", self.combo_vid_qual.currentData())
        Settings._settings.setValue("max_aud_qual", self.combo_aud_qual.currentData())
        Settings._settings.setValue("speed_limit", self.combo_speed.currentData())
        Settings._settings.setValue("download_delay", self.spin_delay.value())
        Settings._settings.setValue(
            "player_client", self.combo_player_client.currentData()
        )
        self.accept()

    def _load_settings(self):
        self.lbl_dest_sel.setText(str(Settings.get_destination()))
        self.spin_num_descargas.setValue(Settings.get_max_concurrent())

        idx = self.combo_vid_qual.findData(Settings.get_video_quality())
        if idx >= 0:
            self.combo_vid_qual.setCurrentIndex(idx)

        idx = self.combo_aud_qual.findData(Settings.get_audio_quality())
        if idx >= 0:
            self.combo_aud_qual.setCurrentIndex(idx)

        idx = self.combo_speed.findData(Settings.get_speed_limit())
        if idx >= 0:
            self.combo_speed.setCurrentIndex(idx)

        idx = self.combo_player_client.findData(Settings.get_player_client())
        if idx >= 0:
            self.combo_player_client.setCurrentIndex(idx)

        self.spin_delay.setValue(Settings.get_download_delay())

    def _cancel_dialog(self):
        self.close()
