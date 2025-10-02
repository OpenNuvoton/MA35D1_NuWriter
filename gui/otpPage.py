
#!/usr/bin/env python

from ecdsa import SigningKey, NIST256p 
from hashlib import sha256
from random import randrange

import json
import os

from PyQt5.QtCore import QDateTime, QPointF, QRegExp, Qt, QTimer
from PyQt5.QtGui import QColor, QIntValidator, QRegExpValidator, QValidator
from PyQt5.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QFileDialog, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout, QLabel, 
        QLineEdit, QMessageBox, QPlainTextEdit, QProgressBar, QPushButton, QRadioButton, QScrollBar, 
        QSizePolicy, QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)
        
# OPT block definitions
OPT_OTPBLK1 = 0x100
OPT_OTPBLK2 = 0x200
OPT_OTPBLK3 = 0x400
OPT_OTPBLK4 = 0x800
OPT_OTPBLK5 = 0x1000
OPT_OTPBLK6 = 0x2000
OPT_OTPBLK7 = 0x4000
OPT_OTPKEY = 0x8000

# for otp lock
OPT_OTPBLK1_LOCK = 0x10000000
OPT_OTPBLK3_LOCK = 0x20000000
OPT_OTPBLK4_LOCK = 0x40000000
OPT_OTPBLK5_LOCK = 0x80000000

# for key lock
OPT_OTPKEY0 = 0x10000
OPT_OTPKEY1 = 0x20000
OPT_OTPKEY2 = 0x40000
OPT_OTPKEY3 = 0x80000
OPT_OTPKEY4 = 0x100000
OPT_OTPKEY5 = 0x200000
OPT_OTPKEY6 = 0x400000
OPT_OTPKEY7 = 0x800000
OPT_OTPKEY8 = 0x1000000

OPT_OTPENC = 0x8000000

class KeySizeMeta(QWidget):

    def __init__(self, title="", parent=None):
        super(KeySizeMeta, self).__init__(parent)

        mainLayout = QVBoxLayout()
        self.keyEdit = QLineEdit()
        self.metaEdit = QComboBox(self)
        self.metaEdit.addItems(['','aes256-unreadable','aes256-cpu-readable','sha256-unreadable',
                                'sha256-cpu-readable','eccp256-unreadable','eccp256-cpu-readable'])
        self.genButton = QPushButton('Generate')

        _HLayout1 = QHBoxLayout()
        _HLayout1.addWidget(QLabel(f"{title} Key:   0x"))
        _HLayout1.addWidget(self.keyEdit)
        _HLayout1.addWidget(self.genButton)

        _HLayout2 = QHBoxLayout()
        _HLayout2.addWidget(QLabel(f"{title} Meta"))
        _HLayout2.addWidget(self.metaEdit)
        _HLayout2.addStretch()

        #self.meta_change()
        mainLayout.addLayout(_HLayout2)
        mainLayout.addLayout(_HLayout1) 
        
        self.keyEdit.textChanged.connect(self.keyEdit_changed)
        self.genButton.clicked.connect(self.gen_key)      

        mainLayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(mainLayout)
    
    def keyEdit_changed(self):
        reg_key64 = QRegExpValidator(QRegExp("[0-9A-Fa-f]{64}"))
        
        if reg_key64.validate(self.keyEdit.text(),0)[0] == QValidator.Acceptable:
            self.keyEdit.setStyleSheet("border: 2px solid limegreen")
        elif self.keyEdit.text()== "":
            self.keyEdit.setStyleSheet("border: 1px solid black")
        else:
            self.keyEdit.setStyleSheet("border: 2px solid red")
    
    def gen_key(self):
        key = ''.join(['%x' % randrange(16) for _ in range(0, 64)])
        self.keyEdit.setText(key)
        
class KeySizeMeta64(QWidget):

    def __init__(self, title="", parent=None):
        super(KeySizeMeta64, self).__init__(parent)

        mainLayout = QVBoxLayout()
        self.keyEdit = QLineEdit()
        self.genButton = QPushButton('Generate')

        _HLayout1 = QHBoxLayout()
        _HLayout1.addWidget(QLabel(f"{title} Key:   0x"))
        _HLayout1.addWidget(self.keyEdit)
        _HLayout1.addWidget(self.genButton)

        #self.meta_change()
        mainLayout.addLayout(_HLayout1) 
        
        self.keyEdit.textChanged.connect(self.keyEdit_changed)
        self.genButton.clicked.connect(self.gen_key)

        mainLayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(mainLayout)
    
    def keyEdit_changed(self):
        reg_key64 = QRegExpValidator(QRegExp("[0-9A-Fa-f]{64}"))
        
        if reg_key64.validate(self.keyEdit.text(),0)[0] == QValidator.Acceptable:
            self.keyEdit.setStyleSheet("border: 2px solid limegreen")
        elif self.keyEdit.text()== "":
            self.keyEdit.setStyleSheet("border: 1px solid black")
        else:
            self.keyEdit.setStyleSheet("border: 2px solid red")
    
    def gen_key(self):
        key = ''.join(['%x' % randrange(16) for _ in range(0, 64)])
        self.keyEdit.setText(key)
        
class KeySizeMeta32(QWidget):
    
    def __init__(self, title="", parent=None):
        super(KeySizeMeta32, self).__init__(parent)

        mainLayout = QVBoxLayout()
        self.keyEdit = QLineEdit()
        self.genButton = QPushButton('Generate')

        _HLayout1 = QHBoxLayout()
        _HLayout1.addWidget(QLabel(f"{title} Key:   0x"))
        _HLayout1.addWidget(self.keyEdit)
        _HLayout1.addWidget(self.genButton)   

        mainLayout.addLayout(_HLayout1)
       
        self.keyEdit.textChanged.connect(self.keyEdit_changed)
        self.genButton.clicked.connect(self.gen_key32)      

        mainLayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(mainLayout)
    
    def keyEdit_changed(self):
        reg_key32 = QRegExpValidator(QRegExp("[0-9A-Fa-f]{32}"))
        
        if reg_key32.validate(self.keyEdit.text(),0)[0] == QValidator.Acceptable:
            self.keyEdit.setStyleSheet("border: 2px solid limegreen")
        elif self.keyEdit.text()== "":
            self.keyEdit.setStyleSheet("border: 1px solid black")
        else:
            self.keyEdit.setStyleSheet("border: 2px solid red")
            
    def gen_key32(self):
        key = ''.join(['%x' % randrange(16) for _ in range(0, 32)])
        self.keyEdit.setText(key)
        
class KeySizeMeta16(QWidget):
    
    def __init__(self, title="", parent=None):
        super(KeySizeMeta16, self).__init__(parent)

        mainLayout = QVBoxLayout()
        self.keyEdit = QLineEdit()
        self.genButton = QPushButton('Generate')

        _HLayout1 = QHBoxLayout()
        _HLayout1.addWidget(QLabel(f"{title} Key:   0x"))
        _HLayout1.addWidget(self.keyEdit)
        _HLayout1.addWidget(self.genButton)   

        mainLayout.addLayout(_HLayout1)
       
        self.keyEdit.textChanged.connect(self.keyEdit_changed)
        self.genButton.clicked.connect(self.gen_key16)

        mainLayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(mainLayout)
    
    def keyEdit_changed(self):
        reg_key16 = QRegExpValidator(QRegExp("[0-9A-Fa-f]{16}"))
        
        if reg_key16.validate(self.keyEdit.text(),0)[0] == QValidator.Acceptable:
            self.keyEdit.setStyleSheet("border: 2px solid limegreen")
        elif self.keyEdit.text()== "":
            self.keyEdit.setStyleSheet("border: 1px solid black")
        else:
            self.keyEdit.setStyleSheet("border: 2px solid red")
            
    def gen_key16(self):
        key = ''.join(['%x' % randrange(16) for _ in range(0, 16)])
        self.keyEdit.setText(key)

class PovPage(QWidget):
    def __init__(self, val=0, parent=None):
        super(PovPage, self).__init__(parent)

        self.powerOnVal = val & 0xFFFF
        self.editPov = QLineEdit(hex(self.powerOnVal))

        # [0] PWRONSRC: Power on Setting Source Control
        self._bit0_0 = QRadioButton("Power on setting values come from pin")
        self._bit0_1 = QRadioButton("Power on setting values come from OTP")

        _GroupBit0 = QGroupBox("Power on Setting Source Control")
        LayoutBit0 = QHBoxLayout()
        LayoutBit0.addWidget(self._bit0_0)
        LayoutBit0.addWidget(self._bit0_1)
        _GroupBit0.setLayout(LayoutBit0)

        # [1] QSPI0CKF: QSPI0 Clock Frequency Selection
        self._bit1_0 = QRadioButton("QSPI clock is 30 MHz")
        self._bit1_1 = QRadioButton("QSPI clock is 50 MHz")

        _GroupBit1 = QGroupBox("QSPI0 Clock Frequency Selection")
        LayoutBit1 = QHBoxLayout()
        LayoutBit1.addWidget(self._bit1_0)
        LayoutBit1.addWidget(self._bit1_1)
        _GroupBit1.setLayout(LayoutBit1)

        # [2] WDT1EN: WDT0 Function Enable Bit
        self._bit2 = QCheckBox("WDT1 Function Enable Bit")
        # _bit2.stateChanged.connect(lambda checked: self.setBit(2) if checked else self.clearBit(2))

        # [4] UR0MSGODIS: UART0 Message Output Disable Bit
        self._bit4 = QCheckBox("UART0 Debug Message Output Disable Bit")

        # [5] SD0BKEN: SD0 Back Up Boot Enable Bit
        self._bit5 = QCheckBox("SD0 Back Up Boot Enable Bit")

        # [6] TSIMGLDEN: TSI Image Load Control Bit
        #self._bit6 = QCheckBox("TSI Image Load Control Bit")

        # [7] TSISWDIS: TSI’s Serial Wire Interface Disable Bit
        #self._bit7 = QCheckBox("TSI’s Serial Wire Interface Disable Bit")
        
        # [9] boot_iovol
        self._bit9_0 = QRadioButton("I/O Voltage is 3.3 V")
        self._bit9_1 = QRadioButton("I/O Voltage is 1.8 V")

        _GroupBit9 = QGroupBox("Boot Source Interface I/O Voltage ")
        LayoutBit9 = QHBoxLayout()
        LayoutBit9.addWidget(self._bit9_0)
        LayoutBit9.addWidget(self._bit9_1)
        _GroupBit9.setLayout(LayoutBit9)

        LayoutOthers = QGridLayout()
        LayoutOthers.addWidget(self._bit2, 0, 0)
        LayoutOthers.addWidget(self._bit4, 0, 1)
        LayoutOthers.addWidget(self._bit5, 1, 0)
        #LayoutOthers.addWidget(self._bit6, 1, 1)
        #LayoutOthers.addWidget(self._bit7, 2, 0)

        # [11:10] BTSRCSEL: Boot Source Selection
        _GroupBit10 = QGroupBox("Boot Source Selection")
        LayoutBit10 = QGridLayout()

        self._bit10_00 = QRadioButton("Boot from SPI Flash")
        self._bit10_01 = QRadioButton("Boot from SD/eMMC")
        self._bit10_10 = QRadioButton("Boot from NAND Flash")
        self._bit10_11 = QRadioButton("Boot from USB")
        LayoutBit10.addWidget(self._bit10_00, 0, 0)
        LayoutBit10.addWidget(self._bit10_01, 0, 1)
        LayoutBit10.addWidget(self._bit10_10, 1, 0)
        LayoutBit10.addWidget(self._bit10_11, 1, 1)
        _GroupBit10.setLayout(LayoutBit10)

        # [13:12] BTNANDPS: NAND Flash Page Size Selection
        self._bit12_00 = QRadioButton("Ignore")
        self._bit12_01 = QRadioButton("NAND Flash page size is 2kB")
        self._bit12_10 = QRadioButton("NAND Flash page size is 4kB")
        self._bit12_11 = QRadioButton("NAND Flash page size is 8kB")
        self._GroupBit12 = QGroupBox("NAND Flash Page Size Selection")
        LayoutBit12 = QGridLayout()
        LayoutBit12.addWidget(self._bit12_00, 0, 0)
        LayoutBit12.addWidget(self._bit12_01, 0, 1)
        LayoutBit12.addWidget(self._bit12_10, 1, 0)
        LayoutBit12.addWidget(self._bit12_11, 1, 1)
        self._GroupBit12.setLayout(LayoutBit12)

        # [15:14] BTOPTION: Boot Option
        self._bit14_00 = QRadioButton("SPI-NAND Flash with 1-bit mode booting")
        self._bit14_01 = QRadioButton("SPI-NAND Flash with 4-bit mode booting")
        self._bit14_10 = QRadioButton("SPI-NOR Flash with 1-bit mode booting")
        self._bit14_11 = QRadioButton("SPI-NOR Flash with 4-bit mode booting")
        self._GroupBit14 = QGroupBox("Boot Option")
        LayoutBit14 = QGridLayout()
        LayoutBit14.addWidget(self._bit14_00, 0, 0)
        LayoutBit14.addWidget(self._bit14_01, 0, 1)
        LayoutBit14.addWidget(self._bit14_10, 1, 0)
        LayoutBit14.addWidget(self._bit14_11, 1, 1)
        self._GroupBit14.setLayout(LayoutBit14)
        
        self._bits_0 = QRadioButton("Secure boot Enabled")
        self._bits_1 = QRadioButton("Secure boot Disabled")

        _GroupBits = QGroupBox("Secure boot Selection")
        LayoutBits = QHBoxLayout()
        LayoutBits.addWidget(self._bits_0)
        LayoutBits.addWidget(self._bits_1)
        _GroupBits.setLayout(LayoutBits)        

        _GroupValue = QGroupBox("Power-on Value")
        LayoutValue = QHBoxLayout()
        LayoutValue.addWidget(QLabel("Bits[0:15]"))

        LayoutValue.addWidget(self.editPov)
        LayoutValue.addStretch()
        self.read_lock_Pov = QCheckBox("Read Only Lock")
        LayoutValue.addWidget(self.read_lock_Pov)
        
        self.read_lock_Pov.toggled.connect(self.on_read_lock_toggled)
        
        '''
        LayoutValue.addWidget(QLabel("Secure Boot Disable Password"))
        LayoutValue.addWidget(QLineEdit(""))
        '''
        LayoutValue.addStretch()
        _GroupValue.setLayout(LayoutValue)
        
        _GroupBootDelay = QGroupBox("Boot Delay")
        LayoutBootDelay = QHBoxLayout()
        self._bootdelay = QSpinBox()
        self._bootdelay.setRange(0, 15)
        LayoutBootDelay.addWidget(QLabel("Boot Delay:           "))
        LayoutBootDelay.addWidget(self._bootdelay)
        LayoutBootDelay.addStretch()
        _GroupBootDelay.setLayout(LayoutBootDelay)
        
        # signal
        self._bit0_0.clicked.connect(lambda: ( 
            self.updateBits(0, 0),
            self.enable_pos(False)))
        self._bit0_1.clicked.connect(lambda: (
            self.updateBits(0, 1),
            self.enable_pos(True)))                
        self._bit1_0.clicked.connect(lambda: self.updateBits(1, 0))
        self._bit1_1.clicked.connect(lambda: self.updateBits(1, 1))
        self._bit2.stateChanged.connect(lambda state: self.checkBit(state, 2))
        self._bit4.stateChanged.connect(lambda state: self.checkBit(state, 4))
        self._bit5.stateChanged.connect(lambda state: self.checkBit(state, 5))
        #self._bit6.stateChanged.connect(lambda state: self.checkBit(state, 6))
        #self._bit7.stateChanged.connect(lambda state: self.checkBit(state, 7))
        self._bit9_0.clicked.connect(lambda: self.updateBits(9, 0))
        self._bit9_1.clicked.connect(lambda: self.updateBits(9, 1))

        self._bit10_00.clicked.connect(lambda: (
            self.change_boot_option(0),
            self.updateBits(10, 0, 2)))

        self._bit10_01.clicked.connect(lambda: (
            self.change_boot_option(1),
            self.updateBits(10, 1, 2)))

        self._bit10_10.clicked.connect(lambda: (
            self.change_boot_option(2),
            self.updateBits(10, 2, 2)))

        self._bit10_11.clicked.connect(lambda: (
            self.change_boot_option(3), 
            self.updateBits(10, 3, 2)))

        self._bit12_00.clicked.connect(lambda: (self.updateBits(12, 0, 2)))
        self._bit12_01.clicked.connect(lambda: (self.updateBits(12, 1, 2)))
        self._bit12_10.clicked.connect(lambda: (self.updateBits(12, 2, 2)))
        self._bit12_11.clicked.connect(lambda: (self.updateBits(12, 3, 2)))

        self._bit14_00.clicked.connect(lambda: (self.updateBits(14, 0, 2)))
        self._bit14_01.clicked.connect(lambda: (self.updateBits(14, 1, 2)))
        self._bit14_10.clicked.connect(lambda: (self.updateBits(14, 2, 2)))
        self._bit14_11.clicked.connect(lambda: (self.updateBits(14, 3, 2)))

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(_GroupBit0)
        mainLayout.addWidget(_GroupBit1)
        mainLayout.addLayout(LayoutOthers)
        mainLayout.addWidget(_GroupBit9)
        mainLayout.addWidget(_GroupBit10)
        mainLayout.addWidget(self._GroupBit12)
        mainLayout.addWidget(self._GroupBit14)
        mainLayout.addWidget(_GroupBits)
        mainLayout.addWidget(_GroupBootDelay)
        mainLayout.addWidget(_GroupValue)

        self.setLayout(mainLayout)

    def on_read_lock_toggled(self, checked: bool):
        if checked:                     
            QMessageBox.warning(
                self,                   
                "Warning",
                " Read Only Lock will be enabled. \n Locked regions cannot be written with new values."
            )

    def enable_pos(self, state):
        
        self._bit10_00.setEnabled(state)
        self._bit10_01.setEnabled(state)
        self._bit10_10.setEnabled(state)
        self._bit10_11.setEnabled(state)
        
        self._bit12_00.setEnabled(state)
        self._bit12_01.setEnabled(state)
        self._bit12_10.setEnabled(state)
        self._bit12_11.setEnabled(state)
        
        self._bit14_00.setEnabled(state)
        self._bit14_01.setEnabled(state)
        self._bit14_10.setEnabled(state)
        self._bit14_11.setEnabled(state)
        
        self._bits_0.setEnabled(state)
        self._bits_1.setEnabled(state)
       
    def checkBit(self, state, lsb):

        if state:
            val = 1
        else:
            val = 0

        self.updateBits(lsb, val, bits = 1)

    def updateBits(self, lsb, val, bits = 1):

        if bits > 2:
            #print(f'do not support {bits} bits setting for OTP')
            return

        if bits == 1:
            _mask = 1
        elif bits == 2:
            _mask = 3

        self.powerOnVal &= ~(_mask << lsb)
        self.powerOnVal |= ((val &_mask) << lsb)
        self.editPov.setText(hex(self.powerOnVal))
        
    def change_boot_option(self, val):
        if val == 0:
            self._GroupBit12.setEnabled(False)
            self._GroupBit14.setEnabled(True)
            self._bit14_10.setEnabled(True)
            self._bit14_11.setEnabled(True)
            self._bit14_00.setText("SPI-NAND Flash with 1-bit mode booting")
            self._bit14_01.setText("SPI-NAND Flash with 4-bit mode booting")
            self._bit14_10.setText("SPI-NOR Flash with 1-bit mode booting")
            self._bit14_11.setText("SPI-NOR Flash with 4-bit mode booting")
        elif val == 1:
            self._GroupBit12.setEnabled(False)
            self._GroupBit14.setEnabled(True)
            self._bit14_00.setText("SD0/eMMC0 booting")
            self._bit14_01.setText("SD1/eMMC1 booting")
            self._bit14_10.setText("---")
            self._bit14_11.setText("---")
            self._bit14_10.setEnabled(False)
            self._bit14_11.setEnabled(False)
        elif val == 2:
            self._GroupBit12.setEnabled(True)
            self._GroupBit14.setEnabled(True)
            self._bit14_10.setEnabled(True)
            self._bit14_11.setEnabled(True)
            self._bit14_00.setText("Ignore")
            self._bit14_01.setText("ECC is BCH T12")
            self._bit14_10.setText("ECC is BCH T24")
            self._bit14_11.setText("No ECC")
        elif val == 3:
            self._GroupBit12.setEnabled(False)
            self._GroupBit14.setEnabled(False)
            
        

class DpmPlmPage(QWidget):
    def __init__(self, dpmVal=0, plmVal = 0, parent=None):
        super(DpmPlmPage, self).__init__(parent)

        self.dpmVal = dpmVal
        self.plmVal = plmVal
        #self.editDpm = QLineEdit(hex(self.dpmVal))
        self.editPlm = QLineEdit(hex(self.plmVal))
        self.dpm_btn = []
        self.plm_btn = []
        '''
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
            self.dpm_btn.append(QCheckBox(desc))
            self.dpm_btn[i].stateChanged.connect(lambda state, i=i: self.checkDpmBit(state, i))
            _dpmLayout.addWidget(self.dpm_btn[i])
        '''
        _plmGroup = QGroupBox("PLM Setting")
        _plmLayout = QHBoxLayout()
        _plmGroup.setLayout(_plmLayout)

        for i, desc in enumerate(["OEM", "Deployed", "RMA"]):  #PRMA canceled
            self.plm_btn.append(QRadioButton(desc))
            self.plm_btn[i].clicked.connect(lambda _, i=i: (self.setPlmStage(i)))
            _plmLayout.addWidget(self.plm_btn[i])

        self.mainLayout = QVBoxLayout()
        #mainLayout.addWidget(_dpmGroup)
        self.mainLayout.addWidget(_plmGroup)
        self.addDplyPwd()
        self.mainLayout.addStretch()

        _valLayout = QHBoxLayout()

        #_valLayout.addWidget(QLabel("DPM Value"))
        #_valLayout.addWidget(self.editDpm)
        _valLayout.addWidget(QLabel("PLM Value"))
        _valLayout.addWidget(self.editPlm)
        self.mainLayout.addLayout(_valLayout)

        self.setLayout(self.mainLayout)
    '''
    def checkDpmBit(self, state, lsb):

        if state:
            val = 1
        else:
            val = 0

        _mask = 1

        self.dpmVal &= ~(_mask << lsb)
        self.dpmVal |= ((val &_mask) << lsb)
        self.editDpm.setText(hex(self.dpmVal))
    '''
    def addDplyPwd(self):

        _Group = QGroupBox("Deployed Password:  0x")
        _Layout = QHBoxLayout()
        _Group.setLayout(_Layout)

        self.dplypwdEdit = QLineEdit()
        _Layout.addWidget(self.dplypwdEdit)
        self.read_lock_Plm = QCheckBox("Read Only Lock")
        _Layout.addWidget(self.read_lock_Plm)
        self.mainLayout.addWidget(_Group)
        
        self.read_lock_Plm.toggled.connect(self.on_read_lock_toggled)
        self.dplypwdEdit.textChanged.connect(self.dplypwdEdit_changed)
        
    def on_read_lock_toggled(self, checked: bool):
        if checked:                     
            QMessageBox.warning(
                self,                   
                "Warning",
                " Read Only Lock will be enabled. \n Locked regions cannot be written with new values."
            )
        
    def dplypwdEdit_changed(self):
        reg_key8 = QRegExpValidator(QRegExp("[0-9A-Fa-f]{8}"))
        
        if reg_key8.validate(self.dplypwdEdit.text(),0)[0] == QValidator.Acceptable:
            self.dplypwdEdit.setStyleSheet("border: 2px solid limegreen")
        elif self.dplypwdEdit.text() == "":
            self.dplypwdEdit.setStyleSheet("border: 1px solid black")
        else:
            self.dplypwdEdit.setStyleSheet("border: 2px solid red")

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
        self.addSecure()
        self.addNonSecure()
        self.mainLayout.addStretch()
        self.setLayout(self.mainLayout)

    def addMacAddress(self):

        _Group = QGroupBox("MAC address")
        _Layout = QGridLayout()
        _Group.setLayout(_Layout)

        self.mac0LineEdit = QLineEdit()
        self.mac1LineEdit = QLineEdit()

        self.mac0LineEdit.setInputMask('HH:HH:HH:HH:HH:HH;_')
        self.mac1LineEdit.setInputMask('HH:HH:HH:HH:HH:HH;_')
        
        self.read_lock_mac0 = QCheckBox("MAC0 Read Only Lock")
        self.read_lock_mac1 = QCheckBox("MAC1 Read Only Lock")

        _Layout.addWidget(QLabel("MAC0 address"), 0, 0)
        _Layout.addWidget(self.mac0LineEdit, 0, 1)
        _Layout.addWidget(self.read_lock_mac0, 0, 2)
        
        _Layout.addWidget(QLabel("MAC1 address"), 1, 0)
        _Layout.addWidget(self.mac1LineEdit, 1, 1)
        _Layout.addWidget(self.read_lock_mac1, 1, 2)
        
        self.read_lock_mac0.toggled.connect(self.on_read_lock_toggled)
        self.read_lock_mac1.toggled.connect(self.on_read_lock_toggled)
        
        self.mainLayout.addWidget(_Group)

    def on_read_lock_toggled(self, checked: bool):
        if checked:                     
            QMessageBox.warning(
                self,                   
                "Warning",
                " Read Only Lock will be enabled. \n Locked regions cannot be written with new values."
            )
    
    def addSecure(self):

        _Group = QGroupBox("Secure Region(hex):  0x")
        _Layout = QHBoxLayout()
        _Group.setLayout(_Layout)

        self.secureText = QPlainTextEdit()
        _Layout.addWidget(self.secureText)
        self.mainLayout.addWidget(_Group)
        self.secureText.textChanged.connect(self.secureText_changed)

    def addNonSecure(self):

        _Group = QGroupBox("Non-secure Region(hex):  0x")
        _Layout = QHBoxLayout()
        _Group.setLayout(_Layout)

        self.nonSecureText = QPlainTextEdit()
        _Layout.addWidget(self.nonSecureText)
        self.mainLayout.addWidget(_Group)
        self.nonSecureText.textChanged.connect(self.nonSecureText_changed)
        
    def secureText_changed(self):
        reg_key176 = QRegExpValidator(QRegExp("[0-9A-Fa-f]{1,176}"))
        
        if reg_key176.validate(self.secureText.toPlainText(),0)[0] == QValidator.Acceptable:
            self.secureText.setStyleSheet("border: 2px solid limegreen")
        elif self.secureText.toPlainText() == "":
            self.secureText.setStyleSheet("border: 1px solid black")
        else:
            self.secureText.setStyleSheet("border: 2px solid red")
    
    def nonSecureText_changed(self):
        reg_key176 = QRegExpValidator(QRegExp("[0-9A-Fa-f]{1,176}"))
        
        if reg_key176.validate(self.nonSecureText.toPlainText(),0)[0] == QValidator.Acceptable:
            self.nonSecureText.setStyleSheet("border: 2px solid limegreen")
        elif self.nonSecureText.toPlainText()== "":
            self.nonSecureText.setStyleSheet("border: 1px solid black")
        else:
            self.nonSecureText.setStyleSheet("border: 2px solid red")


class KeyPage(QWidget):
    def __init__(self, parent=None):
        super(KeyPage, self).__init__(parent)

        self.mainLayout = QVBoxLayout()

        self.addHardwareUniqueKey()
        self.addKeyStorage()
        self.addAesKey()
        #self.mainLayout.addStretch()
        self.addOTPKey()
        self.setLayout(self.mainLayout)

    def addHardwareUniqueKey(self):

        _Group = QGroupBox("Hardware Unique Key")
        _Layout = QVBoxLayout()
        _Group.setLayout(_Layout)

        # _desc = r'“huk0”, “huk1”, and “huk2” are hardware unique keys that stores in OTP. The usage is application specified. The maximum length of these keys are 256 bits. And meta fields maps to the METADATA register used by Key Store. Please refer to the Key Store chapter of MA35D1 Technical Reference Manual for the description of each bit of this element.'

        self.huk0Option = KeySizeMeta32("HUK0")
        self.huk1Option = KeySizeMeta32("HUK1")
        self.huk2Option = KeySizeMeta32("HUK2")
        _Layout.addWidget(self.huk0Option)
        _Layout.addWidget(self.huk1Option)
        _Layout.addWidget(self.huk2Option)
        self.mainLayout.addWidget(_Group)

    def addKeyStorage(self):

        _Group = QGroupBox("Key Storage")
        _Layout = QVBoxLayout()
        _Group.setLayout(_Layout)

        self._34 = False
        self._45 = False

        self.keyStorage3Option = KeySizeMeta("KEY3")
        self.keyStorage4Option = KeySizeMeta("KEY4")
        self.keyStorage5Option = KeySizeMeta("KEY5")
        _Layout.addWidget(self.keyStorage3Option)
        _Layout.addWidget(self.keyStorage4Option)
        _Layout.addWidget(self.keyStorage5Option)
        
        self.keyStorage3Option.metaEdit.activated.connect(self.meta3_change)
        self.keyStorage4Option.metaEdit.activated.connect(self.meta4_change)
        self.keyStorage5Option.metaEdit.activated.connect(self.meta5_change)
        
        self.meta3_change()
        self.meta4_change()
        self.meta5_change()
        
        self.mainLayout.addWidget(_Group)
        
    def meta3_change(self):
    
        if self._45:
            if  (self.keyStorage3Option.metaEdit.currentText()=='eccp256-unreadable') or \
            (self.keyStorage3Option.metaEdit.currentText()=='eccp256-cpu-readable'):
                self.keyStorage3Option.metaEdit.setCurrentText('')                
        elif self._34:
            if  (self.keyStorage3Option.metaEdit.currentText()!='eccp256-unreadable') and \
            (self.keyStorage3Option.metaEdit.currentText()!='eccp256-cpu-readable'):
                self.keyStorage4Option.metaEdit.setCurrentText('')
                self.keyStorage4Option.keyEdit.setText('')
                self.keyStorage4Option.metaEdit.setEnabled(True)
                self.keyStorage4Option.genButton.setEnabled(False)
                self._34 = False
            else :
                self.keyStorage4Option.metaEdit.setCurrentText(self.keyStorage3Option.metaEdit.currentText())
                self.keyStorage4Option.genButton.setEnabled(False)
        else:
            if  (self.keyStorage3Option.metaEdit.currentText()=='eccp256-unreadable') or \
            (self.keyStorage3Option.metaEdit.currentText()=='eccp256-cpu-readable'):
                self.keyStorage4Option.metaEdit.setCurrentText(self.keyStorage3Option.metaEdit.currentText())
                self.keyStorage4Option.metaEdit.setEnabled(False)
                self.keyStorage4Option.genButton.setEnabled(False)
                self._34 = True
                
        self.keyStorage3Option.genButton.setEnabled(True)        
        if self.keyStorage3Option.metaEdit.currentText()=='':
            self.keyStorage3Option.keyEdit.setText('')
            self.keyStorage3Option.genButton.setEnabled(False)
        elif (self.keyStorage3Option.metaEdit.currentText()=='eccp256-unreadable') or \
            (self.keyStorage3Option.metaEdit.currentText()=='eccp256-cpu-readable'):
            self.keyStorage3Option.genButton.setEnabled(False)
            
    def meta4_change(self): 
    
        if self._45:
            if  (self.keyStorage4Option.metaEdit.currentText()!='eccp256-unreadable') and \
            (self.keyStorage4Option.metaEdit.currentText()!='eccp256-cpu-readable'):
                self.keyStorage5Option.metaEdit.setCurrentText('')
                self.keyStorage5Option.keyEdit.setText('')
                self.keyStorage5Option.metaEdit.setEnabled(True)
                self.keyStorage5Option.genButton.setEnabled(False)
                self._45 = False
            else :
                self.keyStorage4Option.metaEdit.setCurrentText(self.keyStorage3Option.metaEdit.currentText())
                self.keyStorage5Option.genButton.setEnabled(False)
        else:
            if  (self.keyStorage4Option.metaEdit.currentText()=='eccp256-unreadable') or \
            (self.keyStorage4Option.metaEdit.currentText()=='eccp256-cpu-readable'):
                self.keyStorage5Option.metaEdit.setCurrentText(self.keyStorage4Option.metaEdit.currentText())
                self.keyStorage5Option.metaEdit.setEnabled(False)
                self.keyStorage5Option.genButton.setEnabled(False)
                self._45 = True
                
        self.keyStorage4Option.genButton.setEnabled(True)        
        if self.keyStorage4Option.metaEdit.currentText()=='':
            self.keyStorage4Option.keyEdit.setText('')
            self.keyStorage4Option.genButton.setEnabled(False)
        elif (self.keyStorage4Option.metaEdit.currentText()=='eccp256-unreadable') or \
            (self.keyStorage4Option.metaEdit.currentText()=='eccp256-cpu-readable'):
            self.keyStorage4Option.genButton.setEnabled(False)
            
    def meta5_change(self):
    
        if  (self.keyStorage5Option.metaEdit.currentText()=='eccp256-unreadable') or \
        (self.keyStorage5Option.metaEdit.currentText()=='eccp256-cpu-readable'):
            self.keyStorage5Option.metaEdit.setCurrentText('')         
                
        self.keyStorage5Option.genButton.setEnabled(True)        
        if self.keyStorage5Option.metaEdit.currentText()=='':
            self.keyStorage5Option.keyEdit.setText('')
            self.keyStorage5Option.genButton.setEnabled(False)
        elif (self.keyStorage5Option.metaEdit.currentText()=='eccp256-unreadable') or \
            (self.keyStorage5Option.metaEdit.currentText()=='eccp256-cpu-readable'):
            self.keyStorage5Option.genButton.setEnabled(False)
            
    def addAesKey(self):

        reg_key64 = QRegExpValidator(QRegExp("[0-9A-Fa-f]{64}"))

        self.aes_Group = QGroupBox("IBR ECC public key (X, Y), and IBR AES key")
        _Layout = QFormLayout()
        self.aes_Group.setLayout(_Layout)

        self.privateEdit = QLineEdit()
        self.publicxEdit = QLineEdit()
        self.publicyEdit = QLineEdit()
        self.aeskeyEdit = QLineEdit()
        self.privateEdit_btn = QPushButton('Generate')
        self.aeskeyEdit_btn = QPushButton('Generate')
        self.privateEdit_sub = QHBoxLayout()
        self.publicxEdit_sub = QHBoxLayout()
        self.publicyEdit_sub = QHBoxLayout()
        self.aeskeyEdit_sub = QHBoxLayout()
        self.privateEdit_sub.addWidget(QLabel(f"Private Key:    0x"))
        self.privateEdit_sub.addWidget(self.privateEdit)
        self.privateEdit_sub.addWidget(self.privateEdit_btn)
        self.publicxEdit_sub.addWidget(QLabel(f"Public X KEY6:  0x"))
        self.publicxEdit_sub.addWidget(self.publicxEdit)
        self.publicyEdit_sub.addWidget(QLabel(f"Public Y KEY7:  0x"))
        self.publicyEdit_sub.addWidget(self.publicyEdit)
        self.aeskeyEdit_sub.addWidget(QLabel(f"AES KEY8:    0x"))
        self.aeskeyEdit_sub.addWidget(self.aeskeyEdit)
        self.aeskeyEdit_sub.addWidget(self.aeskeyEdit_btn)
        
        self.privateEdit.textChanged.connect(self.Edit_changed)
        self.publicxEdit.textChanged.connect(self.Edit_changed)
        self.publicyEdit.textChanged.connect(self.Edit_changed)
        self.aeskeyEdit.textChanged.connect(self.Edit_changed)
        
        #self.privateEdit_btn.clicked.connect(self.gen_key)
        self.privateEdit_btn.clicked.connect(lambda: (self.gen_key(self.privateEdit, self.publicxEdit, self.publicyEdit)))
        self.aeskeyEdit_btn.clicked.connect(self.gen_key_a) 
        
        _Layout.addRow(self.privateEdit_sub)
        _Layout.addRow(self.publicxEdit_sub)
        _Layout.addRow(self.publicyEdit_sub)
        _Layout.addRow(self.aeskeyEdit_sub)
        self.mainLayout.addWidget(self.aes_Group)
        
    def addOTPKey(self):
        reg_key64 = QRegExpValidator(QRegExp("[0-9A-Fa-f]{64}"))
        self.otpkey_Group = QGroupBox("OTP encrypt private key")
        _Layout = QVBoxLayout()
        self.otpkey_Group.setLayout(_Layout)
        self.otpOption = KeySizeMeta64("OTP")
        _Layout.addWidget(self.otpOption)
        self.mainLayout.addWidget(self.otpkey_Group)

    def gen_key(self, key_edit, x_edit, y_edit):
    #def gen_key(self):
        reg_key64 = QRegExpValidator(QRegExp("[0-9A-Fa-f]{64}"))
    
        #if reg_key64.validate(self.privateEdit.text(),0)[0] == QValidator.Acceptable:
        if reg_key64.validate(key_edit.text(),0)[0] == QValidator.Acceptable:
            #key = self.privateEdit.text()
            key = key_edit.text()
            #self.gen_key_pub(key)
            self.gen_key_pub(key, x_edit, y_edit)
        else :
            key = ''.join(['%x' % randrange(16) for _ in range(0, 64)])
            #self.privateEdit.setText(key) 
            key_edit.setText(key)
            #self.gen_key_pub(key)
            self.gen_key_pub(key, x_edit, y_edit)
        
    def gen_key_a(self):
        key = ''.join(['%x' % randrange(16) for _ in range(0, 64)])
        self.aeskeyEdit.setText(key)
        
    #def gen_key_pub(self, key):
    def gen_key_pub(self, key, x_edit, y_edit):
        sk = SigningKey.from_string(bytes.fromhex(key),
                                                curve=NIST256p,
                                                hashfunc=sha256)
        vk = sk.verifying_key
        key_x = hex(vk.pubkey.point.x()) 
        key_y = hex(vk.pubkey.point.y())   
        key_x = key_x.replace('0x', '')
        key_y = key_y.replace('0x', '')
        #self.publicxEdit.setText(key_x.zfill(64))
        x_edit.setText(key_x.zfill(64))
        #self.publicyEdit.setText(key_y.zfill(64))
        y_edit.setText(key_y.zfill(64))
        
    def Edit_changed(self):
        reg_key64 = QRegExpValidator(QRegExp("[0-9A-Fa-f]{64}"))
        stack = [self.privateEdit, self.publicxEdit, self.publicyEdit, self.aeskeyEdit]
        
        for i, target in enumerate(stack):
            if reg_key64.validate(target.text(),0)[0] == QValidator.Acceptable:
                target.setStyleSheet("border: 2px solid limegreen")
            elif target.text()== "":
                target.setStyleSheet("border: 1px solid black")
            else:
                target.setStyleSheet("border: 2px solid red") 
            
class OtpPage(QWidget):
    def __init__(self, val = 0, parent=None):
        super(OtpPage, self).__init__(parent)

        self.mainLayout = QVBoxLayout()
        self.tabMedia = QTabWidget()

        self.pov = val
        self.secure_dis = True

        self.povPage = PovPage(val, self)
        self.dpm_plmPage = DpmPlmPage(0, 0, self)
        self.miscPage = MiscPage(self)
        self.keyPage = KeyPage(self)

        self.tabMedia.addTab(self.povPage, 'Power-On Setting')
        self.tabMedia.addTab(self.dpm_plmPage, 'PLM Setting')
        self.tabMedia.addTab(self.miscPage, 'MISC Setting')
        self.tabMedia.addTab(self.keyPage, 'KEY Setting')

        self.mainLayout.addWidget(self.tabMedia)
        self.addExportOption()

        self.setLayout(self.mainLayout)
        self.setWindowTitle("MA35 Series OTP Settings")
        
    def bin_to_otp(self, d):
        option = int.from_bytes(d[604:608], byteorder='little')
        block_1 = int.from_bytes(d[0:4], byteorder='little')
        pos_pin = True
        if block_1 & 0x1 :
            self.povPage._bit0_1.setChecked(True) 
            self.povPage.updateBits(0, 1)
            #self.povPage.enable_pos(True)
            pos_pin = True
        else :
            self.povPage._bit0_0.setChecked(True) 
            self.povPage.updateBits(0, 0)
            #self.povPage.enable_pos(False)
            pos_pin = False
        if block_1 & 0x2 :
            self.povPage._bit1_1.setChecked(True) 
            self.povPage.updateBits(1, 1)
        else :
            self.povPage._bit1_0.setChecked(True) 
            self.povPage.updateBits(1, 0)
        if block_1 & 0x4 :
            self.povPage._bit2.setChecked(True)
            self.povPage.checkBit(self.povPage._bit2.isChecked(), 2)
        if block_1 & 0x10 :
            self.povPage._bit4.setChecked(True)
            self.povPage.checkBit(self.povPage._bit4.isChecked(), 4)
        if block_1 & 0x20 :
            self.povPage._bit5.setChecked(True)
            self.povPage.checkBit(self.povPage._bit5.isChecked(), 5)
        #if block_1 & 0x40 :
        #    self.povPage._bit6.setChecked(True)
        #    self.povPage.checkBit(self.povPage._bit6.isChecked(), 6)
        #if block_1 & 0x80 :
        #    self.povPage._bit7.setChecked(True)
        #    self.povPage.checkBit(self.povPage._bit7.isChecked(), 7)
        if block_1 & 0x200 :
            self.povPage._bit9_1.setChecked(True) 
            self.povPage.updateBits(9, 1)
        else :
            self.povPage._bit9_0.setChecked(True) 
            self.povPage.updateBits(9, 0)
        if block_1 & 0xC00 == 0xC00:
            self.povPage._bit10_11.setChecked(True)
            self.povPage.change_boot_option(3)
            self.povPage.updateBits(10, 3, 2)  
        elif block_1 & 0x800 :
            self.povPage._bit10_10.setChecked(True)
            self.povPage.change_boot_option(2)
            self.povPage.updateBits(10, 2, 2)
        elif block_1 & 0x400 :
            self.povPage._bit10_01.setChecked(True)
            self.povPage.change_boot_option(1)
            self.povPage.updateBits(10, 1, 2)
        else :
            self.povPage._bit10_00.setChecked(True)
            self.povPage.change_boot_option(0)
            self.povPage.updateBits(10, 0, 2)
        if block_1 & 0x3000 == 0x3000:
            self.povPage._bit12_11.setChecked(True)
            self.povPage.updateBits(12, 3, 2)
        elif block_1 & 0x2000 :
            self.povPage._bit12_10.setChecked(True)
            self.povPage.updateBits(12, 2, 2)
        elif block_1 & 0x1000 :
            self.povPage._bit12_01.setChecked(True)
            self.povPage.updateBits(12, 1, 2)
        else :
            self.povPage._bit12_00.setChecked(True)
            self.povPage.updateBits(12, 0, 2)
        if block_1 & 0xC000 == 0xC000:
            self.povPage._bit14_11.setChecked(True)
            self.povPage.updateBits(14, 3, 2)
        elif block_1 & 0x8000 :
            self.povPage._bit14_10.setChecked(True)
            self.povPage.updateBits(14, 2, 2)
        elif block_1 & 0x4000 :
            self.povPage._bit14_01.setChecked(True)
            self.povPage.updateBits(14, 1, 2)
        else :
            self.povPage._bit14_00.setChecked(True)
            self.povPage.updateBits(14, 0, 2)
        
        self.povPage._bootdelay.setValue((block_1 & 0xF0000) >> 16)
        
        if block_1 & 0x5A000000:
            self.povPage._bits_1.setChecked(True)
        else:
            self.povPage._bits_0.setChecked(True)
        
        if option & OPT_OTPBLK1_LOCK != 0:
            self.povPage.read_lock_Pov.blockSignals(True)
            self.povPage.read_lock_Pov.setChecked(True)
            self.povPage.read_lock_Pov.blockSignals(False)
        
        self.povPage.enable_pos(pos_pin)
        
        #dpm_plm hide right now 
        #block_2_d = int.from_bytes(d[4:8], byteorder='little')
        block_2_p = int.from_bytes(d[8:12], byteorder='little')
        
        #self.dpm_plmPage.setPlmStage(i)
        
        for i in range(0, 3):
            if block_2_p & (0x1 << i):
                self.dpm_plmPage.plm_btn[i].setChecked(True)
                self.dpm_plmPage.setPlmStage(i)
        
        block_3 = d[12:18].hex()
        if block_3 != '' and int(block_3,16) and (option & OPT_OTPBLK3 != 0):
            self.miscPage.mac0LineEdit.setText(block_3)
        if option & OPT_OTPBLK3_LOCK != 0:
            self.miscPage.read_lock_mac0.blockSignals(True)
            self.miscPage.read_lock_mac0.setChecked(True)
            self.miscPage.read_lock_mac0.blockSignals(False)

        block_4 = d[20:26].hex()
        if block_4 != '' and int(block_4,16) and (option & OPT_OTPBLK4 != 0):
            self.miscPage.mac1LineEdit.setText(block_4)
        if option & OPT_OTPBLK4_LOCK != 0:
            self.miscPage.read_lock_mac1.blockSignals(True)
            self.miscPage.read_lock_mac1.setChecked(True)
            self.miscPage.read_lock_mac1.blockSignals(False)

        block_5 = d[28:32].hex()
        if block_5 != '' and int(block_5,16) and (option & OPT_OTPBLK5 != 0):
            self.dpm_plmPage.dplypwdEdit.setText(block_5)
        if option & OPT_OTPBLK5_LOCK != 0:
            self.dpm_plmPage.read_lock_Plm.blockSignals(True)
            self.dpm_plmPage.read_lock_Plm.setChecked(True)
            self.dpm_plmPage.read_lock_Plm.blockSignals(False)

        block_6 = d[32:120].hex()
        if block_6 != '' and int(block_6,16) and (option & OPT_OTPBLK6 != 0):
            self.miscPage.secureText.setPlainText(block_6)

        block_7 = d[120:208].hex()
        if block_7 != '' and int(block_7,16) and (option & OPT_OTPBLK7 != 0):
            self.miscPage.nonSecureText.setPlainText(block_7)
        
        key_0 = d[208:224].hex()
        if key_0 != '' and int(key_0,16) and (option & OPT_OTPKEY0 != 0):
            self.keyPage.huk0Option.keyEdit.setText(key_0)
        key_1 = d[252:268].hex()
        if key_1 != '' and int(key_1,16) and (option & OPT_OTPKEY1 != 0):
            self.keyPage.huk1Option.keyEdit.setText(key_1)
        key_2 = d[296:312].hex()
        if key_2 != '' and int(key_2,16) and (option & OPT_OTPKEY2 != 0):
            self.keyPage.huk2Option.keyEdit.setText(key_2)
        key_3 = d[340:372].hex()
        if key_3 != '' and int(key_3,16) and (option & OPT_OTPKEY3 != 0):
            self.keyPage.keyStorage3Option.keyEdit.setText(key_3)
        key_4 = d[384:416].hex()
        if key_4 != '' and int(key_4,16) and (option & OPT_OTPKEY4 != 0):   
            self.keyPage.keyStorage4Option.keyEdit.setText(key_4)
        key_5 = d[428:460].hex()
        if key_5 != '' and int(key_5,16) and (option & OPT_OTPKEY5 != 0):
            self.keyPage.keyStorage5Option.keyEdit.setText(key_5)
    
    def read_back_otp(self, text):
        self.otp_file_names = text
        self._Group.setVisible(False)
        try:
            with open(self.otp_file_names, 'rb') as bin_file:
                d = bin_file.read()
        except (IOError, OSError) as err:
            print(f"Open {self.otp_file_names} failed") 
            return 1
       
        if len(d) < 672:
            d += b'\x00' * (672 - len(d))
            
        if int.from_bytes(d[0:4], byteorder='little') > 0xF:
            return 2
       
        self.bin_to_otp(d)
        
        style_sheet = "color: black; background-color: white"
        
        self.povPage._bit0_0.setEnabled(False)       
        self.povPage._bit0_1.setEnabled(False)
        self.povPage._bit0_0.setStyleSheet(style_sheet) 
        self.povPage._bit0_1.setStyleSheet(style_sheet)
        
        self.povPage._bit1_0.setEnabled(False)
        self.povPage._bit1_1.setEnabled(False)
        self.povPage._bit1_0.setStyleSheet(style_sheet) 
        self.povPage._bit1_1.setStyleSheet(style_sheet) 
        
        self.povPage._bit2.setEnabled(False)
        self.povPage._bit4.setEnabled(False)
        self.povPage._bit5.setEnabled(False)
        #self.povPage._bit6.setEnabled(False)
        #self.povPage._bit7.setEnabled(False)
        self.povPage._bit2.setStyleSheet(style_sheet)
        self.povPage._bit4.setStyleSheet(style_sheet)
        self.povPage._bit5.setStyleSheet(style_sheet)
        #self.povPage._bit6.setStyleSheet(style_sheet)
        #self.povPage._bit7.setStyleSheet(style_sheet)
        
        self.povPage._bit9_0.setEnabled(False)       
        self.povPage._bit9_1.setEnabled(False)
        self.povPage._bit9_0.setStyleSheet(style_sheet) 
        self.povPage._bit9_1.setStyleSheet(style_sheet)
        
        self.povPage._bit10_00.setEnabled(False)
        self.povPage._bit10_01.setEnabled(False)
        self.povPage._bit10_10.setEnabled(False)
        self.povPage._bit10_11.setEnabled(False)
        self.povPage._bit10_00.setStyleSheet(style_sheet)
        self.povPage._bit10_01.setStyleSheet(style_sheet)
        self.povPage._bit10_10.setStyleSheet(style_sheet)
        self.povPage._bit10_11.setStyleSheet(style_sheet)
        
        self.povPage._bit12_00.setEnabled(False)
        self.povPage._bit12_01.setEnabled(False)
        self.povPage._bit12_10.setEnabled(False)
        self.povPage._bit12_11.setEnabled(False)
        self.povPage._bit12_00.setStyleSheet(style_sheet)
        self.povPage._bit12_01.setStyleSheet(style_sheet)
        self.povPage._bit12_10.setStyleSheet(style_sheet)
        self.povPage._bit12_11.setStyleSheet(style_sheet)
        
        self.povPage._bit14_00.setEnabled(False)
        self.povPage._bit14_01.setEnabled(False)
        self.povPage._bit14_10.setEnabled(False)
        self.povPage._bit14_11.setEnabled(False)
        self.povPage._bit14_00.setStyleSheet(style_sheet)
        self.povPage._bit14_01.setStyleSheet(style_sheet)
        self.povPage._bit14_10.setStyleSheet(style_sheet)
        self.povPage._bit14_11.setStyleSheet(style_sheet)
        
        self.povPage._bits_0.setEnabled(False)
        self.povPage._bits_1.setEnabled(False)
        self.povPage._bits_0.setStyleSheet(style_sheet) 
        self.povPage._bits_1.setStyleSheet(style_sheet)
        
        self.miscPage.mac0LineEdit.setEnabled(False)
        self.miscPage.mac0LineEdit.setStyleSheet(style_sheet)
        self.miscPage.mac1LineEdit.setEnabled(False)
        self.miscPage.mac1LineEdit.setStyleSheet(style_sheet)
        self.dpm_plmPage.dplypwdEdit.setEnabled(False)
        self.dpm_plmPage.dplypwdEdit.setStyleSheet(style_sheet)
        self.miscPage.secureText.setEnabled(False)
        self.miscPage.secureText.setStyleSheet(style_sheet)
        self.miscPage.nonSecureText.setEnabled(False)
        self.miscPage.nonSecureText.setStyleSheet(style_sheet)
        
        self.keyPage.huk0Option.keyEdit.setEnabled(False)
        self.keyPage.huk0Option.keyEdit.setStyleSheet(style_sheet)
        self.keyPage.huk0Option.genButton.setVisible(False)
        self.keyPage.huk1Option.keyEdit.setEnabled(False)
        self.keyPage.huk1Option.keyEdit.setStyleSheet(style_sheet)
        self.keyPage.huk1Option.genButton.setVisible(False)      
        self.keyPage.huk2Option.keyEdit.setEnabled(False)
        self.keyPage.huk2Option.keyEdit.setStyleSheet(style_sheet)
        self.keyPage.huk2Option.genButton.setVisible(False)        
        self.keyPage.keyStorage3Option.keyEdit.setEnabled(False)
        self.keyPage.keyStorage3Option.metaEdit.setEnabled(False)
        self.keyPage.keyStorage3Option.keyEdit.setStyleSheet(style_sheet)
        self.keyPage.keyStorage3Option.metaEdit.setStyleSheet(style_sheet)
        self.keyPage.keyStorage3Option.genButton.setVisible(False)        
        self.keyPage.keyStorage4Option.keyEdit.setEnabled(False)
        self.keyPage.keyStorage4Option.metaEdit.setEnabled(False)
        self.keyPage.keyStorage4Option.keyEdit.setStyleSheet(style_sheet)
        self.keyPage.keyStorage4Option.metaEdit.setStyleSheet(style_sheet)
        self.keyPage.keyStorage4Option.genButton.setVisible(False)        
        self.keyPage.keyStorage5Option.keyEdit.setEnabled(False)
        self.keyPage.keyStorage5Option.metaEdit.setEnabled(False)
        self.keyPage.keyStorage5Option.keyEdit.setStyleSheet(style_sheet)
        self.keyPage.keyStorage5Option.metaEdit.setStyleSheet(style_sheet)
        self.keyPage.keyStorage5Option.genButton.setVisible(False)
        self.keyPage.aes_Group.setVisible(False)
        self.keyPage.otpkey_Group.setVisible(False)
        
        return 0
        '''
        self.keyPage.privateEdit.setEnabled(False)
        self.keyPage.privateEdit.setStyleSheet(style_sheet)
        self.keyPage.privateEdit_btn.setVisible(False)
        self.keyPage.publicxEdit.setEnabled(False)
        self.keyPage.publicyEdit.setEnabled(False)
        self.keyPage.aeskeyEdit.setEnabled(False)
        self.keyPage.publicxEdit.setStyleSheet(style_sheet)
        self.keyPage.publicyEdit.setStyleSheet(style_sheet)
        self.keyPage.aeskeyEdit.setStyleSheet(style_sheet)
        self.keyPage.aeskeyEdit_btn.setVisible(False)
        '''

    def set_otp_name(self, text):
        self.otp_file_names = text
        try:
            with open(self.otp_file_names, "rb") as f:
                raw_data = f.read()
        except (IOError, OSError) as err:
            print(f"Open {self.otp_file_names} failed")
            return
            
        is_utf8 = True
        try:
            text = raw_data.decode('utf-8')
        except UnicodeDecodeError:
            is_utf8 = False

        if is_utf8 == False:
            #print(f"{self.otp_file_names} is Binary")
            d = bytearray(raw_data)
            self.bin_to_otp(d)
            return
        else:
            try:
                d = json.loads(text)
                #print(f"{self.otp_file_names} is JSON")
            except json.JSONDecodeError:
                #print(f"{self.otp_file_names} is UTF-8 text")
                return
        '''
        try:
            with open(self.otp_file_names, 'r') as json_file:
                try:
                    d = json.load(json_file)
                except json.decoder.JSONDecodeError as err:
                    print(f"{self.otp_file_names} parsing error")
                    return
        except (IOError, OSError) as err:
            print(f"Open {self.otp_file_names} failed")
            return
        '''
                      
        for key in d.keys():
            #PovPage fill 
            if key == 'boot_cfg':
                pos_pin = True
                if d['boot_cfg'].get('posotp') == "enable":
                    self.povPage._bit0_1.setChecked(True) 
                    self.povPage.updateBits(0, 1)
                    pos_pin = True
                elif d['boot_cfg'].get('posotp') == "disable":
                    self.povPage._bit0_0.setChecked(True) 
                    self.povPage.updateBits(0, 0)
                    pos_pin = False
                if d['boot_cfg'].get('qspiclk') == "50mhz":
                    self.povPage._bit1_1.setChecked(True) 
                    self.povPage.updateBits(1, 1)
                elif d['boot_cfg'].get('qspiclk') == "30mhz":
                    self.povPage._bit1_0.setChecked(True) 
                    self.povPage.updateBits(1, 0)
                if d['boot_cfg'].get('wdt1en') == "enable":
                    self.povPage._bit2.setChecked(True)
                    self.povPage.checkBit(self.povPage._bit2.isChecked(), 2)
                if d['boot_cfg'].get('uart0en') == "disable":
                    self.povPage._bit4.setChecked(True)
                    self.povPage.checkBit(self.povPage._bit4.isChecked(), 4)
                elif d['boot_cfg'].get('uart0en') == "enable":
                    self.povPage._bit4.setChecked(False)
                    self.povPage.checkBit(self.povPage._bit4.isChecked(), 4)
                if d['boot_cfg'].get('sd0bken') == "enable":
                    self.povPage._bit5.setChecked(True)
                    self.povPage.checkBit(self.povPage._bit5.isChecked(), 5)
                #if d['boot_cfg'].get('tsiimg') == "enable":
                #    self.povPage._bit6.setChecked(True)
                #    self.povPage.checkBit(self.povPage._bit6.isChecked(), 6)
                #if d['boot_cfg'].get('tsidbg') == "disable":
                #    self.povPage._bit7.setChecked(True)
                #    self.povPage.checkBit(self.povPage._bit7.isChecked(), 7)
                #elif d['boot_cfg'].get('tsidbg') == "enable":
                #    self.povPage._bit7.setChecked(False)
                #    self.povPage.checkBit(self.povPage._bit7.isChecked(), 7)
                if d['boot_cfg'].get('boot_iovol') == "1_8v":
                    self.povPage._bit9_1.setChecked(True) 
                    self.povPage.updateBits(9, 1)
                elif d['boot_cfg'].get('boot_iovol') == "3_3v":
                    self.povPage._bit9_0.setChecked(True) 
                    self.povPage.updateBits(9, 0)
                    
                if d['boot_cfg'].get('bootsrc') == "spi":
                    self.povPage._bit10_00.setChecked(True)
                    self.povPage.change_boot_option(0)
                    self.povPage.updateBits(10, 0, 2)
                    
                    if d['boot_cfg'].get('option') == "spinand1":
                        self.povPage._bit14_00.setChecked(True)
                        self.povPage.updateBits(14, 0, 2)
                    elif d['boot_cfg'].get('option') == "spinand4":
                        self.povPage._bit14_01.setChecked(True)
                        self.povPage.updateBits(14, 1, 2)
                    elif d['boot_cfg'].get('option') == "spinor1":
                        self.povPage._bit14_10.setChecked(True)
                        self.povPage.updateBits(14, 2, 2)
                    elif d['boot_cfg'].get('option') == "spinor4":
                        self.povPage._bit14_11.setChecked(True)
                        self.povPage.updateBits(14, 3, 2)
                        
                elif d['boot_cfg'].get('bootsrc') == "sd":
                    self.povPage._bit10_01.setChecked(True)
                    self.povPage.change_boot_option(1)
                    self.povPage.updateBits(10, 1, 2)
                    
                    if d['boot_cfg'].get('option') == "sd0":
                        self.povPage._bit14_00.setChecked(True)
                        self.povPage.updateBits(14, 0, 2)
                    elif d['boot_cfg'].get('option') == "sd1":
                        self.povPage._bit14_01.setChecked(True)
                        self.povPage.updateBits(14, 1, 2) 
                    
                elif d['boot_cfg'].get('bootsrc') == "nand":
                    self.povPage._bit10_10.setChecked(True)
                    self.povPage.change_boot_option(2)
                    self.povPage.updateBits(10, 2, 2)
                    
                    if d['boot_cfg'].get('option') == "ignore":
                        self.povPage._bit14_00.setChecked(True)
                        self.povPage.updateBits(14, 0, 2)
                    elif d['boot_cfg'].get('option')== "t12":
                        self.povPage._bit14_01.setChecked(True)
                        self.povPage.updateBits(14, 1, 2)
                    elif d['boot_cfg'].get('option') == "t24":
                        self.povPage._bit14_10.setChecked(True)
                        self.povPage.updateBits(14, 2, 2)
                    elif d['boot_cfg'].get('option') == "noecc":
                        self.povPage._bit14_11.setChecked(True)
                        self.povPage.updateBits(14, 3, 2)
                    
                elif d['boot_cfg'].get('bootsrc') == "usb":
                    self.povPage._bit10_11.setChecked(True)
                    self.povPage.change_boot_option(3)
                    self.povPage.updateBits(10, 3, 2) 
                    
                if d['boot_cfg'].get('page') == "2k":
                    self.povPage._bit12_01.setChecked(True)
                    self.povPage.updateBits(12, 1, 2)
                elif d['boot_cfg'].get('page')  == "4k":
                    self.povPage._bit12_10.setChecked(True)
                    self.povPage.updateBits(12, 2, 2)
                elif d['boot_cfg'].get('page')  == "8k":
                    self.povPage._bit12_11.setChecked(True)
                    self.povPage.updateBits(12, 3, 2)
                
                if d['boot_cfg'].get('secboot') == "disable":
                    self.povPage._bits_1.setChecked(True)
                    
                if d['boot_cfg'].get('bootdly'):
                    #self.povPage._bits_1.setChecked(True)
                    self.povPage._bootdelay.setValue(int(d['boot_cfg']['bootdly']))
                    
                if d['boot_cfg'].get('lock') == 'enable':
                    self.povPage.read_lock_Pov.setChecked(True)
                    
                self.povPage.enable_pos(pos_pin)
           
            #dpm_plm fill (hide right now) 
                    
            elif key == 'dpm_plm':
                '''
                dpm_order = ["a35sdsdis", "a35sdslock", "a35sndsdis", "a35sndslock", "a35nsdsdis",
                             "a35nsdslock", "a35nsndsdis", "a35nsndslock", "m4dsdis", "m4dslock",
                             "m4ndsdis", "m4ndslock", "extdis", "extlock", "exttdis", "exttlock",
                             "giccfgsdis", "giccfgslock"]
                for i, sub_key in enumerate(dpm_order):
                    if d['dpm_plm'].get('dpm').get(sub_key) == "1":
                        self.dpm_plmPage.dpm_btn[i].setChecked(True)
                        self.dpm_plmPage.checkDpmBit(self.dpm_plmPage.dpm_btn[i].isChecked(), i)
                '''
                plm_order = ["oem", "deploy", "rma"]
                for i, sub_key in enumerate(plm_order):
                    if d['dpm_plm'].get('plm') == sub_key:
                            self.dpm_plmPage.plm_btn[i].setChecked(True)
                            self.dpm_plmPage.setPlmStage(i)
                                   
            elif key == 'mac0':
                if d['mac0'].get('mac') == "enable":
                    self.miscPage.mac0LineEdit.setText(d['mac0']['mac'])
                if d['mac0'].get('lock') == "enable":
                    self.miscPage.read_lock_mac0.setChecked(True)
            elif key == 'mac1':
                if d['mac1'].get('mac') == "enable":
                    self.miscPage.mac1LineEdit.setText(d['mac1']['mac'])
                if d['mac0'].get('lock') == "enable":
                    self.miscPage.read_lock_mac1.setChecked(True)
            elif key == 'dplypwd':
                if d['dplypwd'].get('pwd') == "enable":
                    self.dpm_plmPage.dplypwdEdit.setText(d['dplypwd']['pwd'])
                if d['dplypwd'].get('lock') == "enable":
                    self.dpm_plmPage.read_lock_Plm.setChecked(True)
            elif key == 'sec':
                self.miscPage.secureText.setPlainText(d['sec'])
            elif key == 'nonsec':
                self.miscPage.nonSecureText.setPlainText(d['nonsec'])
            elif key == 'huk0':
                self.keyPage.huk0Option.keyEdit.setText(d['huk0']['key'])
            elif key == 'huk1':
                self.keyPage.huk1Option.keyEdit.setText(d['huk1']['key'])
            elif key == 'huk2':
                self.keyPage.huk2Option.keyEdit.setText(d['huk2']['key'])
            elif key == 'key3':
                self.keyPage.keyStorage3Option.keyEdit.setText(d['key3']['key'])
                self.keyPage.keyStorage3Option.metaEdit.setCurrentText(d['key3']['meta'])
            elif key == 'key4':
                self.keyPage.keyStorage4Option.keyEdit.setText(d['key4']['key'])
                self.keyPage.keyStorage4Option.metaEdit.setCurrentText(d['key4']['meta'])
            elif key == 'key5':
                self.keyPage.keyStorage5Option.keyEdit.setText(d['key5']['key'])
                self.keyPage.keyStorage5Option.metaEdit.setCurrentText(d['key5']['meta'])
            elif key == 'publicx':
                self.keyPage.publicxEdit.setText(d['publicx'])
            elif key == 'publicy':
                self.keyPage.publicyEdit.setText(d['publicy'])
            elif key == 'aeskey':            
                self.keyPage.aeskeyEdit.setText(d['aeskey'])
            elif key == 'otpencrypt':
                if d["otpencrypt"].get("encrypt") == "yes":
                    if d["otpencrypt"].get("key"):
                        self.keyPage.otpOption.keyEdit.setText(d["otpencrypt"].get("key"))
                
    def addExportOption(self):
        self._Group = QGroupBox("Export OTP settings")
        _Layout = QVBoxLayout()
        self._Group.setLayout(_Layout)

        self.exportPov = QCheckBox("Power-On")
        self.exportDpmPlm = QCheckBox("PLM")
        self.exportMAC0 = QCheckBox("MAC0 address")
        self.exportMAC1 = QCheckBox("MAC1 address")
        self.exportDplypwd = QCheckBox("Deployed Password")
        self.exportSecure = QCheckBox("Secure Region")
        self.exportNonSecure = QCheckBox("Non-secure Region")
        self.exportKey = QCheckBox("Hardware Unique Key, Key Storage and IBR Key")
        self.exportOTPKey = QCheckBox("OTP Encrypt Key")
        self.void = QCheckBox("Void")
        self.void.setVisible(False)

        self.checkList = [
            self.exportPov,  self.exportDpmPlm, self.exportKey,
            self.exportMAC0, self.exportMAC1, self.exportOTPKey,
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
        _H2Layout.addWidget(self.void)

        _H3Layout = QHBoxLayout()
        _H3Layout.addWidget(self.exportButton)
        _H3Layout.addWidget(self.exportFileEdit)
        
        _H4Layout = QHBoxLayout()
        _H4Layout.addWidget(self.exportKey)
        _H4Layout.addWidget(self.exportOTPKey)

        _Layout.addLayout(_H1Layout)
        _Layout.addLayout(_H2Layout)
        _Layout.addLayout(_H4Layout)
        _Layout.addLayout(_H3Layout)
        self.mainLayout.addWidget(self._Group)

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
            else:
                boot_cfg["posotp"] = "disable"

            if _pov & (1 << 1):
                boot_cfg["qspiclk"] = "50mhz"
            else:
                boot_cfg["qspiclk"] = "30mhz"

            if _pov & (1 << 2):
                boot_cfg["wdt1en"] = "enable"
            else:   
                boot_cfg["wdt1en"] = "disable"

            if _pov & (1 << 4):
                boot_cfg["uart0en"] = "disable"
            else:
                boot_cfg["uart0en"] = "enable"

            if _pov & (1 << 5):
                boot_cfg["sd0bken"] = "enable"
            else:
                boot_cfg["sd0bken"] = "disable"

            #if _pov & (1 << 6):
            #    boot_cfg["tsiimg"] = "enable"
            #else:
            #    boot_cfg["tsiimg"] = "disable"

            #if _pov & (1 << 7):
            #    boot_cfg["tsidbg"] = "disable"
            #else:
            #    boot_cfg["tsidbg"] = "enable"
                
            if _pov & (1 << 9):
                boot_cfg["boot_iovol"] = "1_8v"
            else:
                boot_cfg["boot_iovol"] = "3_3v"

            bootsrc = (_pov >> 10) & 3

            if _pov & (3 << 10):

                if bootsrc == 1:
                    boot_cfg["bootsrc"] = "sd"
                elif bootsrc == 2:
                    boot_cfg["bootsrc"] = "nand"
                    if _pov & (3 << 12):
                        page = (_pov >> 12) & 3
                        if page == 1:
                            boot_cfg["page"] = "2k"
                        elif page == 2:
                            boot_cfg["page"] = "4k"
                        elif page == 3:
                            boot_cfg["page"] = "8k"                   
                    else:                       
                        boot_cfg["page"] = "2k"
                elif bootsrc == 3:
                    boot_cfg["bootsrc"] = "usb"
            else:
            
                boot_cfg["bootsrc"] = "spi"


            if (bootsrc != 3) and (_pov >> 14) & 3:

                option = (_pov >> 14) & 3

                _option = (
                    "spinand4", "spinor1", "spinor4",
                    "sd1", "sd1", "sd1",
                    "t12", "t24", "noecc"
                )

                boot_cfg["option"] = _option[bootsrc * 3 + option - 1]
                
            elif (bootsrc != 3):
                
                _option = (
                    "spinand1", "sd0", "ignore",
                )
                
                boot_cfg["option"] = _option[bootsrc]

            sec = self.povPage._bits_0.isChecked()
            if sec:
                boot_cfg["secboot"] = "enable"
                self.secure_dis = False
            else:
                boot_cfg["secboot"] = "disable"
                self.secure_dis = True
                
            delay = self.povPage._bootdelay.value()
            boot_cfg["bootdly"] = delay

            if self.povPage.read_lock_Pov.isChecked():
                boot_cfg["lock"] = "enable"
            else:
                boot_cfg["lock"] = "disable"
            
            self.otp_dict["boot_cfg"] = boot_cfg
    
    # DPM Hide Right Now
        
    def _exportDpmPlm(self):

        if self.exportDpmPlm.isChecked():

            #_dpmVal = self.dpm_plmPage.dpmVal
            _plmVal = self.dpm_plmPage.plmVal


            dpm_plm = {}
            '''
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
            '''
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
            mac0 = {}
            
            text = self.miscPage.mac0LineEdit.text()
            addr = text.replace(':', '')
            mac0["mac"] = addr
            if self.miscPage.read_lock_mac0.isChecked():
                mac0["lock"] = "enable"
            else:
                mac0["lock"] = "disable"
                
            self.otp_dict["mac0"] = mac0

        if self.exportMAC1.isChecked():
            mac1 = {}
            
            text = self.miscPage.mac1LineEdit.text()
            addr = text.replace(':', '')
            mac1["mac"] = addr
            if self.miscPage.read_lock_mac1.isChecked():
                mac1["lock"] = "enable"
            else:
                mac1["lock"]  = "disable"
                
            self.otp_dict["mac1"] = mac1

    def _exportDplyPwd(self):

        if self.exportDplypwd.isChecked():
            dplypwd = {}
            
            text = self.dpm_plmPage.dplypwdEdit.text()
            dplypwd["pwd"] = text
            if self.dpm_plmPage.read_lock_Plm.isChecked():
                dplypwd["lock"] = "enable"
            else:
                dplypwd["lock"] = "disable"
                
            self.otp_dict["dplypwd"] = dplypwd

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
                
                if i > 2:
                    _dict["meta"] = opt.metaEdit.currentText()

                if (i < 3 and opt.keyEdit.text()!=""):
                    self.otp_dict[key] = _dict
                    
                elif (i > 2 and opt.keyEdit.text()!="" and opt.metaEdit.currentText()!=""):
                    self.otp_dict[key] = _dict

            if self.keyPage.publicxEdit.text() != "":
                self.otp_dict["publicx"] = self.keyPage.publicxEdit.text()
            if self.keyPage.publicyEdit.text() != "":
                self.otp_dict["publicy"] = self.keyPage.publicyEdit.text()
            if self.keyPage.aeskeyEdit.text() != "":
                self.otp_dict["aeskey"] = self.keyPage.aeskeyEdit.text()
                    
    def _exportOTPKey(self):
        if self.exportOTPKey.isChecked():
            otpencrypt = {}
        
            if self.keyPage.otpOption.keyEdit.text() != "":
                otpencrypt["encrypt"] = "yes"
                otpencrypt["key"] = self.keyPage.otpOption.keyEdit.text()
                otpencrypt["Px"] = "28a15ee9d111b8f82e94dd5b55e820cb77e3ed86b95aa0165bcef93ff7a6e79a"
                otpencrypt["Py"] = "fa83470ec4db951db9923e35c920a47c53bc3ddc61692de0355da20e6085fae3"
            else:
                otpencrypt["encrypt"] = "no"
                
            self.otp_dict["otpencrypt"] = otpencrypt

    def _exportJson(self):

        # filename = "otp_export.json"
        self.otp_dict = {}

        self._exportPov()
        self._exportDpmPlm()
        self._exportMAC01()
        self._exportDplyPwd()
        self._exportSecureNonSecure()
        self._exportKey()
        self._exportOTPKey()

        # print(self.otp_dict)

    def exportFile(self):
        fileName, _ = QFileDialog.getSaveFileName(self,
                                    "save file",
                                    os.getcwd(),
                                    "Json (*.json)")

        if fileName != "":
            self.exportFileEdit.setText(fileName)

            self._exportJson()
            
            if self.secure_dis == False:
                reply = QMessageBox.warning(self,'Warning','WARNING: Secure boot is enabled, please make sure all secure boot settings are correct, OTP can only be programmed once',QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply != QMessageBox.Yes:
                    return
            with open(fileName, "w") as write_file:
                 json.dump(self.otp_dict, write_file, indent=4)

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    testPage = OtpPage()
    testPage.show()

    sys.exit(app.exec_())
