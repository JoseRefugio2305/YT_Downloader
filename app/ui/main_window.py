from PySide6.QtWidgets import QMainWindow, QMessageBox
from PySide6.QtGui import QCloseEvent

from .resources.main_ui import UIMainWindow
from ..database.db_manager import DBManager
from ..core.playlist_manager import PlaylistManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = UIMainWindow()
        self.ui.setupUi(self)
        self._db = DBManager()
        self._manager = PlaylistManager(self._db)
        self._connect_signals()

    def _connect_signals(self):
        # self._manager.item_finished.connect(self._on_item_finished)
        self._manager.all_finished.connect(self._on_all_finished)

    def _on_all_finished(self):
        self.ui.lblInfo.setText("Descargas Finalizadas")

    def closeEvent(self, event: QCloseEvent):
        reply = QMessageBox.question(
            self,
            "Confirmar salida",
            "¿Estás seguro de que deseas salir? Se cancelaran las descargas activas.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self._manager.cancel_all()
            self._db.close()
            event.accept()  # Cierra la ventana
        else:
            event.ignore()  # Cancela el cierre
