import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
import os
from pathlib import Path

from app.database.db_manager import DBManager
from app.ui.main_window import MainWindow
from app.core.settings.settings import Settings
import app.utils.constants as C
from app.core.logging.logger import get_logger

logger = get_logger(__name__)


def _set_up_env():
    node_path = Path(__file__).parent / "node"
    os.environ["PATH"] = str(node_path) + os.pathsep + os.environ.get("PATH", "")


def main():
    db = DBManager("data/downloads.db")
    logger.info("Iniciando YT Downloader")
    logger.info(f"[DB] Inicializada en: {db.db_path.resolve()}")
    _set_up_env()
    app = QApplication(sys.argv)

    scheme = C.THEME_SCHEME.get(Settings.get_theme(), Qt.ColorScheme.Unknown)
    app.styleHints().setColorScheme(scheme)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
