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
    QWidget,
)


class UIMainWindow(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(1000, 650)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QSize(1000, 650))
        Form.setMaximumSize(QSize(1000, 650))
        self.verticalLayoutWidget = QWidget(Form)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(0, 0, 1001, 671))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.mainTab = QTabWidget(self.verticalLayoutWidget)
        self.mainTab.setObjectName("mainTab")
        font = QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setItalic(False)
        self.mainTab.setFont(font)
        self.tab_3 = QWidget()
        self.tab_3.setObjectName("tab_3")
        self.inputLink = QLineEdit(self.tab_3)
        self.inputLink.setObjectName("inputLink")
        self.inputLink.setGeometry(QRect(410, 50, 451, 41))
        font1 = QFont()
        font1.setPointSize(10)
        font1.setBold(False)
        font1.setItalic(False)
        font1.setUnderline(True)
        self.inputLink.setFont(font1)
        self.btnPasteLink = QPushButton(self.tab_3)
        self.btnPasteLink.setObjectName("btnPasteLink")
        self.btnPasteLink.setGeometry(QRect(350, 50, 51, 41))
        font2 = QFont()
        font2.setPointSize(20)
        font2.setBold(True)
        font2.setItalic(False)
        self.btnPasteLink.setFont(font2)
        self.btnPasteLink.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btnPasteLink.setStyleSheet(
            "background-color: rgb(108, 9, 200);\n" "color: rgb(255, 255, 255);"
        )
        self.scrollDownloads = QScrollArea(self.tab_3)
        self.scrollDownloads.setObjectName("scrollDownloads")
        self.scrollDownloads.setGeometry(QRect(10, 220, 981, 391))
        self.scrollDownloads.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 977, 387))
        self.scrollDownloads.setWidget(self.scrollAreaWidgetContents)
        self.btnDownload = QPushButton(self.tab_3)
        self.btnDownload.setObjectName("btnDownload")
        self.btnDownload.setGeometry(QRect(530, 100, 201, 41))
        font3 = QFont()
        font3.setPointSize(13)
        font3.setBold(True)
        font3.setItalic(False)
        self.btnDownload.setFont(font3)
        self.btnDownload.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btnDownload.setStyleSheet(
            "background-color: rgb(108, 9, 200);\n" "color: rgb(255, 255, 255);"
        )
        self.lblInfo = QLabel(self.tab_3)
        self.lblInfo.setObjectName("lblInfo")
        self.lblInfo.setGeometry(QRect(10, 180, 681, 31))
        self.lblInfo.setFont(font)
        self.label = QLabel(self.tab_3)
        self.label.setObjectName("label")
        self.label.setGeometry(QRect(10, 10, 331, 111))
        font4 = QFont()
        font4.setPointSize(30)
        font4.setBold(True)
        font4.setItalic(False)
        font4.setUnderline(True)
        self.label.setFont(font4)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.comboBox = QComboBox(self.tab_3)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName("comboBox")
        self.comboBox.setGeometry(QRect(870, 50, 111, 41))
        self.comboBox.setFont(font3)
        self.comboBox.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.comboBox.setStyleSheet(
            "background-color: rgb(108, 9, 200);\n" "color: rgb(255, 255, 255);"
        )
        self.btn_settings = QPushButton(self.tab_3)
        self.btn_settings.setObjectName("btn_settings")
        self.btn_settings.setGeometry(QRect(930, 100, 51, 41))
        self.btn_settings.setFont(font2)
        self.btn_settings.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_settings.setStyleSheet(
            "background-color: rgb(108, 9, 200);\n" "color: rgb(255, 255, 255);"
        )
        self.mainTab.addTab(self.tab_3, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName("tab_4")
        self.tableHistorial = QTableWidget(self.tab_4)
        self.tableHistorial.setObjectName("tableHistorial")
        self.tableHistorial.setGeometry(QRect(10, 60, 978, 551))
        self.btnLimpiarH = QPushButton(self.tab_4)
        self.btnLimpiarH.setObjectName("btnLimpiarH")
        self.btnLimpiarH.setGeometry(QRect(820, 10, 161, 41))
        font5 = QFont()
        font5.setPointSize(12)
        font5.setBold(True)
        font5.setItalic(False)
        self.btnLimpiarH.setFont(font5)
        self.btnLimpiarH.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btnLimpiarH.setStyleSheet(
            "background-color: rgb(108, 9, 200);\n" "color: rgb(255, 255, 255);"
        )
        self.mainTab.addTab(self.tab_4, "")

        self.verticalLayout.addWidget(self.mainTab)

        self.retranslateUi(Form)

        self.mainTab.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "YT Downloader", None))
        self.btnPasteLink.setText(
            QCoreApplication.translate("Form", "\U0001f4cb", None)
        )
        self.btnDownload.setText(QCoreApplication.translate("Form", "Descargar", None))
        self.lblInfo.setText(
            QCoreApplication.translate("Form", "Lista de Descargas", None)
        )
        self.label.setText(QCoreApplication.translate("Form", "YT Downloader", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("Form", "MP3", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("Form", "MP4", None))

        self.btn_settings.setText(
            QCoreApplication.translate("Form", "\u2699\ufe0f", None)
        )
        self.mainTab.setTabText(
            self.mainTab.indexOf(self.tab_3),
            QCoreApplication.translate("Form", "Descargas", None),
        )
        self.btnLimpiarH.setText(
            QCoreApplication.translate("Form", "Limpiar Historial", None)
        )
        self.mainTab.setTabText(
            self.mainTab.indexOf(self.tab_4),
            QCoreApplication.translate("Form", "Historial", None),
        )

    # retranslateUi
