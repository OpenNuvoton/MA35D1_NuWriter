
#!/usr/bin/env python

import os
import json

from PyQt5.QtCore import QDateTime, Qt, QTimer, QRegExp
from PyQt5.QtGui import QRegExpValidator, QIntValidator, QValidator
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QFormLayout, QWidget, QButtonGroup, QPlainTextEdit, QLineEdit, QFileDialog)
        
     
class PackImage(QWidget):

    def __init__(self, num = 6, pagenum = 0,title="", parent=None):
        super(PackImage, self).__init__(parent)
        
        self._num = num
        self.PCFG_image_offset = []
        self.PCFG_image_file = []
        self.PCFG_image_button = []
        self.PCFG_image_sublayout = []
        self.PCFG_image_type = []

        layout = QFormLayout()
        reg_hex32 = QRegExpValidator(QRegExp("0x[0-9A-Fa-f]{1,8}"))
        reg_zero = QRegExpValidator(QRegExp("[0]{1}"))

        for i in range (0, num):
            self.PCFG_image_offset.append(QLineEdit(''))
            self.PCFG_image_file.append(QLineEdit(''))
            self.PCFG_image_button.append(QPushButton('Browse'))
            self.PCFG_image_sublayout.append(QHBoxLayout())
            self.PCFG_image_type.append(QLineEdit(''))
            self.PCFG_image_offset[i].setValidator(reg_hex32)
            self.PCFG_image_type[i].setValidator(reg_zero)
            index = pagenum * 6 + i + 1
            layout.addRow(QLabel(f"Image {index} Offset:"), self.PCFG_image_offset[i])
            self.PCFG_image_sublayout[i].addWidget(self.PCFG_image_file[i])
            self.PCFG_image_sublayout[i].addWidget(self.PCFG_image_button[i])
            layout.addRow(QLabel(f"Image {index} File:"), self.PCFG_image_sublayout[i])
            layout.addRow(QLabel(f"Image {index} Type:"), self.PCFG_image_type[i])
            
            self.PCFG_image_button[i].clicked.connect(lambda ch, i = i: self.PCFG_image_file_browse(i))
            
        self.setLayout(layout)
    
    def PCFG_image_file_browse(self, i):
        filename = ""
        # Fix for crash in X on Ubuntu 14.04
        filename, _ = QFileDialog.getOpenFileName()
        if filename != "":
            self.PCFG_image_file[i].setText(filename)
            
    def get_num(self):
        return self._num

class PCFG_MainPage(QWidget):
    def __init__(self, num=12, parent=None):
        super(PCFG_MainPage, self).__init__(parent)
        self.mainLayout = QVBoxLayout()
        self.tabMedia = QTabWidget()
        #print(f"{num},{parent}")
        pagenum = int((num - 1)/6 + 1)
        lastpagecount = 6 if int(num % 6) == 0 else int(num % 6)
        
        self.PCFG_Image = []
        for i in range (0, pagenum):
            if i == pagenum - 1 :
                self.PCFG_Image.append(PackImage(lastpagecount,i,self))
            else:
                self.PCFG_Image.append(PackImage(6,i,self))
            self.tabMedia.addTab(self.PCFG_Image[i], 'Pack Image Group ' + str(i+1))
        
        self.gen_Button = QPushButton('Export')
        self.gen_Button.clicked.connect(self.exportFile)

        self.mainLayout.addWidget(self.tabMedia)
        self.mainLayout.addWidget(self.gen_Button)
        
        self.setLayout(self.mainLayout)
     
    def exportJson(self):
    
        self.pcfg_dict = {}
        
        reg_hex32 = QRegExpValidator(QRegExp("0x[0-9A-Fa-f]{1,8}"))
        reg_zero = QRegExpValidator(QRegExp("[0]{1}"))
        
        image = []
        
        for i in range (0, len(self.PCFG_Image)): 
            for j in range (0, self.PCFG_Image[i].get_num()):
                if (reg_hex32.validate(self.PCFG_Image[i].PCFG_image_offset[j].text(),0)[0] == QValidator.Acceptable and
                self.PCFG_Image[i].PCFG_image_file[j].text() != "" and
                reg_zero.validate(self.PCFG_Image[i].PCFG_image_type[j].text(),0)[0] == QValidator.Acceptable):
                    dict_image = {}
                    dict_image["offset"] = self.PCFG_Image[i].PCFG_image_offset[j].text()
                    dict_image["file"] = self.PCFG_Image[i].PCFG_image_file[j].text()
                    dict_image["type"] = int(self.PCFG_Image[i].PCFG_image_type[j].text())
                    image.append(dict_image)

        if bool(image):
            self.pcfg_dict["image"] = image    
        
    def exportFile(self):
    
        fileName, _ = QFileDialog.getSaveFileName(self,
                                    "save file",
                                    os.getcwd(),
                                    "json(*.json)")

        if fileName != "":

            self.exportJson()
            
            with open(fileName, "w") as write_file:
                json.dump(self.pcfg_dict, write_file, indent=4)

if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    w = PCFG_MainPage()
    w.show()
    sys.exit(app.exec_())
