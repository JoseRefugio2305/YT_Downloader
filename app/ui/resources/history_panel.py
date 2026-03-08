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

from .download_queue import DownloadQueue
from ...database.db_manager import DBManager
from ...database.models import Download
from ...utils.text_helpers import get_status_color


class HistoryPanel(QObject):
    def __init__(self, table: QTableWidget, queue: DownloadQueue, db: DBManager):
        super().__init__()
        self._table = table
        self._queue = queue
        self._db = db
        self.COL_TITLE = 0
        self.COL_FORMAT = 1
        self.COL_STATUS = 2
        self.COL_DATE = 3
        self.COL_ROUTE = 4
        self.COL_ACTIONS = 5
        self._setup_table()
        self._load_history()

    def _setup_table(self):
        font = QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(False)
        self._table.setFont(font)
        self._table.setColumnCount(6)
        self._table.verticalHeader().setDefaultSectionSize(100)
        self._table.setHorizontalHeaderLabels(
            ["Título", "Formato", "Estado", "Fecha", "Ruta", "Acciones"]
        )

    def _add_action_buttons(self, row: int, download: Download):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel("No disponibles durante descarga")
        btn_retry = QPushButton()
        btn_retry.setText("Reintentar")
        btn_retry.setStyleSheet("background-color : #FC8A00; color : white;")
        btn_retry.clicked.connect(lambda: self._on_retry( download))
        btn_delete = QPushButton()
        btn_delete.setText("Eliminar")
        btn_delete.setStyleSheet("background-color : #E01616; color : white;")
        btn_delete.clicked.connect(lambda: self._on_delete_from_history(row, download))
        layout.addWidget(btn_retry)
        layout.addWidget(btn_delete)
        layout.addWidget(label)
        # Revisamos que mostrar en acciones segun el estado
        label.setVisible(download.status in ("pending", "downloading"))
        btn_delete.setVisible(download.status not in ("pending", "downloading"))
        btn_retry.setVisible(download.status not in ("pending", "downloading"))

        self._table.setCellWidget(row, self.COL_ACTIONS, widget)

    def _add_row(self, row: int, download: Download):
        # Agregamos una linea vacia
        self._table.insertRow(row)

        self._table.setItem(row, self.COL_TITLE, QTableWidgetItem(download.title))
        self._table.setItem(row, self.COL_FORMAT, QTableWidgetItem(download.format))
        self._table.setItem(row, self.COL_STATUS, QTableWidgetItem(download.status))
        self._table.setItem(
            row,
            self.COL_DATE,
            QTableWidgetItem(download.created_at.strftime("%d/%m/%Y %H:%M")),
        )
        self._table.setItem(
            row, self.COL_ROUTE, QTableWidgetItem(download.destination_path)
        )
        self._add_action_buttons(row, download)
        if download.playlist_id:
            color = QColor("#7CCFE6")  # tono distinto para items de playlist
        else:
            color = QColor("#E0B753")  # color normal para videos sueltos

        for col in range(self._table.columnCount()):
            item = self._table.item(row, col)
            if item:
                item.setBackground(color)
                if (
                    col == self.COL_STATUS
                ):  # Si es la columna del status, le damos tambien un color de texto dependiendo del estado
                    item.setForeground(
                        QColor(get_status_color(download.status.capitalize()))
                    )

    def _load_history(self):
        history = self._db.get_downloads()
        for doanload in history:
            row = self._table.rowCount()
            self._add_row(row, doanload)

    def _on_delete_from_history(self, row: int, doanload: Download):
        reply = QMessageBox.question(
            self._table,
            "Confirmar eliminación",
            f"¿Estás seguro de querer eliminar {doanload.title} del historial?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.No:
            return

        self._db.delete_download(doanload.id)
        self._table.removeRow(row)

    def _on_retry(self, download: Download):
        self._queue.add_item(download.id,download.title)
        self._queue._on_retry_requested(download.id)
        self.refresh()

    def refresh(self):
        self._table.setRowCount(0)
        self._load_history()
