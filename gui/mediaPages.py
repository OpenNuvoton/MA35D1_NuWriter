
from PyQt5 import QtWidgets, QtCore

from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThread

from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QFormLayout, QWidget, QButtonGroup)

import os

DEV_DDR_SRAM = 0
DEV_NAND = 1
DEV_SD_EMMC = 2
DEV_SPINOR = 3
DEV_SPINAND = 4
DEV_OTP = 6
DEV_USBH = 7
DEV_UNKNOWN = 0xFF

# Command options
OPT_NONE = 0
OPT_SCRUB = 1       # For erase, use with care
OPT_WITHBAD = 1     # For read
OPT_EXECUTE = 2     # For write
OPT_VERIFY = 3      # For write
OPT_UNPACK = 4      # For pack
OPT_RAW = 5         # For write
OPT_EJECT = 6      # For msc


class MediaPage(QWidget):

    signalImgProgram = pyqtSignal(int, str, str, int, bool)
    signalImgRead = pyqtSignal(int, str, str, str, int, bool)
    signalImgErase = pyqtSignal(int, str, str, int, bool)
    signalMscStorage = pyqtSignal(str, int)

    def __init__(self, media, parent=None):
        super(MediaPage, self).__init__(parent)

        self.parent = parent
        self._media = media


        self.mainLayout = QVBoxLayout()
        self.buttonLayout = QHBoxLayout()

        self.addWriteArgument()
        self.addReadArgument()

        if media != DEV_DDR_SRAM and media != DEV_SD_EMMC:
            self.addEraseArgument()

        if media == DEV_SD_EMMC:
            self.addStorageArgument()

        self.mainLayout.addStretch()
        buttonGroup = QGroupBox('')
        buttonGroup.setLayout(self.buttonLayout)
        self.mainLayout.addWidget(buttonGroup)

        self.setLayout(self.mainLayout)

        if parent != None:
            self.signalImgRead.connect(parent.doImgRead)
            self.signalImgProgram.connect(parent.doImgProgram)
            self.signalImgErase.connect(parent.doImgErase)
            self.signalMscStorage.connect(parent.doMsc)

    def onRadioToggled(self):

        if self.radioPack.isChecked():
            self.imgAddress.setEnabled(False)
        else:
            self.imgAddress.setEnabled(True)

    def addWriteArgument(self):

        writeGroup = QGroupBox("Write")
        writeLayout = QFormLayout()

        imgBrowseButton = QPushButton('Browse')
        imgBrowseButton.clicked.connect(self.pathBrowse)

        self.imgPathLine = QLineEdit('')

        imgFileLayout = QHBoxLayout()
        imgFileLayout.addWidget(self.imgPathLine)
        imgFileLayout.addWidget(imgBrowseButton)

        writeLayout.addRow(QLabel("Image file"), imgFileLayout)

        if self._media != DEV_DDR_SRAM:
            self.radioData = QRadioButton("Data")
            self.radioPack = QRadioButton("Pack")


            self.btngroup1 = QButtonGroup()
            self.btngroup1.addButton(self.radioData)
            self.btngroup1.addButton(self.radioPack)

            self.radioPack.toggled.connect(self.onRadioToggled)
            self.radioPack.toggled.connect(self.onRadioToggled)

            imgTypeLayout = QHBoxLayout()
            imgTypeLayout.addWidget(self.radioData)
            imgTypeLayout.addWidget(self.radioPack)
            imgTypeLayout.addStretch()

            writeLayout.addRow(QLabel("Image type"), imgTypeLayout)

        self.imgAddress = QLineEdit('')

        writeLayout.addRow(QLabel("Image addr."), self.imgAddress)

        # if option == OPT_RAW and media != DEV_NAND:
        #     raise ValueError(f"Do not support raw write on {str.upper(args.write[0])}")

        if self._media == DEV_NAND:
            self.normalWrite = QRadioButton('None')
            self.rawWrite = QRadioButton('Raw Write')
            self.verifyWrite = QRadioButton('Verify')
            _optLayout = QHBoxLayout()
            _optLayout.addWidget(self.normalWrite)
            _optLayout.addWidget(self.rawWrite)
            _optLayout.addWidget(self.verifyWrite)
            _optLayout.addStretch()
            writeLayout.addRow(QLabel("Option"), _optLayout)
        elif self._media == DEV_DDR_SRAM:
            self.optExecute = QCheckBox('Execute after download')
            writeLayout.addRow(QLabel("Option"), self.optExecute)
        else:
            self.verifyWrite = QCheckBox('Verify')
            writeLayout.addRow(QLabel("Option"), self.verifyWrite)

        writeGroup.setLayout(writeLayout)
        self.mainLayout.addWidget(writeGroup)

        # Write Button
        writeButton = QPushButton('Write')
        writeButton.clicked.connect(self.writeMedia)
        self.buttonLayout.addWidget(writeButton)

    def addReadArgument(self):
        group = QGroupBox("Read")
        layout = QFormLayout()

        _fileLayout = QHBoxLayout()
        self.fileSave = QLineEdit('')
        browseButton = QPushButton('Browse')
        browseButton.clicked.connect(self.saveFile)
        _fileLayout.addWidget(self.fileSave)
        _fileLayout.addWidget(browseButton)

        _rangeLayout = QHBoxLayout()
        self.readStart = QLineEdit('')
        self.readEnd = QLineEdit('')
        self.readAll = QCheckBox('ALL')
        self.readAll.setVisible(False)

        self.readAll.stateChanged.connect(lambda checked: (self.readStart.setEnabled(not checked), self.readEnd.setEnabled(not checked)))

        _rangeLayout.addWidget(self.readStart)
        _rangeLayout.addWidget(QLabel("-"))
        _rangeLayout.addWidget(self.readEnd)
        _rangeLayout.addWidget(self.readAll)

        layout.addRow(QLabel("Save file"), _fileLayout)
        layout.addRow(QLabel("Range"), _rangeLayout)

        if self._media in [DEV_NAND, DEV_SPINAND]:
            self.readWithBad = QCheckBox('With Bad')
            layout.addRow(QLabel("Option"), self.readWithBad)

        group.setLayout(layout)
        self.mainLayout.addWidget(group)

        # Read Button
        readButton = QPushButton('Read')
        readButton.clicked.connect(self.readMedia)
        self.buttonLayout.addWidget(readButton)

    def addEraseArgument(self):
        group = QGroupBox("Erase")
        layout = QFormLayout()

        _rangeLayout = QHBoxLayout()
        self.eraseStart = QLineEdit('')
        self.eraseEnd = QLineEdit('')
        self.eraseAll = QCheckBox('ALL')

        self.eraseAll.stateChanged.connect(lambda checked: (self.eraseStart.setEnabled(not checked), self.eraseEnd.setEnabled(not checked)))

        _rangeLayout.addWidget(self.eraseStart)
        _rangeLayout.addWidget(QLabel("-"))
        _rangeLayout.addWidget(self.eraseEnd)
        _rangeLayout.addWidget(self.eraseAll)

        layout.addRow(QLabel("Range    "), _rangeLayout)

        group.setLayout(layout)
        self.mainLayout.addWidget(group)

        # Erase Button
        eraseButton = QPushButton('Erase')
        eraseButton.clicked.connect(self.eraseMedia)
        self.buttonLayout.addWidget(eraseButton)

    def addStorageArgument(self):

        self.reservedSize = QLineEdit('')

        self.optEject = QCheckBox('Eject')

        _optLayout = QHBoxLayout()
        _optLayout.addWidget(self.optEject)
        _optLayout.addStretch()

        _storageGroup = QGroupBox("Storage")
        _storageLayout = QFormLayout()

        _storageLayout.addRow(QLabel("Reserved size"), self.reservedSize)
        _storageLayout.addRow(QLabel("Option"), _optLayout)

        # _reservedLayout = QHBoxLayout()
        _storageGroup.setLayout(_storageLayout)
        self.mainLayout.addWidget(_storageGroup)

        self.optEject.stateChanged.connect(lambda checked: (self.reservedSize.setEnabled(not checked)))

        # Storage Button
        storageButton = QPushButton('Storage')
        storageButton.clicked.connect(self.storageMSC)
        self.buttonLayout.addWidget(storageButton)

    def writeMedia(self):
        _file = self.imgPathLine.text()
        _address = self.imgAddress.text()
        _media = self._media

        try:
            _ispack = self.radioPack.isChecked()
        except:
            _ispack = False

        _option = OPT_NONE

        if _media == DEV_DDR_SRAM:
            if self.optExecute.isChecked():
                _option = 2 # OPT_EXECUTE
        else:
            if _media == DEV_NAND:
                if self.normalWrite.isChecked():
                    _option = OPT_NONE
                elif self.rawWrite.isChecked():
                    _option = OPT_RAW

            if self.verifyWrite.isChecked():
                _option = OPT_VERIFY

        self.signalImgProgram.emit(_media, _address , _file, _option, _ispack)

    def readMedia(self):
        _file = self.fileSave.text()
        _start = self.readStart.text()
        _end = self.readEnd.text()
        _media = self._media
        _isall = self.readAll.isChecked()

        _option = OPT_NONE

        if _media in [DEV_NAND, DEV_SPINAND] and self.readWithBad.isChecked():
            _option = OPT_WITHBAD

        self.signalImgRead.emit(_media, _start , _file, _end, _option, _isall)

    def eraseMedia(self):
        _start = self.eraseStart.text()
        _end = self.eraseEnd.text()
        _media = self._media
        _isall = self.eraseAll.isChecked()
        self.signalImgErase.emit(_media, _start , _end, 0, _isall)

    def storageMSC(self):
        mscSize = self.reservedSize.text()

        # OPT_EJECT
        if self.optEject.isChecked():
            option = 6
        else:
            option = 0

        self.signalMscStorage.emit(mscSize , option)


    def pathBrowse(self):
        filename = ""
        # Fix for crash in X on Ubuntu 14.04
        filename, _ = QtWidgets.QFileDialog.getOpenFileName()

        if filename != "":
            self.imgPathLine.setText(filename)

    def saveFile(self):
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self,
                                    "save file",
                                    os.getcwd(),
                                    "All Files (*)")

        if fileName != "":
            self.fileSave.setText(fileName)
            return
