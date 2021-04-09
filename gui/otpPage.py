
#!/usr/bin/env python

import os
import json

from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QFormLayout, QWidget, QButtonGroup, QPlainTextEdit, QLineEdit, QFileDialog)


class KeySizeMeta(QWidget):

    def __init__(self, title="", parent=None):
        super(KeySizeMeta, self).__init__(parent)

        mainLayout = QVBoxLayout()
        self.keyEdit = QLineEdit()
        self.sizeEdit = QLineEdit()
        self.metaEdit = QLineEdit()

        _HLayout1 = QHBoxLayout()
        _HLayout1.addWidget(QLabel(f"{title} Key"))
        _HLayout1.addWidget(self.keyEdit)

        _HLayout2 = QHBoxLayout()
        _HLayout2.addWidget(QLabel(f"{title} Size"))
        _HLayout2.addWidget(self.sizeEdit)
        _HLayout2.addWidget(QLabel(f"{title} Meta"))
        _HLayout2.addWidget(self.metaEdit)

        mainLayout.addLayout(_HLayout1)
        mainLayout.addLayout(_HLayout2)

        mainLayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(mainLayout)

class PovPage(QWidget):
    def __init__(self, val=0, parent=None):
        super(PovPage, self).__init__(parent)

        self.powerOnVal = val & 0xFFFF
        self.editPov = QLineEdit(hex(self.powerOnVal))

        # [0] PWRONSRC: Power on Setting Source Control
        _bit0_0 = QRadioButton("Power on setting values come from pin")
        _bit0_1 = QRadioButton("Power on setting values come from OTP")

        _GroupBit0 = QGroupBox("Power on Setting Source Control")
        LayoutBit0 = QHBoxLayout()
        LayoutBit0.addWidget(_bit0_0)
        LayoutBit0.addWidget(_bit0_1)
        _GroupBit0.setLayout(LayoutBit0)

        # [1] QSPI0CKF: QSPI0 Clock Frequency Selection
        _bit1_0 = QRadioButton("QSPI clock is 36 MHz")
        _bit1_1 = QRadioButton("QSPI clock is 60 MHz")

        _GroupBit1 = QGroupBox("QSPI0 Clock Frequency Selection")
        LayoutBit1 = QHBoxLayout()
        LayoutBit1.addWidget(_bit1_0)
        LayoutBit1.addWidget(_bit1_1)
        _GroupBit1.setLayout(LayoutBit1)

        # [2] WDT0EN: WDT0 Function Enable Bit
        _bit2 = QCheckBox("WDT0 Function Enable Bit")
        # _bit2.stateChanged.connect(lambda checked: self.setBit(2) if checked else self.clearBit(2))

        # [4] UR0MSGODIS: UART0 Message Output Disable Bit
        _bit4 = QCheckBox("UART0 Debug Message Output Disable Bit")

        # [5] SD0BKEN: SD0 Back Up Boot Enable Bit
        _bit5 = QCheckBox("SD0 Back Up Boot Enable Bit")

        # [6] TSIMGLDEN: TSI Image Load Control Bit
        _bit6 = QCheckBox("TSI Image Load Control Bit")

        # [7] TSISWDIS: TSI’s Serial Wire Interface Disable Bit
        _bit7 = QCheckBox("TSI’s Serial Wire Interface Disable Bit")

        LayoutOthers = QGridLayout()
        LayoutOthers.addWidget(_bit2, 0, 0)
        LayoutOthers.addWidget(_bit4, 0, 1)
        LayoutOthers.addWidget(_bit5, 1, 0)
        LayoutOthers.addWidget(_bit6, 1, 1)
        LayoutOthers.addWidget(_bit7, 2, 0)

        # [11:10] BTSRCSEL: Boot Source Selection
        _GroupBit10 = QGroupBox("Boot Source Selection")
        LayoutBit10 = QGridLayout()

        _bit10_00 = QRadioButton("Boot from SPI Flash")
        _bit10_01 = QRadioButton("Boot from SD/eMMC")
        _bit10_10 = QRadioButton("Boot from NAND Flash")
        _bit10_11 = QRadioButton("Boot from USB")
        LayoutBit10.addWidget(_bit10_00, 0, 0)
        LayoutBit10.addWidget(_bit10_01, 0, 1)
        LayoutBit10.addWidget(_bit10_10, 1, 0)
        LayoutBit10.addWidget(_bit10_11, 1, 1)
        _GroupBit10.setLayout(LayoutBit10)

        # [13:12] BTNANDPS: NAND Flash Page Size Selection
        _bit12_00 = QRadioButton("NAND Flash page size is 2kB")
        _bit12_01 = QRadioButton("NAND Flash page size is 4kB")
        _bit12_10 = QRadioButton("NAND Flash page size is 8kB")
        _bit12_11 = QRadioButton("Ignore")
        _GroupBit12 = QGroupBox("NAND Flash Page Size Selection")
        LayoutBit12 = QGridLayout()
        LayoutBit12.addWidget(_bit12_00, 0, 0)
        LayoutBit12.addWidget(_bit12_01, 0, 1)
        LayoutBit12.addWidget(_bit12_10, 1, 0)
        LayoutBit12.addWidget(_bit12_11, 1, 1)
        _GroupBit12.setLayout(LayoutBit12)

        # [15:14] BTOPTION: Boot Option
        _bit14_00 = QRadioButton("SPI-NAND Flash with 1-bit mode booting")
        _bit14_01 = QRadioButton("SPI-NAND Flash with 4-bit mode booting")
        _bit14_10 = QRadioButton("SPI-NOR Flash with 1-bit mode booting")
        _bit14_11 = QRadioButton("SPI-NOR Flash with 4-bit mode booting")
        _GroupBit14 = QGroupBox("Boot Option")
        LayoutBit14 = QGridLayout()
        LayoutBit14.addWidget(_bit14_00, 0, 0)
        LayoutBit14.addWidget(_bit14_01, 0, 1)
        LayoutBit14.addWidget(_bit14_10, 1, 0)
        LayoutBit14.addWidget(_bit14_11, 1, 1)
        _GroupBit14.setLayout(LayoutBit14)

        _GroupValue = QGroupBox("Power-on Value")
        LayoutValue = QHBoxLayout()
        LayoutValue.addWidget(QLabel("Bits[0:15]"))

        LayoutValue.addWidget(self.editPov)

        LayoutValue.addWidget(QLabel("Secure Boot Disable Password"))
        LayoutValue.addWidget(QLineEdit(""))
        _GroupValue.setLayout(LayoutValue)

        # signal
        _bit0_0.clicked.connect(lambda: self.updateBits(0, 0))
        _bit0_1.clicked.connect(lambda: self.updateBits(0, 1))
        _bit1_0.clicked.connect(lambda: self.updateBits(1, 0))
        _bit1_1.clicked.connect(lambda: self.updateBits(1, 1))
        _bit2.stateChanged.connect(lambda state: self.checkBit(state, 2))
        _bit4.stateChanged.connect(lambda state: self.checkBit(state, 4))
        _bit5.stateChanged.connect(lambda state: self.checkBit(state, 5))
        _bit6.stateChanged.connect(lambda state: self.checkBit(state, 6))
        _bit7.stateChanged.connect(lambda state: self.checkBit(state, 7))


        _bit10_00.clicked.connect(lambda: (
            _GroupBit14.setEnabled(True),
            _bit14_00.setText("SPI-NAND Flash with 1-bit mode booting"),
            _bit14_01.setText("SPI-NAND Flash with 4-bit mode booting"),
            _bit14_10.setText("SPI-NOR Flash with 1-bit mode booting"),
            _bit14_11.setText("SPI-NOR Flash with 4-bit mode booting"),
            self.updateBits(10, 0, 2)))

        _bit10_01.clicked.connect(lambda: (
            _GroupBit14.setEnabled(True),
            _bit14_00.setText("SD0/eMMC0 booting"),
            _bit14_01.setText("SD1/eMMC1 booting"),
            _bit14_10.setText("SD1/eMMC1 booting"),
            _bit14_11.setText("SD1/eMMC1 booting"),
            self.updateBits(10, 1, 2)))

        _bit10_10.clicked.connect(lambda: (
            _GroupBit14.setEnabled(True),
            _bit14_00.setText("No ECC"),
            _bit14_01.setText("ECC is BCH T12"),
            _bit14_10.setText("ECC is BCH T24"),
            _bit14_11.setText("Ignore"),
            self.updateBits(10, 2, 2)))

        _bit10_11.clicked.connect(lambda: (_GroupBit14.setEnabled(False), self.updateBits(10, 3, 2)))

        _bit12_00.clicked.connect(lambda: (self.updateBits(12, 0, 2)))
        _bit12_01.clicked.connect(lambda: (self.updateBits(12, 1, 2)))
        _bit12_10.clicked.connect(lambda: (self.updateBits(12, 2, 2)))
        _bit12_11.clicked.connect(lambda: (self.updateBits(12, 3, 2)))

        _bit14_00.clicked.connect(lambda: (self.updateBits(14, 0, 2)))
        _bit14_01.clicked.connect(lambda: (self.updateBits(14, 1, 2)))
        _bit14_10.clicked.connect(lambda: (self.updateBits(14, 2, 2)))
        _bit14_11.clicked.connect(lambda: (self.updateBits(14, 3, 2)))

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(_GroupBit0)
        mainLayout.addWidget(_GroupBit1)
        mainLayout.addLayout(LayoutOthers)
        mainLayout.addWidget(_GroupBit10)
        mainLayout.addWidget(_GroupBit12)
        mainLayout.addWidget(_GroupBit14)
        mainLayout.addStretch()
        mainLayout.addWidget(_GroupValue)

        self.setLayout(mainLayout)

    def checkBit(self, state, lsb):

        if state:
            val = 1
        else:
            val = 0

        self.updateBits(lsb, val, bits = 1)

    def updateBits(self, lsb, val, bits = 1):

        if bits > 2:
            print(f'do not support {bits} bits setting for OTP')
            return

        if bits == 1:
            _mask = 1
        elif bits == 2:
            _mask = 3

        self.powerOnVal &= ~(_mask << lsb)
        self.powerOnVal |= ((val &_mask) << lsb)
        self.editPov.setText(hex(self.powerOnVal))

class DpmPlmPage(QWidget):
    def __init__(self, dpmVal=0, plmVal = 0, parent=None):
        super(DpmPlmPage, self).__init__(parent)

        self.dpmVal = dpmVal
        self.plmVal = plmVal
        self.editDpm = QLineEdit(hex(self.dpmVal))
        self.editPlm = QLineEdit(hex(self.plmVal))

        descriptions = [
            "DPM A35 Secure Debug State DISABLE OTP Bit",
            "DPM A35 Secure Debug State LOCK OTP Bit",
            "DPM A35 Secure Non-invasive Debug State DISABLE OTP Bit",
            "DPM A35 Secure Non-invasive Debug State LOCK OTP Bit",
            "DPM A35 Non-secure Debug State DISABLE OTP Bit",
            "DPM A35 Non-secure Debug State LOCK OTP Bit",
            "DPM A35 Non-secure Non-invasive Debug State DISABLE OTP Bit",
            "DPM A35 Non-secure Non-invasive Debug State LOCK OTP Bit",
            "DPM M4 Debug State DISABLE OTP Bit",
            "DPM M4 Debug State LOCK OTP Bit",
            "DPM M4 Non-invasive Debug State DISABLE OTP Bit",
            "DPM M4 Non-invasive Debug State LOCK OTP Bit",
            "DPM External Debug State DISABLE OTP Bit",
            "DPM External Debug State LOCK OTP Bit",
            "DPM External Tracing Debug State DISABLE OTP Bit",
            "DPM External Tracing Debug State LOCK OTP Bit",
            "DPM GIC CFGSDISABLE Debug State DISABLE OTP Bit",
            "DPM GIC CFGSDISABLE Debug State LOCK OTP Bit"
        ]

        _dpmGroup = QGroupBox("DPM Setting")
        _dpmLayout = QVBoxLayout()
        _dpmGroup.setLayout(_dpmLayout)

        for i, desc in enumerate(descriptions):
            _btn = QCheckBox(desc)
            _btn.stateChanged.connect(lambda state, i=i: self.checkDpmBit(state, i))
            _dpmLayout.addWidget(_btn)

        _plmGroup = QGroupBox("PLM Setting")
        _plmLayout = QHBoxLayout()
        _plmGroup.setLayout(_plmLayout)

        for i, desc in enumerate(["OEM", "Deployed", "RMA", "PRMA"]):
            _btn = QRadioButton(desc)
            _btn.clicked.connect(lambda _, i=i: (self.setPlmStage(i)))
            _plmLayout.addWidget(_btn)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(_dpmGroup)
        mainLayout.addWidget(_plmGroup)
        mainLayout.addStretch()


        _valLayout = QHBoxLayout()

        _valLayout.addWidget(QLabel("DPM Value"))
        _valLayout.addWidget(self.editDpm)
        _valLayout.addWidget(QLabel("PLM Value"))
        _valLayout.addWidget(self.editPlm)
        mainLayout.addLayout(_valLayout)


        self.setLayout(mainLayout)

    def checkDpmBit(self, state, lsb):

        if state:
            val = 1
        else:
            val = 0

        _mask = 1

        self.dpmVal &= ~(_mask << lsb)
        self.dpmVal |= ((val &_mask) << lsb)
        self.editDpm.setText(hex(self.dpmVal))


    # def get_plm(plm) -> int:
    #     return {
    #         'oem': 0x1,
    #         'deploy': 0x3,
    #         'rma':  0x7,
    #         'prma': 0xF
    #     }.get(plm, 0)

    def setPlmStage(self, i):

        if i < 4:
            _plm = [0x1, 0x3, 0x7, 0xF]
            self.plmVal = _plm[i]
            self.editPlm.setText(hex(self.plmVal))

class MiscPage(QWidget):
    def __init__(self, parent=None):
        super(MiscPage, self).__init__(parent)

        self.mainLayout = QVBoxLayout()
        self.addMacAddress()
        self.addDplyPwd()
        self.addSecure()
        self.addNonSecure()
        self.mainLayout.addStretch()
        self.setLayout(self.mainLayout)

    def addMacAddress(self):

        _Group = QGroupBox("MAC address")
        _Layout = QHBoxLayout()
        _Group.setLayout(_Layout)

        self.mac0LineEdit = QLineEdit()
        self.mac1LineEdit = QLineEdit()

        self.mac0LineEdit.setInputMask('HH:HH:HH:HH:HH:HH;_')
        self.mac1LineEdit.setInputMask('HH:HH:HH:HH:HH:HH;_')


        _Layout.addWidget(QLabel("MAC0 address"))
        _Layout.addWidget(self.mac0LineEdit)
        _Layout.addWidget(QLabel("MAC1 address"))
        _Layout.addWidget(self.mac1LineEdit)
        self.mainLayout.addWidget(_Group)

    def addDplyPwd(self):

        _Group = QGroupBox("Deployed Password")
        _Layout = QHBoxLayout()
        _Group.setLayout(_Layout)

        self.dplypwdEdit = QLineEdit()
        _Layout.addWidget(self.dplypwdEdit)
        self.mainLayout.addWidget(_Group)


    def addSecure(self):

        _Group = QGroupBox("Secure Region")
        _Layout = QHBoxLayout()
        _Group.setLayout(_Layout)

        self.secureText = QPlainTextEdit()
        _Layout.addWidget(self.secureText)
        self.mainLayout.addWidget(_Group)

    def addNonSecure(self):

        _Group = QGroupBox("Non-secure Region")
        _Layout = QHBoxLayout()
        _Group.setLayout(_Layout)

        self.nonSecureText = QPlainTextEdit()
        _Layout.addWidget(self.nonSecureText)
        self.mainLayout.addWidget(_Group)


class KeyPage(QWidget):
    def __init__(self, parent=None):
        super(KeyPage, self).__init__(parent)

        self.mainLayout = QVBoxLayout()
        # self.tabMedia = QTabWidget()
        # self.mainLayout.addWidget(self.tabMedia)

        self.addHardwareUniqueKey()
        self.addKeyStorage()
        self.addAesKey()
        self.mainLayout.addStretch()

        self.setLayout(self.mainLayout)

    def addHardwareUniqueKey(self):

        _Group = QGroupBox("Hardware Unique Key")
        _Layout = QVBoxLayout()
        _Group.setLayout(_Layout)

        # _desc = r'“huk0”, “huk1”, and “huk2” are hardware unique keys that stores in OTP. The usage is application specified. The maximum length of these keys are 256 bits. And meta fields maps to the METADATA register used by Key Store. Please refer to the Key Store chapter of MA35D1 Technical Reference Manual for the description of each bit of this element.'
        # _Layout.addWidget(QLabel(_desc))

        self.huk0Option = KeySizeMeta("HUK0")
        self.huk1Option = KeySizeMeta("HUK1")
        self.huk2Option = KeySizeMeta("HUK2")
        _Layout.addWidget(self.huk0Option)
        _Layout.addWidget(self.huk1Option)
        _Layout.addWidget(self.huk2Option)
        self.mainLayout.addWidget(_Group)
        # self.tabMedia.addTab(_Group, "Hardware Unique Key")

    def addKeyStorage(self):

        _Group = QGroupBox("Key Storage")
        _Layout = QVBoxLayout()
        _Group.setLayout(_Layout)

        self.keyStorage3Option = KeySizeMeta("KEY3")
        self.keyStorage4Option = KeySizeMeta("KEY4")
        self.keyStorage5Option = KeySizeMeta("KEY5")
        _Layout.addWidget(self.keyStorage3Option)
        _Layout.addWidget(self.keyStorage4Option)
        _Layout.addWidget(self.keyStorage5Option)
        self.mainLayout.addWidget(_Group)
        # self.tabMedia.addTab(_Group, "Key Storage")


    def addAesKey(self):

        _Group = QGroupBox("IBR ECC public key (X, Y), and IBR AES key")
        _Layout = QVBoxLayout()
        _Group.setLayout(_Layout)

        self.publicxEdit = QLineEdit()
        self.publicyEdit = QLineEdit()
        self.aeskeyEdit = QLineEdit()
        _Layout.addWidget(self.publicxEdit)
        _Layout.addWidget(self.publicyEdit)
        _Layout.addWidget(self.aeskeyEdit)
        self.mainLayout.addWidget(_Group)
        # self.tabMedia.addTab(_Group, "IBR Key")

class OtpPage(QWidget):
    def __init__(self, val = 0, parent=None):
        super(OtpPage, self).__init__(parent)

        self.mainLayout = QVBoxLayout()
        self.tabMedia = QTabWidget()

        self.pov = val

        self.povPage = PovPage(val, self)
        self.dpm_plmPage = DpmPlmPage(0, 0, self)
        self.miscPage = MiscPage(self)
        self.keyPage = KeyPage(self)

        self.tabMedia.addTab(self.povPage, 'Power-On Setting')
        self.tabMedia.addTab(self.dpm_plmPage, 'DPM and PLM Setting')
        self.tabMedia.addTab(self.miscPage, 'MISC Setting')
        self.tabMedia.addTab(self.keyPage, 'KEY Setting')

        self.mainLayout.addWidget(self.tabMedia)
        self.addExportOption()

        self.setLayout(self.mainLayout)
        self.setWindowTitle("MA35D1 OTP Settings")

    def addExportOption(self):
        _Group = QGroupBox("Export OTP settings")
        _Layout = QVBoxLayout()
        _Group.setLayout(_Layout)

        self.exportPov = QCheckBox("Power-On")
        self.exportDpmPlm = QCheckBox("DPM and PLM")
        self.exportMAC0 = QCheckBox("MAC0 address")
        self.exportMAC1 = QCheckBox("MAC1 address")
        self.exportDplypwd = QCheckBox("Deployed Password")
        self.exportSecure = QCheckBox("Secure Region")
        self.exportNonSecure = QCheckBox("Non-secure Region")
        self.exportKey = QCheckBox("Hardware Unique Key, Key Storage and IBR Key")

        self.checkList = [
            self.exportPov, self.exportDpmPlm, self.exportKey,
            self.exportDpmPlm, self.exportMAC0, self.exportMAC1,
            self.exportDplypwd, self.exportSecure, self.exportNonSecure
        ]

        for widget in self.checkList:
            widget.clicked.connect(self.exportChecked)

        self.exportButton = QPushButton('Export')
        self.exportFileEdit = QLineEdit('')
        self.exportFileEdit.setEnabled(False)
        self.exportButton.clicked.connect(self.exportFile)
        self.exportButton.setEnabled(False)

        _H1Layout = QHBoxLayout()
        _H1Layout.addWidget(self.exportPov)
        _H1Layout.addWidget(self.exportDpmPlm)
        _H1Layout.addWidget(self.exportMAC0)
        _H1Layout.addWidget(self.exportMAC1)

        _H2Layout = QHBoxLayout()
        _H2Layout.addWidget(self.exportDplypwd)
        _H2Layout.addWidget(self.exportSecure)
        _H2Layout.addWidget(self.exportNonSecure)
        _H2Layout.addStretch()

        _H3Layout = QHBoxLayout()
        _H3Layout.addWidget(self.exportButton)
        _H3Layout.addWidget(self.exportFileEdit)

        _Layout.addLayout(_H1Layout)
        _Layout.addLayout(_H2Layout)
        _Layout.addWidget(self.exportKey)
        _Layout.addLayout(_H3Layout)
        self.mainLayout.addWidget(_Group)

    def exportChecked(self):

        for widget in self.checkList:
            if widget.isChecked():
                self.exportButton.setEnabled(True)
                return

        self.exportButton.setEnabled(False)


    def _exportPov(self):
        # print(f"export POV {self.exportPov.isChecked()}")
        if self.exportPov.isChecked():
            # print(f"POV = {self.povPage.powerOnVal}")

            _pov = self.povPage.powerOnVal

            boot_cfg = {}

            if _pov & (1 << 0):
                boot_cfg["posotp"] = "enable"

            if _pov & (1 << 1):
                boot_cfg["qspiclk"] = "60mhz"

            if _pov & (1 << 2):
                boot_cfg["wdt0en"] = "enable"

            if _pov & (1 << 4):
                boot_cfg["uart0en"] = "enable"

            if _pov & (1 << 5):
                boot_cfg["sd0bken"] = "enable"

            if _pov & (1 << 6):
                boot_cfg["tsiimg"] = "enable"

            if _pov & (1 << 7):
                boot_cfg["tsidbg"] = "enable"

            bootsrc = (_pov >> 10) & 3

            if _pov & (3 << 10):

                if bootsrc == 1:
                    boot_cfg["bootsrc"] = "sd"
                elif bootsrc == 2:
                    boot_cfg["bootsrc"] = "nand"
                elif bootsrc == 3:
                    boot_cfg["bootsrc"] = "usb"


            if _pov & (3 << 12):

                page = (_pov >> 12) & 3

                if page == 1:
                    boot_cfg["page"] = "4k"
                elif page == 2:
                    boot_cfg["page"] = "8k"
                elif page == 3:
                    boot_cfg["page"] = "ignore"

            if (bootsrc != 3) and (_pov >> 14) & 3:

                option = (_pov >> 14) & 3

                _option = {
                    "spinand4", "spinor1", "spinor4",
                    "sd1", "sd1", "sd1",
                    "t12", "t24", "ignore"
                }

                boot_cfg["option"] = _option[bootsrc * 3 + option - 1]


            self.otp_dict["boot_cfg"] = boot_cfg

    def _exportDpmPlm(self):

        if self.exportDpmPlm.isChecked():

            _dpmVal = self.dpm_plmPage.dpmVal
            _plmVal = self.dpm_plmPage.plmVal


            dpm_plm = {}

            if _dpmVal:

                dpm = {}

                if _dpmVal & 0x00000001:
                    dpm["a35sdsdis"] = "1"

                if _dpmVal & 0x00000002:
                    dpm["a35sdslock"] = "1"

                if _dpmVal & 0x00000004:
                    dpm["a35sndsdis"] = "1"

                if _dpmVal & 0x00000008:
                    dpm["a35sndslock"] = "1"

                if _dpmVal & 0x00000010:
                    dpm["a35nsdsdis"] = "1"

                if _dpmVal & 0x00000020:
                    dpm["a35nsdslock"] = "1"

                if _dpmVal & 0x00000040:
                    dpm["a35nsndsdis"] = "1"

                if _dpmVal & 0x00000080:
                    dpm["a35nsndslock"] = "1"

                if _dpmVal & 0x00000100:
                    dpm["m4dsdis"] = "1"

                if _dpmVal & 0x00000200:
                    dpm["m4dslock"] = "1"

                if _dpmVal & 0x00000400:
                    dpm["m4ndsdis"] = "1"

                if _dpmVal & 0x00000800:
                    dpm["m4ndslock"] = "1"

                if _dpmVal & 0x00001000:
                    dpm["extdis"] = "1"

                if _dpmVal & 0x00002000:
                    dpm["extlock"] = "1"

                if _dpmVal & 0x00004000:
                    dpm["exttdis"] = "1"

                if _dpmVal & 0x00008000:
                    dpm["exttlock"] = "1"

                if _dpmVal & 0x00010000:
                    dpm["giccfgsdis"] = "1"

                if _dpmVal & 0x00020000:
                    dpm["giccfgslock"] = "1"

                dpm_plm["dpm"] = dpm

            if _plmVal == 0x1:
                dpm_plm["plm"] = "oem"
            elif _plmVal == 0x3:
                dpm_plm["plm"] = "deploy"
            elif _plmVal == 0x7:
                dpm_plm["plm"] = "rma"
            elif _plmVal == 0xf:
                dpm_plm["plm"] = "prma"

            self.otp_dict["dpm_plm"] = dpm_plm

    def _exportMAC01(self):

        if self.exportMAC0.isChecked():
            text = self.miscPage.mac0LineEdit.text()
            addr = text.replace(':', '')
            self.otp_dict["mac0"] = addr

        if self.exportMAC1.isChecked():
            text = self.miscPage.mac1LineEdit.text()
            addr = text.replace(':', '')
            self.otp_dict["mac1"] = addr

    def _exportDplyPwd(self):

        if self.exportDplypwd.isChecked():
            text = self.miscPage.dplypwdEdit.text()
            self.otp_dict["dplypwd"] = text

    def _exportSecureNonSecure(self):

        if self.exportSecure.isChecked():
            text = self.miscPage.secureText.toPlainText()
            self.otp_dict["sec"] = text

        if self.exportNonSecure.isChecked():
            text = self.miscPage.nonSecureText.toPlainText()
            self.otp_dict["nonsec"] = text

    def _exportKey(self):
        if self.exportKey.isChecked():

                options = [
                    self.keyPage.huk0Option,
                    self.keyPage.huk1Option,
                    self.keyPage.huk2Option,
                    self.keyPage.keyStorage3Option,
                    self.keyPage.keyStorage4Option,
                    self.keyPage.keyStorage5Option,
                ]

                for i, opt in enumerate(options):
                    if i < 3:
                        key = f"huk{i}"
                    else:
                        key = f"key{i}"

                    _dict = {}

                    _dict["key"] = opt.keyEdit.text()
                    _dict["size"] = opt.sizeEdit.text()
                    _dict["meta"] = opt.metaEdit.text()

                    self.otp_dict[key] = _dict

                self.otp_dict["publicx"] = self.keyPage.publicxEdit.text()
                self.otp_dict["publicy"] = self.keyPage.publicyEdit.text()
                self.otp_dict["aeskey"] = self.keyPage.aeskeyEdit.text()

    def _exportJson(self):

        # filename = "otp_export.json"
        self.otp_dict = {}

        self._exportPov()
        self._exportDpmPlm()
        self._exportMAC01()
        self._exportDplyPwd()
        self._exportSecureNonSecure()
        self._exportKey()


        # print(self.otp_dict)


    def exportFile(self):
        fileName, _ = QFileDialog.getSaveFileName(self,
                                    "save file",
                                    os.getcwd(),
                                    "All Files (*)")

        if fileName != "":
            self.exportFileEdit.setText(fileName)

            self._exportJson()

            with open(fileName, "w") as write_file:
                # json.dump(self.otp_dict, write_file)
                json.dump(self.otp_dict, write_file, indent=4)

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    testPage = OtpPage()
    testPage.show()

    sys.exit(app.exec_())
