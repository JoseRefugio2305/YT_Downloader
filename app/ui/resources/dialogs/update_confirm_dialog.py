from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QCursor
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout


class UpdateConfirmDialog(QDialog):
    def __init__(self, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirmar Actualización")
        self.setMinimumWidth(600)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.MSWindowsFixedSizeDialogHint
        )
        layout = QVBoxLayout()
        font1 = QFont()
        font1.setPointSize(13)
        font1.setBold(True)
        font1.setItalic(False)
        lbl_title = QLabel(message)
        lbl_title.setFont(font1)
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)

        btn_layout = QHBoxLayout()
        btn_apply = QPushButton("Aceptar")
        btn_apply.setFont(font1)
        btn_apply.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_apply.setStyleSheet(
            "background-color : #064E6F; color : white; padding:5px; border-radius:10px;"
        )
        btn_apply.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setFont(font1)
        btn_cancel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_cancel.setStyleSheet(
            "background-color : #525252; color : white; padding:5px; border-radius:10px;"
        )
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_apply)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
