from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QCursor


class RenameDialog(QDialog):
    def __init__(self, original_title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Renombrar Archivo")
        self.setMinimumWidth(600)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.MSWindowsFixedSizeDialogHint
        )
        self.setStyleSheet("")
        self.setStyleSheet("QLineEdit { background-color: palette(base);}")

        self._result_title = original_title

        layout = QVBoxLayout()
        font1 = QFont()
        font1.setPointSize(13)
        font1.setBold(True)
        font1.setItalic(False)
        lbl_title = QLabel("Nombre del archivo:")
        lbl_title.setFont(font1)
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)
        self._input = QLineEdit(original_title)
        font1.setBold(False)
        self._input.setFont(font1)
        self._input.setStyleSheet("")
        layout.addWidget(self._input)

        font1.setBold(True)
        btn_layout = QHBoxLayout()
        btn_apply = QPushButton("Aceptar")
        btn_apply.setFont(font1)
        btn_apply.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_apply.setStyleSheet(
            "background-color : #064E6F; color : white; padding:5px; border-radius:10px;"
        )
        btn_apply.clicked.connect(self._on_accept)
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

    def _on_accept(self):
        text = self._input.text().strip()
        if text:
            self._result_title = text
        self.accept()

    def get_title(self) -> str:
        return self._result_title
