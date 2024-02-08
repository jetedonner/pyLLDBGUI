#!/usr/bin/env python
#disasm_ui.py

# ----------------------------------------------------------------------
# Be sure to add the python path that points to the LLDB shared library.
# On MacOSX csh, tcsh:
#   setenv PYTHONPATH /Developer/Library/PrivateFrameworks/LLDB.framework/Resources/Python
# On MacOSX sh, bash:
#   export PYTHONPATH=/Developer/Library/PrivateFrameworks/LLDB.framework/Resources/Python
# ----------------------------------------------------------------------

import lldb
from lldbutil import *
from inputHelper import FBInputHandler
import psutil
import os
import os.path
import sys
import sre_constants
import re
import binascii
import webbrowser
import ctypes
import time
import signal

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from ui.assemblerTextEdit import *
from ui.breakpointTableWidget import *
from ui.registerTreeView import *
from ui.historyLineEdit import *
from ui.statisticsTreeWidget import *
from ui.fileInfoTableWidget import *
from ui.fileStructureTreeView import *
                
from config import *
from dbgHelper import *

from PyQt6.QSwitch import *
from PyQt6.QHEXTextEditSplitter import *
from PyQt6.QConsoleTextEdit import *

import lldbHelper
from worker.targetWorker import *
from worker.attachWorker import *
from worker.registerWorker import *
from worker.execCommandWorker import *
from worker.loadSourceWorker import *

from ansi2html import Ansi2HTMLConverter

#from ctypes import *
#from struct import *
#from binascii import *

APP_NAME = "LLDB-GUI"
WINDOW_SIZE = 720

APP_VERSION = "v0.0.1"

def breakpointHandler(frame, bpno, err):
    print("MLIR debugger attaching...")
    print("IIIIIIIIINNNNNNNN CCCCAAQALLLLLLBBBAAACCKKKK")
    
class Pymobiledevice3GUIWindow(QMainWindow):
    """PyMobiledevice3GUI's main window (GUI or view)."""
    
    regTreeList = []
    
    def settings_click(self, s):
        print("Settings clicked")
        pass
        
    def githubURL_click(self, s):
        url = ConfigClass.githubURL
        webbrowser.open(url)
        
    def load_clicked(self, s):
        dialog = QFileDialog(None, "Select executable or library", "", "All Files (*.*)")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter("Executables (*.exe *.com *.bat *);;Libraries (*.dll *.so *.dylib)")
    
        if dialog.exec():
            filename = dialog.selectedFiles()[0]
            print(filename)
            self.start_workerLoadTarget(filename)
        else:
            return None
            
    def __init__(self):
        super().__init__()
        self.processNode = None
        self.setWindowTitle(APP_NAME + " " + APP_VERSION)
        self.setBaseSize(WINDOW_SIZE * 2, WINDOW_SIZE)
        self.setMinimumSize(WINDOW_SIZE * 2, WINDOW_SIZE + 72)

        self.toolbar = QToolBar('Main ToolBar')
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)
        self.toolbar.setIconSize(QSize(ConfigClass.toolbarIconSize, ConfigClass.toolbarIconSize))
        
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        self.progressbar = QProgressBar()
        self.progressbar.setMinimum(0)
        self.progressbar.setMaximum(100)
        self.progressbar.setValue(0)
        self.progressbar.setFixedWidth(100)
        # Add the progress bar to the status bar
        self.statusBar.addPermanentWidget(self.progressbar)
        
        # new menu item
        self.load_action = QAction(ConfigClass.iconBug, '&Load Target', self)
        self.load_action.setStatusTip('Load Target')
        self.load_action.setShortcut('Ctrl+L')
        self.load_action.triggered.connect(self.load_clicked)
        self.toolbar.addAction(self.load_action)
        
        self.resume_action = QAction(ConfigClass.iconPlay, '&Resume', self)
        self.resume_action.setStatusTip('Resume Debugging')
        self.resume_action.setShortcut('Ctrl+R')
        self.resume_action.triggered.connect(self.handle_resumeThread)
        self.toolbar.addAction(self.resume_action)
        
#       self.run_action = QAction(ConfigClass.iconPlay, '&Resume', self)
#       self.run_action.setStatusTip('Resume Debugging')
#       self.run_action.setShortcut('Ctrl+R')
#       self.run_action.triggered.connect(self.handle_runProcess)
#       self.toolbar.addAction(self.run_action)
        
        self.step_over_action = QAction(ConfigClass.iconStepOver, '&Step Over', self)
        self.step_over_action.setStatusTip('Step over')
        self.step_over_action.setShortcut('Ctrl+T')
        self.step_over_action.triggered.connect(self.handle_stepNext)
        self.toolbar.addAction(self.step_over_action)
        
        self.step_into_action = QAction(ConfigClass.iconStepInto, '&Step Into', self)
        self.step_into_action.setStatusTip('Step Into')
        self.step_into_action.setShortcut('Ctrl+I')
        self.step_into_action.triggered.connect(self.handle_stepInto)
        self.toolbar.addAction(self.step_into_action)
        
        self.step_out_action = QAction(ConfigClass.iconStepOut, '&Step Out', self)
        self.step_out_action.setStatusTip('Step out')
        self.step_out_action.setShortcut('Ctrl+O')
        self.step_out_action.triggered.connect(self.handle_stepOut)
        self.toolbar.addAction(self.step_out_action)
        
        self.settings_action = QAction(ConfigClass.iconSettings, '&Settings', self)
        self.settings_action.setStatusTip('Settings')
        self.settings_action.triggered.connect(self.settings_click)
        self.toolbar.addAction(self.settings_action)
        
        self.githubURL_action = QAction(ConfigClass.iconGithub, 'Github &repo', self)
        self.githubURL_action.setStatusTip('Github repo')
        self.githubURL_action.triggered.connect(self.githubURL_click)
        self.toolbar.addAction(self.githubURL_action)
        
        menu = self.menuBar()
        
        main_menu = QtWidgets.QMenu('pyLLDBGUI', menu)
        menu.addMenu(main_menu)
        
        main_menu.addAction(self.load_action)
        main_menu.addAction(self.githubURL_action)
        
        self.splitter = QSplitter()
        self.splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        
        self.layout = QVBoxLayout()
        
        self.txtMultiline = AssemblerTextEdit()
        self.txtMultiline.table.actionShowMemory.triggered.connect(self.handle_showMemory)
        self.txtMultiline.table.sigEnableBP.connect(self.handle_enableBP)
        self.txtMultiline.table.sigBPOn.connect(self.handle_BPOn)
        
        
        
        self.txtMultiline.setContentsMargins(0, 0, 0, 0)
        self.splitter.setContentsMargins(0, 0, 0, 0)
        
        self.tabWidgetTop = QTabWidget()
        self.tabWidgetTop.addTab(self.txtMultiline, "Debugger")
        
        self.treFile = FileStructureTreeWidget()
        self.treFile.actionShowMemoryFrom.triggered.connect(self.handle_showMemoryFileStructureFrom)
        self.treFile.actionShowMemoryTo.triggered.connect(self.handle_showMemoryFileStructureTo)
        
        self.txtSource = QConsoleTextEdit()
        self.txtSource.setReadOnly(True)
        self.txtSource.setFont(ConfigClass.font)
        self.txtSource.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tabWidgetSource = QWidget()
        self.tabWidgetSource.setLayout(QVBoxLayout())
        self.tabWidgetSource.layout().addWidget(self.txtSource)
        self.tabWidgetTop.addTab(self.tabWidgetSource, "Source code")
        
        self.tblFileInfos = FileInfosTableWidget()
        self.tabWidgetFileInfos = QWidget()
        self.tabWidgetFileInfos.setLayout(QVBoxLayout())
        self.tabWidgetFileInfos.layout().addWidget(self.tblFileInfos)
        self.tabWidgetTop.addTab(self.tabWidgetFileInfos, "File Infos")
        
        self.tabWidgetFile = QWidget()
        self.tabWidgetFile.setLayout(QVBoxLayout())
        self.tabWidgetFile.layout().addWidget(self.treFile)
        self.tabWidgetTop.addTab(self.tabWidgetFile, "File Structure")
        
        self.treStats = QStatisticsTreeWidget()
        self.tabWidgetStats = QWidget()
        self.tabWidgetStats.setLayout(QVBoxLayout())
        self.tabWidgetStats.layout().addWidget(self.treStats)
        self.tabWidgetTop.addTab(self.tabWidgetStats, "Statistics")
        
        self.splitter.addWidget(self.tabWidgetTop)
        
        self.tabWidget = QTabWidget()
        
        self.splitter.addWidget(self.tabWidget)
        
        self.tabRegister = QWidget()
        self.tabRegister.setLayout(QVBoxLayout())
        
        self.tabRegisters = QTabWidget()
        self.tabRegister.layout().addWidget(self.tabRegisters)
        self.tabWidget.addTab(self.tabRegister, "Registers")

        self.treThreads = QTreeWidget()
        self.treThreads.setFont(ConfigClass.font)
        self.treThreads.setHeaderLabels(['Num / ID', 'Hex ID', 'Process / Threads / Frames', 'PC', 'Lang (guess)'])
        self.treThreads.header().resizeSection(0, 128)
        self.treThreads.header().resizeSection(1, 128)
        self.treThreads.header().resizeSection(2, 512)
#       self.tabRegisters.addTab(tabDet, regType)
        
        self.tabThreads = QWidget()
        self.tabThreads.setLayout(QVBoxLayout())
        self.tabThreads.layout().addWidget(self.treThreads)
        self.tabWidget.addTab(self.tabThreads, "Threads/Frames")
        
        self.tblBPs = BreakpointsTableWidget(self)
        self.tabBPs = QWidget()
        self.tabBPs.setLayout(QVBoxLayout())
        self.tabBPs.layout().addWidget(self.tblBPs)
        self.tabWidget.addTab(self.tabBPs, "Breakpoints")
        
        self.tabModules = QWidget()
        self.tabModules.setLayout(QVBoxLayout())
        #       tabDet.layout().addWidget(treDet)
        self.tabWidget.addTab(self.tabModules, "Modules/Symbols")
        
        self.hxtMemory = QHEXTextEditSplitter()
        self.txtMemoryAddr = QLineEdit("0x100003f50")
        self.txtMemorySize = QLineEdit("0x100")
        self.hxtMemory.layoutTopPlaceholer.addWidget(QLabel("Address:"))
        self.hxtMemory.layoutTopPlaceholer.addWidget(self.txtMemoryAddr)
        self.hxtMemory.layoutTopPlaceholer.addWidget(QLabel("Size:"))
        self.hxtMemory.layoutTopPlaceholer.addWidget(self.txtMemorySize)
        self.cmdReadMemory = QPushButton("Read memory")
        self.cmdReadMemory.clicked.connect(self.readMemory_click)
        self.hxtMemory.layoutTopPlaceholer.addWidget(self.cmdReadMemory)
        self.hxtMemory.txtMultiline.setFont(ConfigClass.font)
        self.hxtMemory.txtMultilineHex.setFont(ConfigClass.font)
        self.hxtMemory.txtMultilineHex.hexGrouping = HexGrouping.TwoChars
        
        self.tabMemory = QWidget()
        self.tabMemory.setLayout(QVBoxLayout())
#       tabDet.layout().addWidget(treDet)
        self.tabMemory.layout().addWidget(self.hxtMemory)
        
        self.tabWidget.addTab(self.tabMemory, "Memory")
#       self.tabMemory.show()
        
        self.tabConsole = QWidget()
        self.tabConsole.setLayout(QVBoxLayout())
#       tabDet.layout().addWidget(treDet)
        self.tabWidget.addTab(self.tabConsole, "Console")
        
        self.layout.addWidget(self.splitter)
        
        self.wdgCmd = QWidget()
        self.wdgConsole = QWidget()
        self.layCmdParent = QVBoxLayout()
        self.layCmd = QHBoxLayout()
        self.wdgCmd.setLayout(self.layCmd)
        self.wdgConsole.setLayout(self.layCmdParent)
        
        self.lblCmd = QLabel("Command: ")
        self.lblCmd.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        
        self.txtCmd = HistoryLineEdit()
        self.txtCmd.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.txtCmd.setText("re read")
        self.txtCmd.returnPressed.connect(self.click_execCommand)
        
        self.swtAutoscroll = QSwitch("Autoscroll")
        self.swtAutoscroll.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.swtAutoscroll.setChecked(True)
        
        self.cmdExecuteCmd = QPushButton("Execute")
        self.cmdExecuteCmd.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.cmdExecuteCmd.clicked.connect(self.click_execCommand)
        
        self.cmdClear = QPushButton()
        self.cmdClear.setIcon(ConfigClass.iconBin)
        self.cmdClear.setToolTip("Clear the console log")
        self.cmdClear.setIconSize(QSize(16, 16))
        self.cmdClear.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.cmdClear.clicked.connect(self.clear_clicked)
        
        self.layCmd.addWidget(self.lblCmd)
        self.layCmd.addWidget(self.txtCmd)
        self.layCmd.addWidget(self.cmdExecuteCmd)
        self.layCmd.addWidget(self.swtAutoscroll)
        self.layCmd.addWidget(self.cmdClear)
        self.wdgCmd.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        
        
        self.txtConsole = QConsoleTextEdit()
        self.txtConsole.setReadOnly(True)
        self.txtConsole.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.txtConsole.setFont(ConfigClass.font)
        self.layCmdParent.addWidget(self.txtConsole)
        self.layCmdParent.addWidget(self.wdgCmd)
        
        self.tabConsole.layout().addWidget(self.wdgConsole)
        
        self.centralWidget = QWidget(self)
        self.centralWidget.setLayout(self.layout)        
        self.setCentralWidget(self.centralWidget)
        
        self.threadpool = QThreadPool()
        
        if lldbHelper.exec2Dbg is not None:
            self.start_workerLoadTarget(lldbHelper.exec2Dbg)
#           self.start_loadSourceWorker('/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/hello_world/hello_world_test.c')
        else:
            self.start_workerAttachTarget(123)
    
    def handle_BPOn(self, address, on):
        self.tblBPs.doBPOn(address, on)
        pass
        
    def handle_enableBP(self, address, enable):
        self.tblBPs.doEnableBP(address, enable)
        pass
    
    def handle_showMemoryFileStructureFrom(self):
        address = self.treFile.selectedItems()[0].text(1)
        size = int(self.treFile.selectedItems()[0].text(2), 16) - int(self.treFile.selectedItems()[0].text(1), 16)
        
        self.doReadMemory(address, size)
        
    def handle_showMemoryFileStructureTo(self):
        address = self.treFile.selectedItems()[0].text(2)
        self.doReadMemory(address)
        
    def handle_showMemory(self):
        address = self.txtMultiline.table.item(self.txtMultiline.table.selectedItems()[0].row(), 3).text()
        self.doReadMemory(address)
        
    def readMemory_click(self):
        try:
#           global debugger
            self.handle_readMemory(lldbHelper.debugger, int(self.txtMemoryAddr.text(), 16), int(self.txtMemorySize.text(), 16))
        except Exception as e:
            print(f"Error while reading memory from process: {e}")
    
    def doReadMemory(self, address, size = 0x100):
        self.tabWidget.setCurrentWidget(self.tabMemory)
        self.txtMemoryAddr.setText(address)
        self.txtMemorySize.setText(hex(size))
        try:
#           global debugger
            self.handle_readMemory(lldbHelper.debugger, int(self.txtMemoryAddr.text(), 16), int(self.txtMemorySize.text(), 16))
        except Exception as e:
            print(f"Error while reading memory from process: {e}")
        
    def clear_clicked(self):
        self.txtConsole.setText("")
        
    def click_execCommand(self):
        newCommand = self.txtCmd.text()
        
        if len(self.txtCmd.lstCommands) > 0:
            if self.txtCmd.lstCommands[len(self.txtCmd.lstCommands) - 1] != newCommand:
                self.txtCmd.lstCommands.append(newCommand)
                self.txtCmd.currCmd = len(self.txtCmd.lstCommands) - 1
        else:
            self.txtCmd.lstCommands.append(newCommand)
            self.txtCmd.currCmd = len(self.txtCmd.lstCommands) - 1
            
        self.start_execCommandWorker(newCommand)
        
    def start_execCommandWorker(self, command):
        workerExecCommand = ExecCommandWorker(command)
        workerExecCommand.signals.finished.connect(self.handle_commandFinished)
        
        self.threadpool.start(workerExecCommand)
    
    def handle_commandFinished(self, res):
#       print(res.Succeeded())
#       print(res.GetError())
#       if "\x1b[32m" in res.GetOutput():
#           print("KIM YOU ARE THE MAN!!!")
#       else:
#           print("KIM YOU NOT ARE THE MAN!!!")
            
        if res.Succeeded():
            self.txtConsole.appendEscapedText(res.GetOutput())
        else:
            self.txtConsole.appendEscapedText(f"{res.GetError()}")
        
        if self.swtAutoscroll.isChecked():
            self.sb = self.txtConsole.verticalScrollBar()
            self.sb.setValue(self.sb.maximum())
    
    def start_loadSourceWorker(self, sourceFile):
        self.interruptLoadSourceWorker = LoadSourceCodeReceiver()
        workerLoadSource = LoadSourceCodeWorker(lldbHelper.debugger, sourceFile, self.interruptLoadSourceWorker)
        workerLoadSource.signals.finished.connect(self.handle_loadSourceFinished)
        
        self.threadpool.start(workerLoadSource)
    
#   def extract_color_codes(self, text):
#       pattern = r"\[\d{1,}[m]"
#       matches = re.findall(pattern, text)
#       return matches
    
    def handle_loadSourceFinished(self, sourceCode):
        if sourceCode != "":
#           conv = Ansi2HTMLConverter()
#           ansi = "".join(sourceCode)
#           html = conv.convert(ansi)
#           html = html.replace("font-size: normal;", "font-size: small; font-weight: lighter; font-family: monospace;")
#   #       print(html)
#           log(html)
#           self.txtSource.setHtml(html)
            log(sourceCode)
            self.txtSource.setEscapedText(sourceCode) # 
        else:
            self.txtSource.setText("<Source code NOT available>")
        
#       lldbHelper.debugger.SetAsync(True)
#       self.apply_colors(sourceCode, self.txtSource)
#       pattern = r"\x1b\[1;3\d\m"
#       replacement = "\u001b[{}m"
#       
#       text = "[33mThis is red text\n[35mThis is blue text\n[0mThis is normal text"
#       colored_text = re.sub(pattern, replacement, text)
#       print(colored_text)
        
#       pattern = r"\[3\d{2}\m"
#       replacement = f"\x1b[{match[0]}m"
#       
#       text = "[31mThis is red text\n[32mThis is green text\n[33mThis is yellow text\n[34mThis is blue text\n[35mThis is magenta text\n[36mThis is cyan text\n[37mThis is white text\n[39mThis is normal text"
#       colored_text = re.sub(pattern, replacement, text)
#       print(colored_text)
        
#       pattern = r"\[\d{1,}[m]"
#       
#       text = "[33mThis is red text\n[35mThis is blue text\n[0mThis is normal text"
#       match = re.search(pattern, text)
#       
#       if match:
#           matched_color_code = match.group(1)
#           print(f"Matched color code: {matched_color_code}")
    
#   def apply_colors(self, text, qtextedit):
#       color_codes = self.extract_color_codes(text)
#       for color_code in color_codes:
#           print(f'color_code: {color_code}')
#           start_index = text.find(color_code)
#           end_index = start_index + len(color_code)
#           
#           print(f'start_index: {start_index}, end_index: {end_index}, len: {len(color_code)}')
#           # Get the color code value
#           color_value = color_code[1:-1]
#           
#           print(f'start_index: {start_index}, end_index: {end_index}, len: {len(color_code)}, color_value: {color_value}')
#           
#           # Convert the color value to a QColor object
#           color = QColor(int(color_value))
#           
#           # Set the text color for the matched range
##           qtextedit.setTextColor(color, start_index, end_index)
    
    
    def start_workerLoadTarget(self, target):
        
        self.setWindowTitle(APP_NAME + " " + APP_VERSION + " - " + os.path.basename(target))
        
        mach_header = lldbHelper.GetFileHeader(target)
            
        self.tblFileInfos.addRow("Magic", lldbHelper.MachoMagic.to_str(lldbHelper.MachoMagic.create_magic_value(mach_header.magic)), hex(mach_header.magic))
        self.tblFileInfos.addRow("CPU Type", lldbHelper.MachoCPUType.to_str(lldbHelper.MachoCPUType.create_cputype_value(mach_header.cputype)), hex(mach_header.cputype))
        self.tblFileInfos.addRow("CPU SubType", str(mach_header.cpusubtype), hex(mach_header.cpusubtype))
        self.tblFileInfos.addRow("File Type", lldbHelper.MachoFileType.to_str(lldbHelper.MachoFileType.create_filetype_value(mach_header.filetype)), hex(mach_header.filetype))
        self.tblFileInfos.addRow("Num CMDs", str(mach_header.ncmds), hex(mach_header.ncmds))
        self.tblFileInfos.addRow("Size CMDs", str(mach_header.sizeofcmds), hex(mach_header.sizeofcmds))
        self.tblFileInfos.addRow("Flags", lldbHelper.MachoFlag.to_str(lldbHelper.MachoFlag.create_flag_value(mach_header.flags)), hex(mach_header.flags))
                    
        self.updateStatusBar("Loading target '%s' ..." % target)
        
        self.txtMultiline.clear()
        self.regTreeList.clear()
        self.tabRegisters.clear()
        self.tblBPs.resetContent()
#       self.tblBPs.setRowCount(0)
        
        self.interruptLoadWorker = TargetLoadReceiver()
        
        self.workerLoadTarget = TargetLoadWorker(self, self.interruptLoadWorker, target)
        self.workerLoadTarget.signals.sendProgressUpdate.connect(self.handle_progressUpdate)
        self.workerLoadTarget.signals.finished.connect(self.handle_progressFinished)
        self.workerLoadTarget.signals.loadStats.connect(self.handle_loadStats)
        self.workerLoadTarget.signals.loadRegister.connect(self.handle_loadRegister)
        self.workerLoadTarget.signals.loadRegisterValue.connect(self.handle_loadRegisterValue)
        self.workerLoadTarget.signals.loadProcess.connect(self.handle_loadProcess)
        self.workerLoadTarget.signals.loadSections.connect(self.handle_loadSections)
        self.workerLoadTarget.signals.loadThread.connect(self.handle_loadThread)
        self.workerLoadTarget.signals.addInstructionNG.connect(self.handle_addInstructionNG)
        self.workerLoadTarget.signals.setTextColor.connect(self.handle_setTextColor)
        
        self.threadpool.start(self.workerLoadTarget)
        
    def start_workerAttachTarget(self, pid):
        print(f'Attaching to PID: {pid}')
        
        self.workerAttachTarget = AttachLoadWorker(self, int(pid)) #substring))
        self.workerAttachTarget.signals.sendProgressUpdate.connect(self.handle_progressUpdate)
        self.workerAttachTarget.signals.finished.connect(self.handle_progressFinished)
        self.workerAttachTarget.signals.loadStats.connect(self.handle_loadStats)
        self.workerAttachTarget.signals.loadRegister.connect(self.handle_loadRegister)
        self.workerAttachTarget.signals.loadRegisterValue.connect(self.handle_loadRegisterValue)
        self.workerAttachTarget.signals.loadProcess.connect(self.handle_loadProcess)
        self.workerAttachTarget.signals.loadSections.connect(self.handle_loadSections)
        self.workerAttachTarget.signals.loadThread.connect(self.handle_loadThread)
        self.workerAttachTarget.signals.addInstructionNG.connect(self.handle_addInstructionNG)
        self.workerAttachTarget.signals.setTextColor.connect(self.handle_setTextColor)
        
        self.threadpool.start(self.workerAttachTarget)
    
    def handle_loadSections(self, module):
        print('Number of sections: %d' % module.GetNumSections())
        for sec in module.section_iter():
            print(sec)
            print(sec.GetName())
            print(f'GetFileByteSize() == {hex(sec.GetFileByteSize())}')
            print(f'GetByteSize() == {hex(sec.GetByteSize())}')
            
            print(f'GetSectionType: {sec.GetSectionType()} / {lldbHelper.SectionTypeString(sec.GetSectionType())}')
            
#           for inin in dir(sec):
#               print(inin)
                
            sectionNode = QTreeWidgetItem(self.treFile, [sec.GetName(), str(hex(sec.GetFileAddress())), str(hex(sec.GetFileAddress() + sec.GetByteSize())), hex(sec.GetFileByteSize()) + " / " + hex(sec.GetByteSize()), lldbHelper.SectionTypeString(sec.GetSectionType()) + " (" + str(sec.GetSectionType()) + ")"])
#           for jete in dir(sec):
#               print(jete)
            INDENT = "\t"
            INDENT2 = "\t\t"
#           if sec.GetName() == "__TEXT":
            # Iterates the text section and prints each symbols within each sub-section.
#           for subsec2 in sec:
#               print(subsec2.GetName())
#               print(INDENT + repr(subsec2))
#               for sym in module.symbol_in_section_iter(subsec2):
#                   print(sym.GetName())
#                   print(INDENT2 + repr(sym))
#                   print(INDENT2 + 'symbol type: %s' % str(sym.GetType())) # symbol_type_to_str
                        
            for jete2 in range(sec.GetNumSubSections()):
                print(sec.GetSubSectionAtIndex(jete2).GetName())
                
                subSec = sec.GetSubSectionAtIndex(jete2)
                
                subSectionNode = QTreeWidgetItem(sectionNode, [subSec.GetName(), str(hex(subSec.GetFileAddress())), str(hex(subSec.GetFileAddress() + subSec.GetByteSize())), hex(subSec.GetFileByteSize()) + " / " + hex(subSec.GetByteSize()), lldbHelper.SectionTypeString(subSec.GetSectionType()) + " (" + str(subSec.GetSectionType()) + ")"])
                
                for sym in module.symbol_in_section_iter(subSec):
                    subSectionNode2 = QTreeWidgetItem(subSectionNode, [sym.GetName(), str(hex(sym.GetStartAddress().GetFileAddress())), str(hex(sym.GetEndAddress().GetFileAddress())), hex(sym.GetSize()), 'Symbol'])
                    print(dir(sym))
                    print(sym.GetName())
                    print(INDENT2 + repr(sym))
                    print(INDENT2 + 'symbol type: %s' % str(sym.GetType())) # symbol_type_to_str
        pass
        
    def handle_setTextColor(self, color = "black", lineNum = False):
        self.txtMultiline.setTextColor(color, lineNum)
        pass
        
    def handle_addInstructionNG(self, addr, instr, comment, data, addLineNum, newLine, bold, color, rip):
        if newLine:
            self.txtMultiline.appendAsmTextNG(addr, instr, comment, data.replace("                             ", "\t\t").replace("		            ", "\t\t\t").replace("		         ", "\t\t").replace("		      ", "\t\t").replace("			   ", "\t\t\t"), addLineNum, rip)
        else:
#           self.txtMultiline.insertText(txt, bold, color)
            pass
        
    def handle_loadStats(self, json_data):
        self.treStats.loadJSON(json_data)
        pass
        
    def handle_loadRegisterValue(self, regIdx, regName, regValue, regMemory):
        registerDetailNode = QTreeWidgetItem(self.regTreeList[regIdx], [regName, regValue, regMemory])
    
    def handle_loadThread(self, idx, thread):
        self.threadNode = QTreeWidgetItem(self.processNode, ["#" + str(idx) + " " + str(thread.GetThreadID()), "0x" + hex(thread.GetThreadID()) + "", thread.GetQueueName(), '', ''])
        
#       print(thread.GetNumFrames())
        for idx2 in range(thread.GetNumFrames()):
            frame = thread.GetFrameAtIndex(idx2)
#           print(dir(frame))
            frameNode = QTreeWidgetItem(self.threadNode, ["", "", "#" + str(frame.GetFrameID()) + " " + str(frame.GetPCAddress()), str(hex(frame.GetPC())), lldbHelper.GuessLanguage(frame)]) # + " " + str(thread.GetThreadID()) + " (0x" + hex(thread.GetThreadID()) + ")", thread.GetQueueName()])
            
        self.processNode.setExpanded(True)
        if self.threadNode:
            self.threadNode.setExpanded(True)
        pass
        
    def handle_loadProcess(self, process):
        self.treThreads.clear()
        self.processNode = QTreeWidgetItem(self.treThreads, ["#0 " + str(process.GetProcessID()), "0x" + hex(process.GetProcessID()) + "", process.GetTarget().GetExecutable().GetFilename(), '', ''])
        pass
    
    def handle_loadRegister(self, regType):
        tabDet = QWidget()
        treDet = RegisterTreeWidget()
        self.regTreeList.append(treDet)
        tabDet.setLayout(QVBoxLayout())
        tabDet.layout().addWidget(treDet)
        
        treDet.setFont(ConfigClass.font)
        treDet.setHeaderLabels(['Registername', 'Value', 'Memory'])
        treDet.header().resizeSection(0, 128)
        treDet.header().resizeSection(1, 256)
        self.tabRegisters.addTab(tabDet, regType)
        pass
        
    def handle_progressFinished(self):
#       t = Timer(1.0, self.resetProgress)
#       t.start() # after 30 seconds, "hello, world" will be printed
        print(f'GetNumBreakpoints() => {lldbHelper.target.GetNumBreakpoints()}')
        idx = 0
        for i in range(lldbHelper.target.GetNumBreakpoints()):
            idx += 1
#           print(dir(lldbHelper.target.GetBreakpointAtIndex(i)))
            bp_cur = lldbHelper.target.GetBreakpointAtIndex(i)
            print(bp_cur)
            for bl in bp_cur:
                # Make sure the name list has the remaining name:
                name_list = lldb.SBStringList()
                bp_cur.GetNames(name_list)
#               print(name_list)
#               print(len(name_list))
#               print(name_list.GetSize())
                num_names = name_list.GetSize()
#               self.assertEquals(
#                   num_names, 1, "Name list has %d items, expected 1." % (num_names)
#               )
        
                name = name_list.GetStringAtIndex(0)
#               self.assertEquals(
#                   name,
#                   other_bkpt_name,
#                   "Remaining name was: %s expected %s." % (name, other_bkpt_name),
#               )
#               print(dir(bl))
#               bp_cur = lldbHelper.target.GetBreakpointAtIndex(i)
#               print(bl)
#               print(dir(bl))
#               print(bl.GetQueueName())
#               print(get_description(bp_cur))
#               print(dir(get_description(bp_cur)))
                self.txtMultiline.table.toggleBPAtAddress(hex(bl.GetLoadAddress()), False)
#               self.tblBPs.resetContent()
                self.tblBPs.addRow(bp_cur.GetID(), idx, hex(bl.GetLoadAddress()), name, str(bp_cur.GetHitCount()), bp_cur.GetCondition())
#               print(f'LOADING BREAKPOINT AT ADDRESS: {hex(bl.GetLoadAddress())}')
                
                
#       print(f'get_caller_symbol: {get_caller_symbol(lldbHelper.thread)}')
#       print(f'get_function_names: {get_function_names(lldbHelper.thread)}')
#       print(f'get_symbol_names: {get_symbol_names(lldbHelper.thread)}')
#       print(f'get_pc_addresses: {get_pc_addresses(lldbHelper.thread)}')
#       print(f'get_filenames: {get_filenames(lldbHelper.thread)}')
#       print(f'get_line_numbers: {get_line_numbers(lldbHelper.thread)}')
#       print(f'get_module_names: {get_module_names(lldbHelper.thread)}')
#       print(f'get_stack_frames: {get_stack_frames(lldbHelper.thread)}')
        self.start_loadSourceWorker('/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/hello_world/hello_world_test.c')
        pass
        
    def updateProgress(self, newValue, finished = False):
        #       print(f"newValue: {newValue}")
        self.progressbar.setValue(int(newValue))
#       if finished:
#           self.handle_progressFinished()
#           #       self.progressbar.repaint()
#           
#   def resetProgress(self):
##       self.updateStatusBar("Ready ...")
#       self.updateProgress(0)
        
    def handle_progressUpdate(self, newProgress:int):
        self.updateProgress(newProgress)
        
    def updateStatusBar(self, msg):
        self.statusBar.showMessage(msg)
    
    def handle_readMemory(self, debugger, address, data_size = 0x100):
        error_ref = lldb.SBError()
        process = debugger.GetSelectedTarget().GetProcess()
        memory = process.ReadMemory(address, data_size, error_ref)
        if error_ref.Success():
#           hex_string = binascii.hexlify(memory)
            # `memory` is a regular byte string
#           print(f'BYTES:\n{memory}\nHEX:\n{hex_string}')
            self.hxtMemory.setTxtHexNG(memory, True, int(self.txtMemoryAddr.text(), 16))
        else:
            print(str(error_ref))
    
    def get_running_processes(self):
        # Get a list of all running processes
        processes = [proc.info for proc in psutil.process_iter(['pid', 'name', 'status'])]
        return processes
    
    def print_running_processes(self):
        processes = self.get_running_processes()
        
#       # Print process information
#       for processNG in processes:
#           print(f"PID: {processNG['pid']}, Name: {processNG['name']}, Status: {processNG['status']}")
    
    def handle_resumeThread(self):
        print("Trying to SIGINT ...")
        error = lldbHelper.process.Stop() #.Signal(signal.SIGBREAK)
        print("After SIGINT ...")
        if error:
            print(error)
#       self.run_action.setIcon(ConfigClass.iconPlay)
#       if lldbHelper.process.Continue():
#           self.updateStatusBar("Thread resumed ...")
        
    def handle_runProcess(self):
        self.run_action.setIcon(ConfigClass.iconPlay)
#       # Set the hourglass cursor
#       self.waitCursor = QCursor(Qt.CursorShape.WaitCursor)
#       QApplication.setOverrideCursor(self.waitCursor)
#       QApplication.changeOverrideCursor(self.waitCursor)
#
##       QApplication.restoreOverrideCursor()
##       QApplication.changeOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
#       
#       # Simulate some lengthy task
#       time.sleep(5)
##       
##       # Restore the default cursor
##       QApplication.setOverrideCursor(QCursor(Qt.CursorShape.ArrowCursor))
        
        processes = self.get_running_processes()

        # Create a QInputDialog to select a process name
        title = 'Select a running Process'
        label = 'Select the process you want to debug:'
        
        dialog = QInputDialog()
        dialog.setWindowTitle(title)
        dialog.setLabelText(label)
        
        my_list = []
        for processNG in processes:
            my_list.append(processNG["name"] + " - PID: " + str(processNG["pid"]) + "")
            
        dialog.textValueSelected.connect(self.handle_procSelected)
        # Set the possible choices to the list of process names
        dialog.setComboBoxItems(my_list)
        
        # Show the dialog and get the selected process name
        if dialog.exec():
            pass
        
#       if selected_daemon_process:
#           # Use QProcess to kill the selected process
#           process = QProcess()
#           process.start('kill -9 {}'.format(daemon_processes[selected_daemon_process]))
#           process.waitForFinished()

        
    def handle_procSelected(self, procName):
        print(procName)
        # Extract the substring using a regular expression
        regex = r"PID: (.*)"
        pattern = re.compile(regex)
        match = pattern.search(procName)
        
        if match:
            substring = match.group(1)
        else:
            substring = None
            
#       print(f'Attaching to PID: {substring}')
#       
#       self.workerAttachTarget = AttachLoadWorker(self, int(7300)) #substring))
#       self.workerAttachTarget.signals.sendProgressUpdate.connect(self.handle_progressUpdate)
#       self.workerAttachTarget.signals.finished.connect(self.handle_progressFinished)
#       self.workerAttachTarget.signals.loadStats.connect(self.handle_loadStats)
#       self.workerAttachTarget.signals.loadRegister.connect(self.handle_loadRegister)
#       self.workerAttachTarget.signals.loadRegisterValue.connect(self.handle_loadRegisterValue)
#       self.workerAttachTarget.signals.loadProcess.connect(self.handle_loadProcess)
#       self.workerAttachTarget.signals.loadSections.connect(self.handle_loadSections)
#       self.workerAttachTarget.signals.loadThread.connect(self.handle_loadThread)
#       self.workerAttachTarget.signals.addInstructionNG.connect(self.handle_addInstructionNG)
#       self.workerAttachTarget.signals.setTextColor.connect(self.handle_setTextColor)
#       
#       self.threadpool.start(self.workerAttachTarget)
        
    def handle_stepNext(self):
#       global thread
#       output_stream = thread.GetOutput()
        lldbHelper.thread.StepInstruction(True)
#       for line in output_stream.readlines():
#           print(f'>>>>>>> OUTPUT OF STEP: {line}')
        
        frame = lldbHelper.thread.GetFrameAtIndex(0)
        print(f'DEEEEEEBBBBBUUUUUGGGG: {lldbHelper.thread} / {lldbHelper.thread.GetNumFrames()} / {frame}')
        print(f'NEXT STEP {frame.register["rip"].value}')
        
        # Get the current instruction
#       instruction = frame
        print(f'NEXT INSTRUCTION {hex(frame.GetPC())}')
        self.txtMultiline.setPC(frame.GetPC())
        
#       self.regTreeList.clear()
        for reg in self.regTreeList:
            reg.clear()
        
        self.workerLoadRegister = RegisterLoadWorker(self, lldbHelper.target)
        self.workerLoadRegister.signals.loadRegister.connect(self.handle_loadRegister)
        self.workerLoadRegister.signals.loadRegisterValue.connect(self.handle_loadRegisterValue)
        
        self.threadpool.start(self.workerLoadRegister)
    
    def handle_stepInto(self):
#       global thread
        lldbHelper.process.Continue()
#       lldbHelper.thread.StepInstruction(False)
#       frame = lldbHelper.thread.GetFrameAtIndex(0)
#       print(f'NEXT STEP INTO {frame.register["rip"].value}')
        
#       function = frame.GetFunction()
#       # See if we have debug info (a function)
#       if function:
#           # We do have a function, print some info for the
#           # function
#           print(function)
#           
##                               for functionNG2 in dir(function):
##                                   print(functionNG2)
#           
#           # Now get all instructions for this function and print
#           # them
#           insts = function.GetInstructions(target)
#           self.txtMultiline.disassemble_instructions(insts, rip)
#       else:
#           # See if we have a symbol in the symbol table for where
#           # we stopped
#           symbol = frame.GetSymbol()
#           if symbol:
#               # We do have a symbol, print some info for the
#               # symbol
#               print(symbol)
#               
##                                   print(f'DisplayName: {symbol.GetName()}')
#               # Now get all instructions for this symbol and
#               # print them
#               insts = symbol.GetInstructions(target)
#               self.txtMultiline.disassemble_instructions(insts, rip)
#               
##                                   for functionNG2 in dir(symbol):
##   #                                   if functionNG2.startswith("__"):
##   #                                       continue
##                                       print(functionNG2)
                                    
        # Get the current instruction
#       instruction = frame
        print(f'NEXT INTO INSTRUCTION {hex(frame.GetPC())}')
        self.txtMultiline.setPC(frame.GetPC())
        
    def handle_stepOut(self):
        pass
        
def close_application():
#   global process
    # Stop all running tasks in the thread pool
    if lldbHelper.process:
        pymobiledevice3GUIWindow.interruptLoadWorker.interruptTargetLoadSignal.emit()
        QCoreApplication.processEvents()
        print("KILLING PROCESS")
        lldbHelper.process.Kill()
    else:
        print("NO PROCESS TO KILL!!!")
#   global pymobiledevice3GUIApp
#   pymobiledevice3GUIApp.quit()

#import sys

# Get the number of run arguments
num_args = len(sys.argv)
if num_args >= 2: #2 and sys.argv[i]:
    lldbHelper.exec2Dbg = sys.argv[1]
    pass

# Print the run arguments
#for i in range(1, num_args):
#   print(f"Argument {i}: {sys.argv[i]}")
    
#def main():
"""PyMobiledevice3GUI's main function."""
global pymobiledevice3GUIApp
pymobiledevice3GUIApp = QApplication([])
pymobiledevice3GUIApp.aboutToQuit.connect(close_application)
ConfigClass.initIcons()

# Set the app icon
#pymobiledevice3GUIApp.setWindowIcon(IconHelper.iconApp) #QIcon(icon))
pymobiledevice3GUIApp.setWindowIcon(ConfigClass.iconBPEnabled)
pymobiledevice3GUIWindow = Pymobiledevice3GUIWindow()
pymobiledevice3GUIWindow.show()
#PyMobiledevice3GUI(view=pymobiledevice3GUIWindow)
#pymobiledevice3GUIApp.setQuitOnLastWindowClosed(True)

sys.exit(pymobiledevice3GUIApp.exec())