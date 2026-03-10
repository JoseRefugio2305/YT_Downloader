from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QMovie
from PySide6.QtWidgets import QLabel, QVBoxLayout, QDialog
from pathlib import Path


class LoadingDialog(QDialog):
    ASSETS_DIR = Path(__file__).parent.parent.parent.parent / "assets"

    def __init__(self, message: str, parent=None):
        super().__init__(parent)
        self.message = message
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setWindowTitle("Cargando...")
        self.setModal(True)
        self.setFixedSize(450, 300)
        self.layout_princ = QVBoxLayout()
        font = QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setItalic(False)
        self.label_msg = QLabel(self.message)
        self.label_msg.setFont(font)
        self.label_msg.setAlignment(Qt.AlignCenter)
        self.loading_gif = QMovie(str(self.ASSETS_DIR / "loading.gif"))
        self.loading_gif.setScaledSize(QSize(200, 200))
        self.label_gif = QLabel(self)
        self.label_gif.setAlignment(Qt.AlignCenter)
        self.label_gif.setMovie(self.loading_gif)
        if self.loading_gif.isValid():
            self.loading_gif.start()  # Iniciamos la animacion
        self.layout_princ.addWidget(self.label_msg)
        self.layout_princ.addWidget(self.label_gif)

        self.setLayout(self.layout_princ)
