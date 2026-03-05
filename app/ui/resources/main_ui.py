from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QHeaderView, QLabel,
    QLineEdit, QPushButton, QScrollArea, QSizePolicy,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)

class UIMainWindow(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(700, 650)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QSize(700, 650))
        Form.setMaximumSize(QSize(700, 650))
        self.verticalLayoutWidget = QWidget(Form)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(0, 0, 711, 671))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.mainTab = QTabWidget(self.verticalLayoutWidget)
        self.mainTab.setObjectName(u"mainTab")
        font = QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setItalic(False)
        self.mainTab.setFont(font)
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.inputLink = QLineEdit(self.tab_3)
        self.inputLink.setObjectName(u"inputLink")
        self.inputLink.setGeometry(QRect(120, 50, 451, 41))
        font1 = QFont()
        font1.setPointSize(10)
        font1.setBold(False)
        font1.setItalic(False)
        font1.setUnderline(True)
        self.inputLink.setFont(font1)
        self.btnPasteLink = QPushButton(self.tab_3)
        self.btnPasteLink.setObjectName(u"btnPasteLink")
        self.btnPasteLink.setGeometry(QRect(30, 50, 81, 41))
        font2 = QFont()
        font2.setPointSize(10)
        font2.setBold(True)
        font2.setItalic(False)
        self.btnPasteLink.setFont(font2)
        self.scrollDownloads = QScrollArea(self.tab_3)
        self.scrollDownloads.setObjectName(u"scrollDownloads")
        self.scrollDownloads.setGeometry(QRect(10, 220, 681, 391))
        self.scrollDownloads.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 677, 387))
        self.scrollDownloads.setWidget(self.scrollAreaWidgetContents)
        self.btnDownload = QPushButton(self.tab_3)
        self.btnDownload.setObjectName(u"btnDownload")
        self.btnDownload.setGeometry(QRect(240, 110, 201, 41))
        font3 = QFont()
        font3.setPointSize(13)
        font3.setBold(True)
        font3.setItalic(False)
        self.btnDownload.setFont(font3)
        self.lblInfo = QLabel(self.tab_3)
        self.lblInfo.setObjectName(u"lblInfo")
        self.lblInfo.setGeometry(QRect(10, 180, 681, 31))
        self.lblInfo.setFont(font2)
        self.label = QLabel(self.tab_3)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(30, 10, 621, 41))
        font4 = QFont()
        font4.setPointSize(20)
        font4.setBold(True)
        font4.setItalic(False)
        font4.setUnderline(True)
        self.label.setFont(font4)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.comboBox = QComboBox(self.tab_3)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")
        self.comboBox.setGeometry(QRect(580, 50, 111, 41))
        self.comboBox.setFont(font3)
        self.mainTab.addTab(self.tab_3, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.tableHistorial = QTableWidget(self.tab_4)
        self.tableHistorial.setObjectName(u"tableHistorial")
        self.tableHistorial.setGeometry(QRect(10, 10, 681, 601))
        self.mainTab.addTab(self.tab_4, "")

        self.verticalLayout.addWidget(self.mainTab)


        self.retranslateUi(Form)

        self.mainTab.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.btnPasteLink.setText(QCoreApplication.translate("Form", u"Pegar Link", None))
        self.btnDownload.setText(QCoreApplication.translate("Form", u"Descargar", None))
        self.lblInfo.setText("")
        self.label.setText(QCoreApplication.translate("Form", u"YT Downloader", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("Form", u"MP3", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("Form", u"MP4", None))

        self.mainTab.setTabText(self.mainTab.indexOf(self.tab_3), QCoreApplication.translate("Form", u"Descargas", None))
        self.mainTab.setTabText(self.mainTab.indexOf(self.tab_4), QCoreApplication.translate("Form", u"Historial", None))
    # retranslateUi

