
#!/usr/bin/python3

import os
import sys

from configparser import ConfigParser
from webbrowser import open_new
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject, QRunnable, QThreadPool

from nuwriter import (DEV_DDR_SRAM, DEV_NAND, DEV_OTP, DEV_SD_EMMC,
        DEV_SPINAND, DEV_SPINOR, DEV_USBH,
        OPT_NONE, OPT_SCRUB, OPT_WITHBAD, OPT_EXECUTE, OPT_VERIFY,
        OPT_UNPACK, OPT_RAW, OPT_EJECT, OPT_SETINFO, OPT_CONCAT, 
        OPT_OTPBLK1, OPT_OTPBLK2, OPT_OTPBLK3, OPT_OTPBLK4, OPT_OTPBLK5, OPT_OTPBLK6, OPT_OTPBLK7,
        do_attach, do_convert, do_pack, do_stuff, do_unpack, do_img_erase, do_img_program, do_img_read, 
        do_otp_program, do_otp_erase, do_otp_read,
        do_pack_program, do_msc)        

from mainwindow import Ui_MainWindow
from gui.mediaPages import MediaPage
from attachPage import SetInfoPage
from gui.otpPage import OtpPage
from gui.generateCCFG import CCFG_MainPage
from gui.generatePCFG import PCFG_MainPage

class EmittingStream(QtCore.QObject):

    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))

    def flush(self):
        pass
try:
    # Include in try/except block if you're also targeting Mac/Linux
    from PyQt5.QtWinExtras import QtWin
    myappid = 'Nuvoton.nuwriter.UiPyqt5.0120'
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass
        
class Ui(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self) # Call the inherited classes __init__ method

        self.setupUi(self)

        self.setWindowTitle("MA35D1 NuWriter")

        self.addMedia()

        self.text_browser = QtWidgets.QTextBrowser(self)
        self.verticalLayout.addWidget(self.text_browser)

        # Install the custom output stream
        self.outputStream = EmittingStream(textWritten=self.normalOutputWritten)
        sys.stdout = self.outputStream
        sys.stderr = self.outputStream

        self.initToolSetting()

        # Attach
        self.browseDDR_btn.clicked.connect(self.iniBrowseDDR)
        self.browseInfo_btn.clicked.connect(self.iniBrowseInfo)
        self.attach_btn.clicked.connect(self.doAttach)
       
        self.checkBox_a1.stateChanged.connect(self.checkBox_a_ChangedAction)          
        self.pushButton_a.clicked.connect(self.attachshow)
        self.checkBox_a_ChangedAction()
        
        # Convert    
        self.browseCCFG_btn.clicked.connect(self.iniBrowseCCFG)
        self.convert_btn.clicked.connect(self.doConvert)   

        self.pushButton_c.clicked.connect(self.CCFG_generate)        
        
        # Pack 
        self.browsePCFG_btn.clicked.connect(self.iniBrowsePCFG)
        self.pack_btn.clicked.connect(self.doPack) 
        
        self.pushButton_p.clicked.connect(self.PCFG_generate)
        if self.pcfgImgNumEdit.text() == "":
            self.pushButton_p.setEnabled(False)
        self.pcfgImgNumEdit.textChanged.connect(self.pcfgImgNumEdit_ChangedAction)               

        self.browseUPCFG_btn.clicked.connect(self.iniBrowseUPCFG)
        self.unpack_btn.clicked.connect(self.doUnpack) 
        
        self.threadpool = QThreadPool() 

        # develop/otp mode setting
        self.dev_mode = False
        self.otp_mode = False
        
        self.tabWidget.setTabVisible(1,self.dev_mode)
        self.tabWidget.setTabVisible(2,self.dev_mode)
        self.tabMedia.setTabVisible(0,self.dev_mode)
        self.tabMedia.setTabVisible(3,self.dev_mode)
        
        self.tabMedia.setTabVisible(5,self.otp_mode)
        
        # ToolBar setting         
        self.actionDev.triggered.connect(self.dev_mode_check)
        self.actionOTP.triggered.connect(self.otp_mode_check)
        
        self.actionLicense.triggered.connect(self.showLicense)
        self.actionAbout.triggered.connect(self.showManual)
    
    def dev_mode_check(self):
        self.dev_mode = not self.dev_mode
        
        self.tabWidget.setTabVisible(1,self.dev_mode)
        self.tabWidget.setTabVisible(2,self.dev_mode)
        self.tabMedia.setTabVisible(0,self.dev_mode)
        self.tabMedia.setTabVisible(3,self.dev_mode)
        
    def otp_mode_check(self):
        self.otp_mode = not self.otp_mode
        
        self.tabMedia.setTabVisible(5,self.otp_mode)

    def showLicense(self):
        reply = QtWidgets.QMessageBox.about(self,'License',' NuWriterGUI Version: 1.00 \n\n NuWriterGUI is based on pyQt5 ')
    
    def showManual(self):
        manual_path = "UM_EN_MA35D1_NuWriter.pdf"
        open_new(manual_path)
    
    def checkBox_a_ChangedAction(self):
        if self.checkBox_a1.isChecked():
            self.pushButton_a.setEnabled(True)
            self.InfoFileLineEdit.setEnabled(True)
            self.browseInfo_btn.setEnabled(True)            
        else:
            self.pushButton_a.setEnabled(False)
            self.InfoFileLineEdit.setEnabled(False)
            self.browseInfo_btn.setEnabled(False)
            
    def pcfgImgNumEdit_ChangedAction(self):
        if self.pcfgImgNumEdit.text() == "":
            self.pushButton_p.setEnabled(False)
        else:
            self.pushButton_p.setEnabled(True)
      
    def attachshow(self):        
        self.attachwindow = SetInfoPage(parent = self) 
        self.attachwindow.set_info_name(self.InfoFileLineEdit.text())        
        self.attachwindow.show() 

    def CCFG_generate(self):
        self.CCFG_generate_window = CCFG_MainPage()        
        self.CCFG_generate_window.show()   

    def PCFG_generate(self):
        self.PCFG_generate_window = PCFG_MainPage(int(self.pcfgImgNumEdit.text()))        
        self.PCFG_generate_window.show()  
        
    @QtCore.pyqtSlot()   
    def OTP_generate(self):
        self.OTP_generate_window = OtpPage()  
        self.OTP_generate_window.set_otp_name(self.otpPage.imgPathLine.text())                
        self.OTP_generate_window.show() 
        
    @QtCore.pyqtSlot()   
    def OTP_readback(self):
        self.OTP_generate_window = OtpPage() 
        self.OTP_generate_window.read_back_otp(self.otpPage.fileShow.text())
        self.OTP_generate_window.show()
        
    def addMedia(self):

        # DEV_DDR_SRAM = 0
        self.ddrPage = MediaPage(DEV_DDR_SRAM, self)
        self.tabMedia.addTab(self.ddrPage, "DDR/SRAM")

        # DEV_NAND = 1
        self.nandPage = MediaPage(DEV_NAND, self)
        self.tabMedia.addTab(self.nandPage, "NAND")

        # DEV_SD_EMMC = 2
        self.sdEmmcPage = MediaPage(DEV_SD_EMMC, self)
        self.tabMedia.addTab(self.sdEmmcPage, "SD/EMMC")

        # DEV_SPINOR = 3
        self.spiNorPage = MediaPage(DEV_SPINOR, self)
        self.tabMedia.addTab(self.spiNorPage, "SPI NOR")

        # DEV_SPINAND = 4
        self.spiNandPage = MediaPage(DEV_SPINAND, self)
        self.tabMedia.addTab(self.spiNandPage, "SPI NAND")

        # DEV_OTP = 6
        self.otpPage = MediaPage(DEV_OTP, self)
        self.tabMedia.addTab(self.otpPage, "OTP")

    def __del__(self):
        # Restore sys.stdout
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    ################################################################################################
    # 'MA35D1.ini'
    ################################################################################################

    def initToolSetting(self):

        self.iniFileName = 'MA35D1.ini'

        iniFileName = self.iniFileName

        # https://pyinstaller.readthedocs.io/en/stable/runtime-information.html
        if getattr(sys, 'frozen', False):
            # we are running in a bundle
            app_dir = os.path.dirname(os.path.abspath(sys.executable))
        else:
            # we are running in a normal Python environment
            app_dir = os.path.dirname(os.path.abspath(__file__))

        iniFilePath = os.path.join(app_dir, iniFileName)

        if not os.path.exists(iniFilePath):
            open(iniFilePath, 'w', encoding='utf-8')

        self.conf = ConfigParser()
        self.conf.read(iniFilePath, encoding='utf-8')

        self.iniFilePath = iniFilePath

        if not self.conf.has_section('Attach'):
            self.conf.add_section('Attach')

        self.ddrFileLineEdit.setText(self.conf.get('Attach', 'Ini File', fallback=''))
        self.InfoFileLineEdit.setText(self.conf.get('Attach', 'Info File', fallback=''))
        
        if not self.conf.has_section('Convert'):
            self.conf.add_section('Convert')

        self.ccfgFileLineEdit.setText(self.conf.get('Convert', 'Config File', fallback=''))
        
        if not self.conf.has_section('Pack'):
            self.conf.add_section('Pack')
        
        self.pcfgFileLineEdit.setText(self.conf.get('Pack', 'Config File', fallback=''))
        
        if not self.conf.has_section('Unpack'):
            self.conf.add_section('Unpack')

        self.upcfgFileLineEdit.setText(self.conf.get('Unpack', 'Config File', fallback=''))

        sections = ['DDR', 'NAND', 'SD', 'SPINOR', 'SPINAND', 'OTP', 'USBH']

        for section in sections:
            if not self.conf.has_section(section):
                self.conf.add_section(section)

            if section == 'DDR':
                page = self.ddrPage
            elif section == 'NAND':
                page = self.nandPage
            elif section == 'SD':
                page = self.sdEmmcPage
            elif section == 'SPINOR':
                page = self.spiNorPage
            elif section == 'SPINAND':
                page = self.spiNandPage
            elif section == 'OTP':
                page = self.otpPage
            else:
                #print(f'{section} is not supported yet')
                continue

            page.imgPathLine.setText(self.conf.get(section, 'write file', fallback=''))
            if section != 'OTP':
                page.imgAddress.setText(self.conf.get(section, 'write addr', fallback=''))

            try:
                page.radioPack.setChecked(self.conf.getboolean(section, 'write pack', fallback=False))
            except:

                if section != 'DDR' and section != 'OTP':
                    print(f'fail to set pack in {section}')

                pass

            option = self.conf.get(section, 'write option', fallback='')

            try:
                if option == "Verify":
                    page.verifyWrite.setChecked(True)
                elif option == "Raw":
                    page.rawWrite.setChecked(True)
                elif option == "Execute":
                    page.optExecute.setChecked(True)
                elif option != '' and option != 'None':
                    print(f'unknown optioin {option}')
            except:
                print(f'fail to set optioin {option} in {section}')
                pass

            page.fileSave.setText(self.conf.get(section, 'read file', fallback='')) 
            page.readEnd.setText(self.conf.get(section, 'read length', fallback=''))
            if section != 'OTP':
                page.readStart.setText(self.conf.get(section, 'read start', fallback=''))
                
            option = self.conf.get(section, 'read option', fallback='')

            try:
                if option == "WithBad":
                    page.readWithBad.setChecked(True)
                elif option != '' and option != 'None':
                    print(f'unknown optioin {option}')
            except:
                print(f'fail to set optioin {option} in {section}')
                pass

            if section == 'DDR':
                continue

            #if section == 'SD':
            #    page.reservedSize.setText(self.conf.get(section, 'storage size', fallback=''))
            #    page.optEject.setChecked(self.conf.get(section, 'storage option', fallback='') == 'Eject')
                
            if section == 'OTP' or section == 'SD':    
                continue
            else:
                page.eraseStart.setText(self.conf.get(section, 'erase start', fallback=''))
                page.eraseEnd.setText(self.conf.get(section, 'erase length', fallback=''))
                page.eraseAll.setChecked(self.conf.getboolean(section, 'erase all', fallback=False))

    # def closeEvent(self, evt):
    #     pass

    def normalOutputWritten(self, text):
        self.text_browser.insertPlainText(text)
        self.text_browser.moveCursor(QtGui.QTextCursor.End)

    def iniBrowseDDR(self):
        filename = ""
        # Fix for crash in X on Ubuntu 14.04
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(filter = "bin(*.bin)")
        if filename != "":
            self.ddrFileLineEdit.setText(filename)
            
    def iniBrowseInfo(self):
        filename = ""
        # Fix for crash in X on Ubuntu 14.04
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(filter = "json(*.json)")
        if filename != "":
            self.InfoFileLineEdit.setText(filename)
    
    def iniBrowseCCFG(self):
        filename = ""
        # Fix for crash in X on Ubuntu 14.04
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(filter = "json(*.json)")
        if filename != "":
            self.ccfgFileLineEdit.setText(filename)
            
    def iniBrowsePCFG(self):
        filename = ""
        # Fix for crash in X on Ubuntu 14.04
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(filter = "json(*.json)")
        if filename != "":
            self.pcfgFileLineEdit.setText(filename)
            
    def iniBrowseUPCFG(self):
        filename = ""
        # Fix for crash in X on Ubuntu 14.04
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(filter = "bin(*.bin)")
        if filename != "":
            self.upcfgFileLineEdit.setText(filename)
           

    ################################################################################################
    # command line
    ################################################################################################

    @QtCore.pyqtSlot()
    def doAttach(self):
        iniFile = self.ddrFileLineEdit.text()
        infoFile = self.InfoFileLineEdit.text()
        if iniFile == "":
            print(f'Ini File missing!')
            return
        
        option = OPT_NONE
        if self.checkBox_a1.isChecked():
            option = OPT_SETINFO
            
        self.conf.set('Attach', 'Ini File', iniFile)
        self.conf.set('Attach', 'Info File', infoFile)
        self.conf.write(open(self.iniFilePath, 'w', encoding='utf-8'))

        self.text_browser.clear()
        #print(f'do_attach({iniFile},{option})')

        worker = Worker(do_attach, iniFile, option)

        # Execute
        self.threadpool.start(worker)
        
    @QtCore.pyqtSlot()
    def doConvert(self):
        cfg_file = self.ccfgFileLineEdit.text()
        if cfg_file == "":
            print(f'Config File missing!')
            return
        
        option = OPT_NONE
            
        self.conf.set('Convert', 'Config File', cfg_file)
        self.conf.write(open(self.iniFilePath, 'w', encoding='utf-8'))

        self.text_browser.clear()
        #print(f'do_convert({cfg_file},{option})')

        worker = Worker(do_convert, cfg_file, option)

        # Execute
        self.threadpool.start(worker)
    
    @QtCore.pyqtSlot()
    def doPack(self):
        cfg_file = self.pcfgFileLineEdit.text()
        if cfg_file == "":
            print(f'Config File missing!')
            return
            
        self.conf.set('Pack', 'Config File', cfg_file)
        self.conf.write(open(self.iniFilePath, 'w', encoding='utf-8'))

        self.text_browser.clear()

        if self.checkBox_p1.isChecked():
            #print(f'do_stuff({cfg_file})')
            worker = Worker(do_stuff, cfg_file)
        else :
            #print(f'do_pack({cfg_file})')
            worker = Worker(do_pack, cfg_file)

        # Execute
        self.threadpool.start(worker)
    
    @QtCore.pyqtSlot()
    def doUnpack(self):
        cfg_file = self.upcfgFileLineEdit.text()
        if cfg_file == "":
            print(f'Config File missing!')
            return
            
        self.conf.set('Unpack', 'Config File', cfg_file)
        self.conf.write(open(self.iniFilePath, 'w', encoding='utf-8'))

        self.text_browser.clear()
        
        #print(f'do_unpack({cfg_file})')
        worker = Worker(do_unpack, cfg_file)

        # Execute
        self.threadpool.start(worker)
    
    # def do_img_read(media, start, out_file_name, length=0x1, option=OPT_NONE) -> None:
    @QtCore.pyqtSlot(int, str, str, str, int, bool)
    def doImgRead(self, media, startStr, fileStr, lengthStr, option, isall=False):
        
        if fileStr == "":
            print(f'Save File missing!')
            return
        
        if isall:
            start = 0
            length = 0
            if media == DEV_OTP:
                length = 352
                option |= 0x3fff00
        else:            
            try:
                start = int(startStr, 16) & 0xffffffff
            except:
                start = 0

            try:
                length = int(lengthStr, 16) & 0xffffffff
            except:
                length = 0x1    


        self.text_browser.clear()

        if media in [DEV_DDR_SRAM, DEV_NAND, DEV_SPINOR, DEV_SPINAND, DEV_OTP, DEV_SD_EMMC]:

            if media == DEV_DDR_SRAM:
                section = 'DDR'
            elif media == DEV_NAND:
                section = 'NAND'
            elif media == DEV_SPINOR:
                section = 'SPINOR'
            elif media == DEV_SPINAND:
                section = 'SPINAND'
            elif media == DEV_OTP:
                section = 'OTP'
            else:
                section = 'SD'

            self.conf.set(section, 'read file', fileStr)
            self.conf.set(section, 'read start', startStr)
            self.conf.set(section, 'read length', lengthStr)

            if option == OPT_NONE:
                self.conf.set(section, 'read option', "None")
            elif option == OPT_WITHBAD:
                self.conf.set(section, 'read option', "WithBad")

            if isall:
                self.conf.set(section, 'read all', 'true')
            else:
                self.conf.set(section, 'read all', 'false')

        self.conf.write(open(self.iniFilePath, 'w', encoding='utf-8'))

        #print(f'do_img_read({media}, {start}, {fileStr}, {length}, {option})')
        if media == DEV_OTP:
            worker = Worker(do_otp_read, media, 0, fileStr, length, option)
        else:
            worker = Worker(do_img_read, media, start, fileStr, length, option)
        # Execute
        self.threadpool.start(worker)

    # def do_img_program(media, start, image_file_name, option=OPT_NONE) -> None:
    @QtCore.pyqtSlot(int, str, str, int, bool)
    def doImgProgram(self, media, startStr, image_file_name, option, ispack=False):

        if image_file_name == "" and media == DEV_OTP:
            print(f'OTP File missing!')
            return
        elif image_file_name == "":
            print(f'Image File missing!')
            return 

        try:
            start = int(startStr, 16) & 0xffffffff
        except:
            start = 0 

        self.text_browser.clear()

        if media == DEV_DDR_SRAM:
            section = 'DDR'
            self.conf.set(section, 'write file', image_file_name)
            self.conf.set(section, 'write addr', startStr)
            if option == 0:
                self.conf.set(section, 'write option', "None")
            elif option == 2:
                self.conf.set(section, 'write option', "Execute")

        elif media in [DEV_NAND, DEV_SPINOR, DEV_SPINAND, DEV_SD_EMMC]:

            if media == DEV_NAND:
                section = 'NAND'
            elif media == DEV_SPINOR:
                section = 'SPINOR'
            elif media == DEV_SPINAND:
                section = 'SPINAND'
            else:
                section = 'SD'

            self.conf.set(section, 'write file', image_file_name)
            self.conf.set(section, 'write addr', startStr)

            if ispack:
                self.conf.set(section, 'write pack', 'true')
            else:
                self.conf.set(section, 'write pack', 'false')

        elif media == DEV_OTP:
            section = 'OTP'
            self.conf.set(section, 'write file', image_file_name)

        if option == OPT_NONE:
            self.conf.set(section, 'write option', "None")
        elif option == OPT_VERIFY:
            self.conf.set(section, 'write option', "Verify")
        elif option == OPT_RAW:
            self.conf.set(section, 'write option', "Raw")

        self.conf.write(open(self.iniFilePath, 'w', encoding='utf-8'))

        if media == DEV_OTP:
            # print(f'do_otp_program({image_file_name})')
            worker = Worker(do_otp_program, image_file_name)
        elif ispack:
            # print(f'do_pack_program({media}, {image_file_name}, {option})')
            worker = Worker(do_pack_program, media, image_file_name, option)
        else:
            # print(f'do_img_program({media}, {start}, {image_file_name}, {option})')
            worker = Worker(do_img_program, media, start, image_file_name, option)

        # Execute
        self.threadpool.start(worker)


    # def do_img_erase(media, start, length=0, option=OPT_NONE) -> None:
    @QtCore.pyqtSlot(int, str, str, int, bool)
    def doImgErase(self, media, startStr, lengthStr, option, isall=False):

        if isall:
            start = 0
            length = 0
        else:
            try:
                start = int(startStr, 16) & 0xffffffff
            except:
                start = 0

            try:
                length = int(lengthStr, 16) & 0xffffffff
            except:
                length = 0x1


        self.text_browser.clear()

        if media in [DEV_NAND, DEV_SPINOR, DEV_SPINAND, DEV_OTP, DEV_SD_EMMC]:

            if media == DEV_NAND:
                section = 'NAND'
            elif media == DEV_SPINOR:
                section = 'SPINOR'
            elif media == DEV_SPINAND:
                section = 'SPINAND'
            elif media == DEV_OTP:
                section = 'OTP'
            else:
                section = 'SD'

            self.conf.set(section, 'erase start', startStr)
            self.conf.set(section, 'erase length', lengthStr)

            if isall:
                self.conf.set(section, 'erase all', 'true')
            else:
                self.conf.set(section, 'erase all', 'false')
                
        self.conf.write(open(self.iniFilePath, 'w', encoding='utf-8'))

        # print(f'do_img_erase({media}, {start}, {length}, {option})')
        if media == DEV_OTP:
            worker = Worker(do_otp_erase, option)
        else:
            worker = Worker(do_img_erase, media, start, length, option)

        # Execute
        self.threadpool.start(worker)

    '''
    @QtCore.pyqtSlot(str, int)
    def doMsc(self, reserveStr, option):

        try:
            reserve = int(reserveStr, 0) & 0xffffffff
        except:
            reserve = 0

        self.text_browser.clear()

        section = 'SD'

        if option == OPT_EJECT:
            self.conf.set(section, 'storage option', "Eject")
            reserve = 0
        else:
            self.conf.set(section, 'storage option', "None")
            self.conf.set(section, 'storage size', reserveStr)


        self.conf.write(open(self.iniFilePath, 'w', encoding='utf-8'))

        media = DEV_SD_EMMC
        # print(f'do_msc({media}, {reserve}, {option})')

        worker = Worker(do_msc, media, reserve, option)

        # Execute
        self.threadpool.start(worker)
    '''
        
class Worker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):

        """Long-running task."""
        # from time import sleep
        # for i in range(5):
        #     sleep(1)
        #     print("Long-running task.")

        try:
            self.fn(*self.args, **self.kwargs)
        except SystemExit as e:
            print(f'SystemExit: {e}')
            pass
        except Exception as e:
            print(f'An Error occurred: {e}')
            pass
        except:
            print('except')
            pass

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    # tool icon
    app.setWindowIcon(QtGui.QIcon(':/icons/app.ico'))
    myapp = Ui()
    myapp.show()
    sys.exit(app.exec_())
