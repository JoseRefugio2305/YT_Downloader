from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QMovie
from PySide6.QtWidgets import QLabel, QVBoxLayout, QDialog, QProgressBar, QHBoxLayout
from pathlib import Path
import random

from ....utils.constants import LOADING_GIFS_LIST


class ExtractUpdateDialog(QDialog):
    ASSETS_DIR = Path(__file__).parent.parent.parent.parent.parent / "assets"

    GIF = (
        LOADING_GIFS_LIST[0]
        if random.random() < 0.92
        else random.choice(LOADING_GIFS_LIST)
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setWindowTitle("Extrayendo...")
        self.setModal(True)
        self.setFixedSize(600, 400)
        self.layout_princ = QVBoxLayout()
        font = QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setItalic(False)
        self.label_msg = QLabel("Extrayendo archivo de acutalización...")
        self.label_msg.setFont(font)
        self.label_msg.setAlignment(Qt.AlignCenter)
        self.label_info_extract = QLabel("Se han extraído – MB de – MB.")
        self.label_info_extract.setFont(font)
        self.label_info_extract.setAlignment(Qt.AlignCenter)
        self.horizontalProgL = QHBoxLayout()
        self.horizontalProgL.setContentsMargins(0, 0, 0, 0)
        self.progressBar = QProgressBar()
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setFont(font)
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(False)  # oculta el texto dentro de la barra
        self.horizontalProgL.addWidget(self.progressBar)
        self.lblPercent = QLabel("0%")
        self.lblPercent.setObjectName("lblPercent")
        self.lblPercent.setFont(font)
        self.lblPercent.setFixedWidth(45)
        self.horizontalProgL.addWidget(self.lblPercent)
        self.loading_gif = QMovie(str(self.ASSETS_DIR / self.GIF))
        self.loading_gif.setScaledSize(QSize(200, 200))
        self.label_gif = QLabel(self)
        self.label_gif.setAlignment(Qt.AlignCenter)
        self.label_gif.setMovie(self.loading_gif)
        if self.loading_gif.isValid():
            self.loading_gif.start()  # Iniciamos la animacion
        self.layout_princ.addWidget(self.label_msg)
        self.layout_princ.addWidget(self.label_info_extract)
        self.layout_princ.addLayout(self.horizontalProgL)
        self.layout_princ.addWidget(self.label_gif)

        self.setLayout(self.layout_princ)

    def update_progress_bar(self, progress: int):
        self.lblPercent.setText(f"{progress}%")
        self.progressBar.setValue(progress)

    def update_progress_msg(self, list_msgs: list[str]):
        self.label_msg.setText(list_msgs[0])
        self.label_info_extract.setText(list_msgs[1])
