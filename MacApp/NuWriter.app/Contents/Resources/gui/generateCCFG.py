
#!/usr/bin/env python

import json
import os

from random import randrange

from PyQt5.QtCore import QDateTime, Qt, QTimer, QRegExp
from PyQt5.QtGui import QRegExpValidator, QIntValidator, QValidator
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QFormLayout, QWidget, QButtonGroup, QPlainTextEdit, QLineEdit, QFileDialog)

class ConfigHeaderInfo(QWidget):

    def __init__(self, title="", parent=None):
        super(ConfigHeaderInfo, self).__init__(parent)

        layout = QFormLayout()
        self.CCFG_header_version = QLineEdit('')
        self.CCFG_header_pagesize = QLineEdit('')
        self.CCFG_header_sparearea = QLineEdit('')
        self.CCFG_header_pageperblk = QLineEdit('')
        self.CCFG_header_quadread = QLineEdit('')
        self.CCFG_header_readsts = QLineEdit('')
        self.CCFG_header_writests = QLineEdit('')
        self.CCFG_header_stsvalue = QLineEdit('')
        self.CCFG_header_dummy1 = QLineEdit('')
        self.CCFG_header_dummy2 = QLineEdit('')
        self.CCFG_header_suspintvl = QLineEdit('')
        self.CCFG_header_secureboot = QCheckBox('Enable')
        self.CCFG_header_entrypoint = QLineEdit('')
        
        reg_hex32 = QRegExpValidator(QRegExp("[0-9A-Fa-f]{1,8}"))
        reg_hex8 = QRegExpValidator(QRegExp("[0-9A-Fa-f]{1,2}"))
        
        self.CCFG_header_version.setValidator(reg_hex32)
        self.CCFG_header_pagesize.setValidator(QIntValidator())
        self.CCFG_header_sparearea.setValidator(QIntValidator())
        self.CCFG_header_pageperblk.setValidator(QIntValidator())
        self.CCFG_header_quadread.setValidator(reg_hex8)
        self.CCFG_header_readsts.setValidator(reg_hex8)
        self.CCFG_header_writests.setValidator(reg_hex8)
        self.CCFG_header_stsvalue.setValidator(reg_hex8)
        self.CCFG_header_dummy1.setValidator(QIntValidator(0,1))
        self.CCFG_header_dummy2.setValidator(QIntValidator(0,1))
        self.CCFG_header_suspintvl.setValidator(QIntValidator(0,15))
        self.CCFG_header_entrypoint.setValidator(reg_hex32)
        
        layout.addRow(QLabel("Version:                                                    0x"), self.CCFG_header_version)
        layout.addRow(QLabel("SPI NAND flash Page Size:"), self.CCFG_header_pagesize)
        layout.addRow(QLabel("SPI NAND flash Spare Area Size:"), self.CCFG_header_sparearea)
        layout.addRow(QLabel("SPI NAND flash Page per block:"), self.CCFG_header_pageperblk)
        layout.addRow(QLabel("SPI NAND flash Quad Read Command:         0x"), self.CCFG_header_quadread)
        layout.addRow(QLabel("SPI NAND flash Read Status Command:        0x"), self.CCFG_header_readsts)
        layout.addRow(QLabel("SPI NAND flash Write Status Command:       0x"), self.CCFG_header_writests)
        layout.addRow(QLabel("SPI Status Register Bit Value:                       0x"), self.CCFG_header_stsvalue)
        layout.addRow(QLabel("SPI Dummy1 Byte:"), self.CCFG_header_dummy1)
        layout.addRow(QLabel("SPI Dummy2 Byte:"), self.CCFG_header_dummy2)
        layout.addRow(QLabel("SPI Suspend Interval:"), self.CCFG_header_suspintvl)
        layout.addRow(QLabel("Secureboot:"), self.CCFG_header_secureboot)
        layout.addRow(QLabel("Entrypoint:                                                0x"), self.CCFG_header_entrypoint)
        self.setLayout(layout)
        
class ConfigHeaderOption(QWidget):

    def __init__(self, title="", parent=None):
        super(ConfigHeaderOption, self).__init__(parent)

        reg_key64 = QRegExpValidator(QRegExp("[0-9A-Fa-f]{64}"))
        reg_hex32 = QRegExpValidator(QRegExp("[0-9A-Fa-f]{1,8}"))

        layout = QFormLayout()
        self.CCFG_headeropt_aeskey = QLineEdit('')
        self.CCFG_headeropt_aeskey_button = QPushButton('Generate')
        self.CCFG_headeropt_aeskey_sublayout = QHBoxLayout()
        self.CCFG_headeropt_aeskey_sublayout.addWidget(self.CCFG_headeropt_aeskey)
        self.CCFG_headeropt_aeskey_sublayout.addWidget(self.CCFG_headeropt_aeskey_button)
        self.CCFG_headeropt_ecdsakey = QLineEdit('')
        self.CCFG_headeropt_ecdsakey_button = QPushButton('Generate')
        self.CCFG_headeropt_ecdsakey_sublayout = QHBoxLayout()
        self.CCFG_headeropt_ecdsakey_sublayout.addWidget(self.CCFG_headeropt_ecdsakey)
        self.CCFG_headeropt_ecdsakey_sublayout.addWidget(self.CCFG_headeropt_ecdsakey_button)
        
        layout.addRow(QLabel("Aeskey:                       0x"), self.CCFG_headeropt_aeskey_sublayout)
        layout.addRow(QLabel("Ecdsakey:                     0x"), self.CCFG_headeropt_ecdsakey_sublayout)
        
        self.CCFG_headeropt_image_offset = []
        self.CCFG_headeropt_image_loadaddr = []
        self.CCFG_headeropt_image_type = []
        self.CCFG_headeropt_image_file = []
        self.CCFG_headeropt_image_button = []
        self.CCFG_headeropt_image_sublayout = []
               
        for i in range (0, 4):
            self.CCFG_headeropt_image_offset.append(QLineEdit(''))
            self.CCFG_headeropt_image_loadaddr.append(QLineEdit(''))
                        
            combobox = QComboBox(self)
            image_type = ['','1','2','3','4']
            combobox.addItems(image_type)
            self.CCFG_headeropt_image_type.append(combobox)
            
            self.CCFG_headeropt_image_file.append(QLineEdit(''))
            self.CCFG_headeropt_image_button.append(QPushButton('Browse'))
            self.CCFG_headeropt_image_sublayout.append(QHBoxLayout())
            
            self.CCFG_headeropt_image_offset[i].setValidator(reg_hex32)
            self.CCFG_headeropt_image_loadaddr[i].setValidator(reg_hex32)
        
            index = i + 1
            layout.addRow(QLabel(f"Image {index} Offset:            0x"), self.CCFG_headeropt_image_offset[i])
            layout.addRow(QLabel(f"Image {index} Loadaddr:       0x"), self.CCFG_headeropt_image_loadaddr[i])
            layout.addRow(QLabel(f"Image {index} Type:"), self.CCFG_headeropt_image_type[i])
            self.CCFG_headeropt_image_sublayout[i].addWidget(self.CCFG_headeropt_image_file[i])
            self.CCFG_headeropt_image_sublayout[i].addWidget(self.CCFG_headeropt_image_button[i])
            layout.addRow(QLabel(f"Image {index} File:"), self.CCFG_headeropt_image_sublayout[i])
                       
            self.CCFG_headeropt_image_button[i].clicked.connect(lambda ch, i = i: self.CCFG_image_file_browse(i))       

        self.CCFG_headeropt_aeskey.setValidator(reg_key64)
        self.CCFG_headeropt_ecdsakey.setValidator(reg_key64)
        
        self.setLayout(layout)
        
        self.CCFG_headeropt_aeskey_button.clicked.connect(self.CCFG_headeropt_aeskey_gen)
        self.CCFG_headeropt_ecdsakey_button.clicked.connect(self.CCFG_headeropt_ecdsakey_gen)
        
    def CCFG_headeropt_aeskey_gen(self):
        aeskey = ''.join(['%x' % randrange(16) for _ in range(0, 64)])
        self.CCFG_headeropt_aeskey.setText(aeskey)
        
    def CCFG_headeropt_ecdsakey_gen(self):
        ecdsakey = ''.join(['%x' % randrange(16) for _ in range(0, 64)])
        self.CCFG_headeropt_ecdsakey.setText(ecdsakey)
        
    def CCFG_image_file_browse(self, i):
        filename = ""
        # Fix for crash in X on Ubuntu 14.04
        filename, _ = QFileDialog.getOpenFileName()
        if filename != "":
            self.CCFG_headeropt_image_file[i].setText(filename)
   
class ConfigEnvInfo(QWidget):

    def __init__(self, title="", parent=None):
        super(ConfigEnvInfo, self).__init__(parent)

        layout = QFormLayout()
        self.CCFG_env_file = QLineEdit('')
        self.CCFG_env_blksize = QLineEdit('')
        reg_hex32 = QRegExpValidator(QRegExp("[0-9A-Fa-f]{1,8}"))
        self.CCFG_env_blksize.setValidator(reg_hex32)
        layout.addRow(QLabel("File:"), self.CCFG_env_file)
        layout.addRow(QLabel("Block Size:   0x"), self.CCFG_env_blksize)
        self.setLayout(layout)

class ConfigDataInfo(QWidget):

    def __init__(self, title="", parent=None):
        super(ConfigDataInfo, self).__init__(parent)

        layout = QFormLayout()
        self.CCFG_data_aeskey = QLineEdit('')
        self.CCFG_data_ecdsakey = QLineEdit('')
        self.CCFG_data_image1_file = QLineEdit('')
        self.CCFG_data_image2_file = QLineEdit('')
        self.CCFG_data_image3_file = QLineEdit('')
        self.CCFG_data_image4_file = QLineEdit('')
        
        reg_key64 = QRegExpValidator(QRegExp("[0-9A-Fa-f]{64}"))
        self.CCFG_data_aeskey.setValidator(reg_key64)
        self.CCFG_data_ecdsakey.setValidator(reg_key64)
        
        layout.addRow(QLabel("Aeskey:   0x"), self.CCFG_data_aeskey)
        layout.addRow(QLabel("Ecdsakey: 0x"), self.CCFG_data_ecdsakey)
        layout.addRow(QLabel("Image 1 File:"), self.CCFG_data_image1_file)
        layout.addRow(QLabel("Image 2 File:"), self.CCFG_data_image2_file)
        layout.addRow(QLabel("Image 3 File:"), self.CCFG_data_image3_file)
        layout.addRow(QLabel("Image 4 File:"), self.CCFG_data_image4_file)
        self.setLayout(layout)

class CCFG_MainPage(QWidget):

    def __init__(self, title="", parent=None):
        super(CCFG_MainPage, self).__init__(parent)
        
        self.mainLayout = QVBoxLayout()
        self.tabMedia = QTabWidget()
        self.setStyleSheet("QLabel{font-family:monospace;}")
        
        self.CCFG_Header = ConfigHeaderInfo()
        self.tabMedia.addTab(self.CCFG_Header, 'Header Setting')
        
        self.CCFG_HeaderOpt = ConfigHeaderOption()
        self.tabMedia.addTab(self.CCFG_HeaderOpt, 'Header Option')
        
        # hide env and data right now
        
        #self.CCFG_Env = ConfigEnvInfo()
        #self.tabMedia.addTab(self.CCFG_Env, 'Env Setting')
        
        #self.CCFG_Data = ConfigDataInfo()
        #self.tabMedia.addTab(self.CCFG_Data, 'Data Setting')
        
        self.gen_Button = QPushButton('Export')
        self.gen_Button.clicked.connect(self.exportFile)

        self.mainLayout.addWidget(self.tabMedia)
        self.mainLayout.addWidget(self.gen_Button)
        
        self.setLayout(self.mainLayout)
        
        #self.showExport("C:\\Users\\PWHSU0\\Desktop\\MA35D1\\header.json")
        
    def hideExport(self):
        self.gen_Button.setHidden(True)
        
    def showExport(self, text):
        self.ccfg_file_names = text
        
        try:
            with open(self.ccfg_file_names, 'r') as json_file:
                try:
                    d = json.load(json_file)
                except json.decoder.JSONDecodeError as err:
                    print(f"{self.ccfg_file_names} parsing error")
                    return
        except (IOError, OSError) as err:
            print(f"Open {self.ccfg_file_names} failed")
            return

        for key in d.keys():
            if key == 'header':
                self.CCFG_Header.CCFG_header_version.setText((d['header'].get('version')).replace('0x',''))
                if d['header'].get('spiinfo'): 
                    self.CCFG_Header.CCFG_header_pagesize.setText(d['header']['spiinfo'].get('pagesize'))
                    self.CCFG_Header.CCFG_header_sparearea.setText(d['header']['spiinfo'].get('sparearea'))
                    self.CCFG_Header.CCFG_header_pageperblk.setText(d['header']['spiinfo'].get('pageperblk'))
                    self.CCFG_Header.CCFG_header_quadread.setText((d['header']['spiinfo'].get('quadread')).replace('0x',''))
                    self.CCFG_Header.CCFG_header_readsts.setText((d['header']['spiinfo'].get('readsts')).replace('0x',''))
                    self.CCFG_Header.CCFG_header_writests.setText((d['header']['spiinfo'].get('writests')).replace('0x',''))
                    self.CCFG_Header.CCFG_header_stsvalue.setText((d['header']['spiinfo'].get('stsvalue')).replace('0x',''))
                    self.CCFG_Header.CCFG_header_dummy1.setText(d['header']['spiinfo'].get('dummy1'))
                    self.CCFG_Header.CCFG_header_dummy2.setText(d['header']['spiinfo'].get('dummy2'))
                    self.CCFG_Header.CCFG_header_suspintvl.setText(d['header']['spiinfo'].get('suspintvl'))
                self.CCFG_Header.CCFG_header_secureboot.setText(d['header'].get('secureboot'))
                self.CCFG_Header.CCFG_header_entrypoint.setText((d['header'].get('entrypoint')).replace('0x',''))
                self.CCFG_HeaderOpt.CCFG_headeropt_aeskey.setText(d['header'].get('aeskey'))
                self.CCFG_HeaderOpt.CCFG_headeropt_ecdsakey.setText(d['header'].get('ecdsakey'))
                if d['header'].get('image'): 
                    for i in range(len(d['header']['image'])):
                        self.CCFG_HeaderOpt.CCFG_headeropt_image_offset[i].setText((d['header']['image'][i].get('offset')).replace('0x','')) 
                        self.CCFG_HeaderOpt.CCFG_headeropt_image_loadaddr[i].setText((d['header']['image'][i].get('loadaddr')).replace('0x',''))
                        self.CCFG_HeaderOpt.CCFG_headeropt_image_type[i].setCurrentText(d['header']['image'][i].get('type'))
                        self.CCFG_HeaderOpt.CCFG_headeropt_image_file[i].setText(d['header']['image'][i].get('file')) 
                        
    
    def exportJson(self):
    
        self.ccfg_dict = {}
        
        reg_hex32 = QRegExpValidator(QRegExp("[0-9A-Fa-f]{1,8}"))
        reg_hex8 = QRegExpValidator(QRegExp("[0-9A-Fa-f]{1,2}"))
        reg_key64 = QRegExpValidator(QRegExp("[0-9A-Fa-f]{64}"))
        reg_4int = QRegExpValidator(QRegExp("[1-4]{1}"))
        
        header = {}
     
        if reg_hex32.validate(self.CCFG_Header.CCFG_header_version.text(),0)[0] == QValidator.Acceptable :
            header["version"] = "0x" + self.CCFG_Header.CCFG_header_version.text()
        else:
            header["version"] = "0x00000000"
        
        spiinfo = {}
        
        if QIntValidator().validate(self.CCFG_Header.CCFG_header_pagesize.text(),0)[0] == QValidator.Acceptable :
            spiinfo["pagesize"] = self.CCFG_Header.CCFG_header_pagesize.text()
        else:
            spiinfo["pagesize"] = '0'
        if QIntValidator().validate(self.CCFG_Header.CCFG_header_sparearea.text(),0)[0] == QValidator.Acceptable :
            spiinfo["sparearea"] = self.CCFG_Header.CCFG_header_sparearea.text()
        else:
            spiinfo["sparearea"] = '0'
        if QIntValidator().validate(self.CCFG_Header.CCFG_header_pageperblk.text(),0)[0] == QValidator.Acceptable :
            spiinfo["pageperblk"] = self.CCFG_Header.CCFG_header_pageperblk.text()
        else:
            spiinfo["pageperblk"] = '0'
        if reg_hex8.validate(self.CCFG_Header.CCFG_header_quadread.text(),0)[0] == QValidator.Acceptable :
            spiinfo["quadread"] = "0x" + self.CCFG_Header.CCFG_header_quadread.text()
        else:
            spiinfo["quadread"] = '0x00'
        if reg_hex8.validate(self.CCFG_Header.CCFG_header_readsts.text(),0)[0] == QValidator.Acceptable :
            spiinfo["readsts"] = "0x" +self.CCFG_Header.CCFG_header_readsts.text()
        else:
            spiinfo["readsts"] = '0x00'
        if reg_hex8.validate(self.CCFG_Header.CCFG_header_writests.text(),0)[0] == QValidator.Acceptable :
            spiinfo["writests"] = "0x" +self.CCFG_Header.CCFG_header_writests.text()
        else:
            spiinfo["writests"] = '0x00'
        if reg_hex8.validate(self.CCFG_Header.CCFG_header_stsvalue.text(),0)[0] == QValidator.Acceptable :
            spiinfo["stsvalue"] = "0x" +self.CCFG_Header.CCFG_header_stsvalue.text()
        else:
            spiinfo["stsvalue"] = '0x00'
        if QIntValidator(0,1).validate(self.CCFG_Header.CCFG_header_dummy1.text(),0)[0] == QValidator.Acceptable :
            spiinfo["dummy1"] = self.CCFG_Header.CCFG_header_dummy1.text()
        else:
            spiinfo["dummy1"] = '0'
        if QIntValidator(0,1).validate(self.CCFG_Header.CCFG_header_dummy2.text(),0)[0] == QValidator.Acceptable :
            spiinfo["dummy2"] = self.CCFG_Header.CCFG_header_dummy2.text()
        else:
            spiinfo["dummy2"] = '0'
        if QIntValidator(0,15).validate(self.CCFG_Header.CCFG_header_suspintvl.text(),0)[0] == QValidator.Acceptable :
            spiinfo["suspintvl"] = self.CCFG_Header.CCFG_header_suspintvl.text()
        else:
            spiinfo["suspintvl"] = '0'
        
        header["spiinfo"] = spiinfo
        
        if self.CCFG_Header.CCFG_header_secureboot.isChecked():
            header["secureboot"] = "yes"
        else:
            header["secureboot"] = "no"
        if reg_hex32.validate(self.CCFG_Header.CCFG_header_entrypoint.text(),0)[0] == QValidator.Acceptable :
            header["entrypoint"] = "0x" + self.CCFG_Header.CCFG_header_entrypoint.text()
        else:
            header["entrypoint"] = "0x00000000" 

        if reg_key64.validate(self.CCFG_HeaderOpt.CCFG_headeropt_aeskey.text(),0)[0] == QValidator.Acceptable :
            header["aeskey"] = self.CCFG_HeaderOpt.CCFG_headeropt_aeskey.text()
        if reg_key64.validate(self.CCFG_HeaderOpt.CCFG_headeropt_ecdsakey.text(),0)[0] == QValidator.Acceptable :
            header["ecdsakey"] = self.CCFG_HeaderOpt.CCFG_headeropt_ecdsakey.text()
            
        image = []
        
        if (reg_hex32.validate(self.CCFG_HeaderOpt.CCFG_headeropt_image_offset[0].text(),0)[0] == QValidator.Acceptable and
        reg_hex32.validate(self.CCFG_HeaderOpt.CCFG_headeropt_image_loadaddr[0].text(),0)[0] == QValidator.Acceptable and
        self.CCFG_HeaderOpt.CCFG_headeropt_image_file[0].text() != "") :
            dict1 = {}
            dict1["offset"] = "0x" + self.CCFG_HeaderOpt.CCFG_headeropt_image_offset[0].text()
            dict1["loadaddr"] = "0x" + self.CCFG_HeaderOpt.CCFG_headeropt_image_loadaddr[0].text()
            dict1["type"] = self.CCFG_HeaderOpt.CCFG_headeropt_image_type[0].currentText()
            dict1["file"] = self.CCFG_HeaderOpt.CCFG_headeropt_image_file[0].text()
            image.append(dict1)
            
        if (reg_hex32.validate(self.CCFG_HeaderOpt.CCFG_headeropt_image_offset[1].text(),0)[0] == QValidator.Acceptable and
        reg_hex32.validate(self.CCFG_HeaderOpt.CCFG_headeropt_image_loadaddr[1].text(),0)[0] == QValidator.Acceptable and
        self.CCFG_HeaderOpt.CCFG_headeropt_image_file[1].text() != "") :
            dict2 = {}
            dict2["offset"] = "0x" + self.CCFG_HeaderOpt.CCFG_headeropt_image_offset[1].text()
            dict2["loadaddr"] = "0x" + self.CCFG_HeaderOpt.CCFG_headeropt_image_loadaddr[1].text()
            dict2["type"] = self.CCFG_HeaderOpt.CCFG_headeropt_image_type[1].currentText()
            dict2["file"] = self.CCFG_HeaderOpt.CCFG_headeropt_image_file[1].text()
            image.append(dict2)
            
        if (reg_hex32.validate(self.CCFG_HeaderOpt.CCFG_headeropt_image_offset[2].text(),0)[0] == QValidator.Acceptable and
        reg_hex32.validate(self.CCFG_HeaderOpt.CCFG_headeropt_image_loadaddr[2].text(),0)[0] == QValidator.Acceptable and
        self.CCFG_HeaderOpt.CCFG_headeropt_image_file[2].text() != "") :
            dict3 = {}
            dict3["offset"] = "0x" + self.CCFG_HeaderOpt.CCFG_headeropt_image_offset[2].text()
            dict3["loadaddr"] = "0x" + self.CCFG_HeaderOpt.CCFG_headeropt_image_loadaddr[2].text()
            dict3["type"] = self.CCFG_HeaderOpt.CCFG_headeropt_image_type[2].currentText()
            dict3["file"] = self.CCFG_HeaderOpt.CCFG_headeropt_image_file[2].text()
            image.append(dict3)
            
        if (reg_hex32.validate(self.CCFG_HeaderOpt.CCFG_headeropt_image_offset[3].text(),0)[0] == QValidator.Acceptable and
        reg_hex32.validate(self.CCFG_HeaderOpt.CCFG_headeropt_image_loadaddr[3].text(),0)[0] == QValidator.Acceptable and
        self.CCFG_HeaderOpt.CCFG_headeropt_image_file[3].text() != "") :
            dict4 = {}
            dict4["offset"] = "0x" + self.CCFG_HeaderOpt.CCFG_headeropt_image_offset[3].text()
            dict4["loadaddr"] = "0x" + self.CCFG_HeaderOpt.CCFG_headeropt_image_loadaddr[3].text()
            dict4["type"] = self.CCFG_HeaderOpt.CCFG_headeropt_image_type[3].currentText()
            dict4["file"] = self.CCFG_HeaderOpt.CCFG_headeropt_image_file[3].text()
            image.append(dict4)
            
        if bool(image):
            header["image"] = image
        
        self.ccfg_dict["header"] = header
        
        '''
        # hide env and data right now
        env = {}
        
        if self.CCFG_Env.CCFG_env_file.text() != "" and reg_hex32.validate(self.CCFG_Env.CCFG_env_blksize.text(),0)[0] == QValidator.Acceptable :
            env["file"] = self.CCFG_Env.CCFG_env_file.text()
            env["blksize"] = self.CCFG_Env.CCFG_env_blksize.text()
            self.ccfg_dict["env"] = env       
            
        data = {}
        
        if reg_key64.validate(self.CCFG_Data.CCFG_data_aeskey.text(),0)[0] == QValidator.Acceptable :
            data["aeskey"] = self.CCFG_Data.CCFG_data_aeskey.text()
        if reg_key64.validate(self.CCFG_Data.CCFG_data_ecdsakey.text(),0)[0] == QValidator.Acceptable :
            data["ecdsakey"] = self.CCFG_Data.CCFG_data_ecdsakey.text()
            
        image_data = []
        
        if self.CCFG_Data.CCFG_data_image1_file.text() != "" :
            dict1 = {}
            dict1["file"] = self.CCFG_Data.CCFG_data_image1_file.text()
            image_data.append(dict1)
        if self.CCFG_Data.CCFG_data_image2_file.text() != "" :
            dict2 = {}
            dict2["file"] = self.CCFG_Data.CCFG_data_image2_file.text()
            image_data.append(dict2)
        if self.CCFG_Data.CCFG_data_image3_file.text() != "" :
            dict3 = {}
            dict3["file"] = self.CCFG_Data.CCFG_data_image3_file.text()
            image_data.append(dict3)
        if self.CCFG_Data.CCFG_data_image4_file.text() != "" :
            dict4 = {}
            dict4["file"] = self.CCFG_Data.CCFG_data_image4_file.text()
            image_data.append(dict4)
        
        if bool(image_data):
            data["image"] = image_data
         
        if bool(data):
            self.ccfg_dict["data"] = data
        '''
    def exportFile(self):
    
        fileName, _ = QFileDialog.getSaveFileName(self,
                                    "save file",
                                    os.getcwd(),
                                    "json(*.json)")

        if fileName != "":

            self.exportJson()
            
            with open(fileName, "w") as write_file:
                json.dump(self.ccfg_dict, write_file, indent=4)

if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    w = CCFG_MainPage()
    w.show()
    sys.exit(app.exec_())
