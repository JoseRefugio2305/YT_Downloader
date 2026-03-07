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
    QMovie,
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
    QDialog,
)
from pathlib import Path


class LoadingDialog(QDialog):
    ASSETS_DIR = Path(__file__).parent.parent.parent.parent / "assets"

    def __init__(self, message: str, parent=None):
        super().__init__(parent)
        self.message = message
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowFlags(Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.layout_princ = QVBoxLayout()
        self.label_msg = QLabel(self.message)
        self.loading_gif = QMovie(str(self.ASSETS_DIR / "loading.gif"))
        self.label_gif = QLabel(self)
        self.label_gif.setAlignment(Qt.AlignCenter)
        self.label_gif.setMovie(self.loading_gif)
        if self.loading_gif.isValid():
            self.loading_gif.start()  # Iniciamos la animacion
        self.layout_princ.addWidget(self.label_msg)
        self.layout_princ.addWidget(self.label_gif)

        self.setLayout(self.layout_princ)
