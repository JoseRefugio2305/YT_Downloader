from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QMessageBox,
    QComboBox,
    QLineEdit,
)

from ..download.download_queue import DownloadQueue
from ....database.db_manager import DBManager
from ....database.models import Download
from ....utils.text_helpers import get_status_color


class HistoryPanel(QObject):
    def __init__(
        self,
        table: QTableWidget,
        widgetBusHist: QWidget,
        queue: DownloadQueue,
        db: DBManager,
    ):
        super().__init__()
        self._table = table
        self._widget_bus_hist = widgetBusHist
        self._queue = queue
        self._db = db
        self.COL_TITLE = 0
        self.COL_FORMAT = 1
        self.COL_STATUS = 2
        self.COL_DATE = 3
        self.COL_ROUTE = 4
        self.COL_ACTIONS = 5
        self._set_up_search_widget()
        self._setup_table()
        self._load_history()

    def _set_up_search_widget(self):
        self._delete_all_btn = self._widget_bus_hist.findChild(
            QPushButton, "btnLimpiarH"
        )
        self._delete_all_btn.clicked.connect(self._on_delete_all_history)
        self._input_search = self._widget_bus_hist.findChild(
            QLineEdit, "inputSearchHist"
        )
        self._btn_search_hist = self._widget_bus_hist.findChild(
            QPushButton, "btnSearchHistorial"
        )
        self._btn_search_hist.clicked.connect(self._on_search_history)
        self._btn_clean_search = self._widget_bus_hist.findChild(
            QPushButton, "btnCleanSearch"
        )
        self._btn_clean_search.clicked.connect(self._on_clean_search)
        self._combo_status = self._widget_bus_hist.findChild(QComboBox, "comboStatus")
        # 'pending' | 'downloading' | 'completed' | 'failed' | 'cancelled'
        self._combo_status.addItem("Todos", None)
        self._combo_status.addItem("Completado", "completed")
        self._combo_status.addItem("Pendiente", "pending")
        self._combo_status.addItem("Descargando", "downloading")
        self._combo_status.addItem("Cancelada", "cancelled")
        self._combo_status.addItem("Fallo", "failed")

        self._combo_format = self._widget_bus_hist.findChild(
            QComboBox, "comboFormatHist"
        )
        # 'pending' | 'downloading' | 'completed' | 'failed' | 'cancelled'
        self._combo_format.addItem("Todos", None)
        self._combo_format.addItem("MP4", "mp4")
        self._combo_format.addItem("MP3", "mp3")

    def _setup_table(self):
        font = QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setItalic(False)
        self._table.setFont(font)
        self._table.setColumnCount(6)
        self._table.verticalHeader().setDefaultSectionSize(100)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.setHorizontalHeaderLabels(
            ["Título", "Formato", "Estado", "Fecha", "Ruta", "Acciones"]
        )

    def _add_action_buttons(self, row: int, download: Download):
        font = QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setItalic(False)
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel("No disponibles durante descarga")
        btn_retry = QPushButton()
        btn_retry.setText("Reintentar")
        btn_retry.setStyleSheet("background-color : #FC8A00; color : white;")
        btn_retry.setFont(font)
        btn_retry.clicked.connect(lambda: self._on_retry(download))
        btn_delete = QPushButton()
        btn_delete.setText("Eliminar")
        btn_delete.setStyleSheet("background-color : #E01616; color : white;")
        btn_delete.setFont(font)
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
            color = QColor("#A9ECFF")  # tono distinto para items de playlist
        else:
            color = QColor("#FFE5A3")  # color normal para videos sueltos
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(False)
        for col in range(self._table.columnCount()):
            item = self._table.item(row, col)
            if item:
                item.setTextAlignment(Qt.AlignCenter)
                # Si es la columna del status, le damos tambien un color de texto dependiendo del estado
                if col == self.COL_STATUS:
                    item.setForeground(QColor(get_status_color(download.status)))
                    item.setFont(font)
                else:
                    item.setForeground(QColor("#000000"))
                    item.setBackground(color)

    def _load_history(self, is_search: bool = False):
        if is_search:
            txt_search = self._input_search.text().strip().lower()
            status = self._combo_status.currentData()
            format = self._combo_format.currentData()
            history = self._db.get_downloads(
                status=status,
                txt_search=txt_search if txt_search != "" else None,
                format=format,
            )
        else:
            history = self._db.get_downloads()
        for download in history:
            row = self._table.rowCount()
            self._add_row(row, download)

    def _on_delete_from_history(self, row: int, download: Download):

        msgBox = QMessageBox(self._table)
        msgBox.setIcon(QMessageBox.Icon.Question)
        msgBox.setWindowTitle("Confirmar eliminación")
        msgBox.setText(
            f"¿Estás seguro de querer eliminar {download.title} del historial?"
        )
        msgBox.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        buttonY = msgBox.button(QMessageBox.StandardButton.Yes)
        buttonY.setText("Borrar")

        buttonN = msgBox.button(QMessageBox.StandardButton.No)
        buttonN.setText("Cancelar")

        ret = msgBox.exec()

        if msgBox.clickedButton() == buttonN:
            return

        self._db.delete_download(download.id)
        self._table.removeRow(row)

    def _on_delete_all_history(self):
        msgBox = QMessageBox(self._table)
        msgBox.setIcon(QMessageBox.Icon.Question)
        msgBox.setWindowTitle("Confirmar eliminación")
        msgBox.setText(
            "¿Estás seguro de querer eliminar todo el historial de descargas?"
        )
        msgBox.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        buttonY = msgBox.button(QMessageBox.StandardButton.Yes)
        buttonY.setText("Borrar")

        buttonN = msgBox.button(QMessageBox.StandardButton.No)
        buttonN.setText("Cancelar")

        ret = msgBox.exec()

        if msgBox.clickedButton() == buttonN:
            return

        self._db.delete_historial()
        self.refresh()

    def _on_retry(self, download: Download):
        self._queue.add_item(download.id, download.title)
        self._queue._on_retry_requested(download.id)
        self.refresh()

    def _on_search_history(self):
        self.refresh(True)

    def _on_clean_search(self):
        self._combo_status.setCurrentIndex(0)
        self._combo_format.setCurrentIndex(0)
        self._input_search.setText("")
        self.refresh()

    def refresh(self, is_search: bool = False):
        self._table.setRowCount(0)
        self._load_history(is_search=is_search)
