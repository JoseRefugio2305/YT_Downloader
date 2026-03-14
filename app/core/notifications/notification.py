import sys
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QStyle
from PySide6.QtCore import QCoreApplication


def show_notification(titulo, mensaje):
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Crear el icono en la bandeja
    tray = QSystemTrayIcon()
    icon = app.windowIcon()
    print(icon)
    if icon.isNull():
        icon = app.style().standardIcon(QStyle.SP_ComputerIcon)
    tray.setIcon(icon)
    tray.show()

    # Mostrar la notificación
    tray.showMessage(titulo, mensaje, QSystemTrayIcon.Information, 2000)
