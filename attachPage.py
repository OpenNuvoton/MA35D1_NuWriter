
#!/usr/bin/env python

import json
import os

from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QComboBox, 
        QDateTimeEdit, QDial, QDialog, QFileDialog, QFormLayout, QGridLayout, 
        QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QProgressBar, 
        QPushButton, QRadioButton, QScrollBar, QSizePolicy, QSlider, QSpinBox, 
        QStyleFactory, QTableWidget, QTabWidget, QTextEdit, QVBoxLayout, QWidget)

class SpiNorInfo(QWidget):

    def __init__(self, title="", parent=None):
        super(SpiNorInfo, self).__init__(parent)

        layout = QFormLayout()
        self.SpiNor_quadread = QLineEdit('')
        self.SpiNor_readsts = QLineEdit('')
        self.SpiNor_writests = QLineEdit('')
        self.SpiNor_stsvalue = QLineEdit('')
        self.SpiNor_dummy = QLineEdit('')
        
        layout.addRow(QLabel("Quad Read Command:"), self.SpiNor_quadread)
        layout.addRow(QLabel("Read Status Command:"), self.SpiNor_readsts)
        layout.addRow(QLabel("Write Status Command:"), self.SpiNor_writests)
        layout.addRow(QLabel("Status Value:"), self.SpiNor_stsvalue)
        layout.addRow(QLabel("Dummy Byte:"), self.SpiNor_dummy)
        self.setLayout(layout)

class SpiNandInfo(QWidget):

    def __init__(self, title="", parent=None):
        super(SpiNandInfo, self).__init__(parent)

        layout = QFormLayout()
        self.SpiNand_pagesize = QLineEdit('')
        self.SpiNand_sparearea = QLineEdit('')
        self.SpiNand_quadread = QLineEdit('')
        self.SpiNand_readsts = QLineEdit('')
        self.SpiNand_writests = QLineEdit('')
        self.SpiNand_stsvalue = QLineEdit('')
        self.SpiNand_pageperblk = QLineEdit('')
        self.SpiNand_dummy = QLineEdit('')
        self.SpiNand_blkcnt = QLineEdit('')
        
        layout.addRow(QLabel("Page Size:"), self.SpiNand_pagesize)
        layout.addRow(QLabel("Spare Area:"), self.SpiNand_sparearea)
        layout.addRow(QLabel("Quad Read Command:"), self.SpiNand_quadread)
        layout.addRow(QLabel("Read Status Command:"), self.SpiNand_readsts)
        layout.addRow(QLabel("Write Status Command:"), self.SpiNand_writests)
        layout.addRow(QLabel("Status Value:"), self.SpiNand_stsvalue)
        layout.addRow(QLabel("PagePerBlock:"), self.SpiNand_pageperblk)
        layout.addRow(QLabel("Dummy Byte:"), self.SpiNand_dummy)
        layout.addRow(QLabel("Block Count:"), self.SpiNand_blkcnt)
        self.setLayout(layout)

class NandInfo(QWidget):

    def __init__(self, title="", parent=None):
    
        super(NandInfo, self).__init__(parent)
        
        layout = QFormLayout()
        self.Nand_blkcnt = QLineEdit('')
        self.Nand_pageperblk = QLineEdit('')
        
        layout.addRow(QLabel("Block Count:"), self.Nand_blkcnt)
        layout.addRow(QLabel("PagePerBlock:"), self.Nand_pageperblk)
        self.setLayout(layout)
        
class LedInfo(QWidget):

    def __init__(self, title="", parent=None):
    
        super(LedInfo, self).__init__(parent)
        
        layout = QFormLayout()
        self.Led_port = QLineEdit('')
        self.Led_bit = QLineEdit('')
        self.Led_on = QLineEdit('')
        self.Led_off = QLineEdit('')
        
        layout.addRow(QLabel("LED Port:"), self.Led_port)
        layout.addRow(QLabel("LED bit:"), self.Led_bit)
        layout.addRow(QLabel("LED on:"), self.Led_on)
        layout.addRow(QLabel("LED off:"), self.Led_off)
        self.setLayout(layout)


class SetInfoPage(QWidget):
    
    def __init__(self, parent=None):
        super(SetInfoPage, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        
        self.info_file_names = ""
        
        self.parent = parent
        
        self.mainLayout = QVBoxLayout()
        self.tabMedia = QTabWidget()

        self.spiNor = SpiNorInfo()
        self.spiNand = SpiNandInfo()
        self.nand = NandInfo()
        self.led = LedInfo()
        
        self.tabMedia.addTab(self.spiNor, 'SPI NOR')
        self.tabMedia.addTab(self.spiNand, 'SPI NAND')
        self.tabMedia.addTab(self.nand, 'NAND')
        self.tabMedia.addTab(self.led, 'LED')

        self.gen_Button = QPushButton('Export')
        self.gen_Button.clicked.connect(self.exportFile)

        self.mainLayout.addWidget(self.tabMedia)
        self.mainLayout.addWidget(self.gen_Button)
        self.setLayout(self.mainLayout)

        #self.set_info_name("C:\\Users\\PWHSU0\\Desktop\\MA35D1_NuWriter-master\\info.json")  <- For Debug
    
    # use to import exist json to window
    def set_info_name(self, text):
        self.info_file_names = text
        try:
            with open(self.info_file_names, 'r') as json_file:
                try:
                    d = json.load(json_file)
                except json.decoder.JSONDecodeError as err:
                    print(f"{self.info_file_names} parsing error")
                    return
        except (IOError, OSError) as err:
            print(f"Open {self.info_file_names} failed")
            return
                
        for key in d.keys():
            if key == 'spinor':
                for sub_key in d['spinor'].keys():
                    if sub_key == 'quadread':
                        self.spiNor.SpiNor_quadread.setText(d['spinor']['quadread'])
                    elif sub_key == 'readsts':
                        self.spiNor.SpiNor_readsts.setText(d['spinor']['readsts'])
                    elif sub_key == 'writests':
                        self.spiNor.SpiNor_writests.setText(d['spinor']['writests'])
                    elif sub_key == 'stsvalue':
                        self.spiNor.SpiNor_stsvalue.setText(d['spinor']['stsvalue'])
                    elif sub_key == 'dummy':
                        self.spiNor.SpiNor_dummy.setText(d['spinor']['dummy'])
            elif key == 'spinand':
                for sub_key in d['spinand'].keys():
                    if sub_key == 'pagesize':
                        self.spiNand.SpiNand_pagesize.setText(d['spinand']['pagesize'])
                    elif sub_key == 'sparearea':
                        self.spiNand.SpiNand_sparearea.setText(d['spinand']['sparearea'])
                    elif sub_key == 'quadread':
                        self.spiNand.SpiNand_quadread.setText(d['spinand']['quadread'])
                    elif sub_key == 'readsts':
                        self.spiNand.SpiNand_readsts.setText(d['spinand']['readsts'])
                    elif sub_key == 'writests':
                        self.spiNand.SpiNand_writests.setText(d['spinand']['writests'])
                    elif sub_key == 'stsvalue':
                        self.spiNand.SpiNand_stsvalue.setText(d['spinand']['stsvalue'])
                    elif sub_key == 'dummy':
                        self.spiNand.SpiNand_dummy.setText(d['spinand']['dummy'])
                    elif sub_key == 'blkcnt':
                        self.spiNand.SpiNand_blkcnt.setText(d['spinand']['blkcnt'])
                    elif sub_key == 'pageperblk':
                        self.spiNand.SpiNand_pageperblk.setText(d['spinand']['pageperblk'])
            elif key == 'nand':
                for sub_key in d['nand'].keys():
                    if sub_key == 'blkcnt':
                        self.nand.Nand_blkcnt.setText(d['nand']['blkcnt'])
                    elif sub_key == 'pageperblk':
                        self.nand.Nand_pageperblk.setText(d['nand']['pageperblk'])
            elif key == 'led':
                for sub_key in d['led'].keys():
                    if sub_key == 'port':
                        self.led.Led_port.setText(d['led']['port'])
                    elif sub_key == 'bit':
                        self.led.Led_bit.setText(d['led']['bit'])
                    elif sub_key == 'on':
                        self.led.Led_on.setText(d['led']['on'])
                    elif sub_key == 'off':
                        self.led.Led_off.setText(d['led']['off'])
    
    def exportJson(self):
    
        self.info_dict = {}
        
        spinor = {}
        
        spinor["quadread"] = self.spiNor.SpiNor_quadread.text()
        spinor["readsts"] = self.spiNor.SpiNor_readsts.text()
        spinor["writests"] = self.spiNor.SpiNor_writests.text()
        spinor["stsvalue"] = self.spiNor.SpiNor_stsvalue.text()
        spinor["dummy"] = self.spiNor.SpiNor_dummy.text()

        spinand = {}
        
        spinand["pagesize"] = self.spiNand.SpiNand_pagesize.text()
        spinand["sparearea"] = self.spiNand.SpiNand_sparearea.text()
        spinand["quadread"] = self.spiNand.SpiNand_quadread.text()
        spinand["readsts"] = self.spiNand.SpiNand_readsts.text()
        spinand["writests"] = self.spiNand.SpiNand_writests.text()
        spinand["stsvalue"] = self.spiNand.SpiNand_stsvalue.text()
        spinand["dummy"] = self.spiNand.SpiNand_dummy.text()
        spinand["blkcnt"] = self.spiNand.SpiNand_blkcnt.text()
        spinand["pageperblk"] = self.spiNand.SpiNand_pageperblk.text()
        
        nand = {}
        
        nand["blkcnt"] = self.nand.Nand_blkcnt.text()
        nand["pageperblk"] = self.nand.Nand_pageperblk.text()
        
        led = {}
        
        led["port"] = self.led.Led_port.text()
        led["bit"] = self.led.Led_bit.text()
        led["on"] = self.led.Led_on.text()
        led["off"] = self.led.Led_off.text()
        
        self.info_dict["spinor"] = spinor
        self.info_dict["spinand"] = spinand
        self.info_dict["nand"] = nand
        self.info_dict["led"] = led
    
    def exportFile(self):
    
        fileName, _ = QFileDialog.getSaveFileName(self,
                                    "save file",
                                    os.getcwd(),
                                    "json(*.json)")

        if fileName != "":

            self.exportJson()
            
            with open(fileName, "w") as write_file:
                json.dump(self.info_dict, write_file, indent=4)

            self.parent.InfoFileLineEdit.setText(fileName)
    

if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    w = SetInfoPage()
    w.__init__()
    w.show()
    sys.exit(app.exec_())
