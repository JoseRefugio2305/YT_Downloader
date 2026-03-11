import sys
from PySide6.QtWidgets import QApplication

from app.database.db_manager import DBManager
from app.ui.main_window import MainWindow

def main():
     db=DBManager("data/downloads.db")
     print(f"[DB] Inicializada en: {db.db_path.resolve()}")

     app=QApplication(sys.argv)
     window=MainWindow()
     window.show()
     sys.exit(app.exec())

if __name__=="__main__":
     main()