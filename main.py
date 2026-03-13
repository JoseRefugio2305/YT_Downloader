import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from app.database.db_manager import DBManager
from app.ui.main_window import MainWindow
from app.core.settings.settings import Settings
from app.utils.constants import THEME_SCHEME


def main():
    db = DBManager("data/downloads.db")
    print(f"[DB] Inicializada en: {db.db_path.resolve()}")

    app = QApplication(sys.argv)

    scheme = THEME_SCHEME.get(Settings.get_theme(), Qt.ColorScheme.Unknown)
    app.styleHints().setColorScheme(scheme)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
