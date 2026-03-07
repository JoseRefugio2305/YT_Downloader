import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from PySide6.QtCore import Qt

from app.database.db_manager import DBManager
from app.ui.main_window import MainWindow

# class MainWindow(QMainWindow):
#      def __init__(self):
#           super().__init__()
#           self.setWindowTitle("YT Downloader"
#                               )
#           self.setMinimumSize(900,600)

#           label = QLabel("YT Downloader")
#           label.setAlignment(Qt.AlignCenter)
#           self.setCentralWidget(label)


def main():
     db=DBManager("data/downloads.db")
     print(f"[DB] Inicializada en: {db.db_path.resolve()}")

     app=QApplication(sys.argv)
     window=MainWindow()
     window.show()
     sys.exit(app.exec())

if __name__=="__main__":
     main()