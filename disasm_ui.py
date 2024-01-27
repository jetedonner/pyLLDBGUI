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
from lldbutil import print_stacktrace
from inputHelper import FBInputHandler
import psutil
import os
import os.path
import sys
import re
import binascii
import webbrowser
import ctypes
import time

#import time
#from gi.repository import Gdk, Gtk, GObject

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from assemblerTextEdit import *
from registerTreeView import *
from config import *

from PyQt6.QSwitch import *
from PyQt6.QHEXTextEditSplitter import *

import lldbHelper
from targetWorker import *
from execCommandWorker import *
from historyLineEdit import *

APP_NAME = "LLDB-GUI"
WINDOW_SIZE = 620

APP_VERSION = "v0.0.1"

fname = "main"
exe = "/Users/dave/Downloads/hello_world/hello_world_test"

#global debugger
#debugger = None

global process
process = None

global target
target = None

global thread
thread = None

#interruptExecCommand = False

        
#class ExecCommandReceiver(QObject):
#   interruptExecCommand = pyqtSignal()
#   
#class ExecCommandWorkerSignals(QObject):
#   finished = pyqtSignal(object)
#   
#class ExecCommandWorker(QRunnable):
#   
#   def __init__(self, command):
#       super(ExecCommandWorker, self).__init__()
#       self.isExecCommandActive = False
#       self.command = command
#       self.signals = ExecCommandWorkerSignals()
#       
#   def run(self):
#       self.runExecCommand()
#       
#   def runExecCommand(self):
#       if self.isExecCommandActive:
#           interruptExecCommand = True
#           return
#       else:
#           interruptExecCommand = False
#       QCoreApplication.processEvents()
#       self.isExecCommandActive = True
#       
#       global debugger
#       res = lldb.SBCommandReturnObject()
#       
#       
#       # Get the command interpreter
#       command_interpreter = pymobiledevice3GUIWindow.workerLoadTarget.debugger.GetCommandInterpreter()
#       
#       # Execute the 'frame variable' command
#       command_interpreter.HandleCommand(self.command, res)
##       print(f'{res}')
##       for i in dir(res):
##           print(i)
##       print(res.Succeeded())
##       print(res.GetError())
#       
#       self.isExecCommandActive = False
#       self.signals.finished.emit(res)
#       QCoreApplication.processEvents()
#   
#   def handle_interruptExecCommand(self):
##		print(f"Received interrupt in the sysLog worker thread")
##		self.isSysLogActive = False
#       pass
        
#interruptTargetLoad = False
    
        
class Pymobiledevice3GUIWindow(QMainWindow):
    """PyMobiledevice3GUI's main window (GUI or view)."""
    
    regTreeList = []
    
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
        self.setMinimumSize(WINDOW_SIZE * 2, WINDOW_SIZE)

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
        load_action = QAction(QIcon(os.path.join("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/resources/", 'bug.png')), '&Load Target', self)
        load_action.setStatusTip('Load Target')
        load_action.setShortcut('Ctrl+L')
        load_action.triggered.connect(self.load_clicked)
        
#       file_menu.addAction(new_action)
        self.toolbar.addAction(load_action)
        
#       self.run_action.setIcon(ConfigClass.iconPause)
        
        self.run_action = QAction(ConfigClass.iconPause, '&Run', self)
        self.run_action.setStatusTip('Run Debugging')
        self.run_action.setShortcut('Ctrl+P')
        self.run_action.triggered.connect(self.handle_runProcess)
#       file_menu.addAction(new_action)
        self.toolbar.addAction(self.run_action)
        
        step_over_action = QAction(QIcon(os.path.join("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/resources/", 'step_over_ng2.png')), '&Step Over', self)
        step_over_action.setStatusTip('Step over')
        step_over_action.setShortcut('Ctrl+T')
        step_over_action.triggered.connect(self.handle_stepNext)
#       file_menu.addAction(new_action)
        self.toolbar.addAction(step_over_action)
        
        step_into_action = QAction(QIcon(os.path.join("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/resources/", 'step_into.png')), '&Step Into', self)
        step_into_action.setStatusTip('Step Into')
        step_into_action.setShortcut('Ctrl+I')
        step_into_action.triggered.connect(self.handle_stepInto)
#       file_menu.addAction(new_action)
        self.toolbar.addAction(step_into_action)
        
        step_out_action = QAction(QIcon(os.path.join("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/resources/", 'step_out_ng.png')), '&Step Out', self)
        step_out_action.setStatusTip('Step out')
        step_out_action.setShortcut('Ctrl+O')
#       new_action.triggered.connect(self.new_document)
#       file_menu.addAction(new_action)
        self.toolbar.addAction(step_out_action)
        
        githubURL_action = QAction(QIcon(os.path.join("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/resources/", 'github.png')), 'Github &repo', self)
        githubURL_action.setStatusTip('Github repo')
        githubURL_action.triggered.connect(self.githubURL_click)
        self.toolbar.addAction(githubURL_action)
        
        menu = self.menuBar()
        
        main_menu = QtWidgets.QMenu('pyLLDBGUI', menu)
        menu.addMenu(main_menu)
        
        main_menu.addAction(load_action)
        main_menu.addAction(githubURL_action)
        
        self.splitter = QSplitter()
        self.splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        
        self.layout = QVBoxLayout()
        
        self.txtMultiline = AssemblerTextEdit()
        self.txtMultiline.table.actionShowMemory.triggered.connect(self.handle_showMemory)
        
        self.txtMultiline.setContentsMargins(0, 0, 0, 0)
        self.splitter.setContentsMargins(0, 0, 0, 0)
        
        self.splitter.addWidget(self.txtMultiline)
        
        self.tabWidget = QTabWidget()
        
        self.splitter.addWidget(self.tabWidget)
        
        self.tabRegister = QWidget()
        self.tabRegister.setLayout(QVBoxLayout())
        
        self.tabRegisters = QTabWidget()
        self.tabRegister.layout().addWidget(self.tabRegisters)
        self.tabWidget.addTab(self.tabRegister, "Registers")

        self.treThreads = QTreeWidget()
        self.treThreads.setFont(ConfigClass.font)
        self.treThreads.setHeaderLabels(['Num / ID', 'Hex ID', 'Process / Threads / Frames'])
        self.treThreads.header().resizeSection(0, 128)
        self.treThreads.header().resizeSection(1, 128)
#       self.tabRegisters.addTab(tabDet, regType)
        
        self.tabThreads = QWidget()
        self.tabThreads.setLayout(QVBoxLayout())
        self.tabThreads.layout().addWidget(self.treThreads)
        self.tabWidget.addTab(self.tabThreads, "Threads")
        
        self.tblBPs = BreakpointsTableWidget()
        self.tabBPs = QWidget()
        self.tabBPs.setLayout(QVBoxLayout())
        self.tabBPs.layout().addWidget(self.tblBPs)
        self.tabWidget.addTab(self.tabBPs, "Breakpoints")
        
#       self.tabFrames = QWidget()
#       self.tabFrames.setLayout(QVBoxLayout())
##       tabDet.layout().addWidget(treDet)
#       self.tabWidget.addTab(self.tabFrames, "Frames")
        
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
        
        
        self.txtConsole = QTextEdit()
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
        
        self.start_workerLoadTarget(exe)
    
    def handle_showMemory(self):
        self.tabWidget.setCurrentWidget(self.tabMemory)
        print(self.txtMultiline.table.item(self.txtMultiline.table.selectedItems()[0].row(), 3).text())
        self.txtMemoryAddr.setText(self.txtMultiline.table.item(self.txtMultiline.table.selectedItems()[0].row(), 3).text())
        
    def readMemory_click(self):
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
        if res.Succeeded():
            self.txtConsole.append(res.GetOutput())
        else:
            self.txtConsole.append(f"{res.GetError()}")
        
        if self.swtAutoscroll.isChecked():
            self.sb = self.txtConsole.verticalScrollBar()
            self.sb.setValue(self.sb.maximum())
    
    def start_workerLoadTarget(self, target):
        
        self.setWindowTitle(APP_NAME + " " + APP_VERSION + " - " + os.path.basename(target))
        
        self.updateStatusBar("Loading target '%s' ..." % target)
        
        self.txtMultiline.clear()
        self.regTreeList.clear()
        self.tabRegisters.clear()
        
        self.workerLoadTarget = TargetLoadWorker(self, target)
        self.workerLoadTarget.signals.sendProgressUpdate.connect(self.handle_progressUpdate)
        self.workerLoadTarget.signals.finished.connect(self.handle_progressFinished)
        self.workerLoadTarget.signals.loadRegister.connect(self.handle_loadRegister)
        self.workerLoadTarget.signals.loadRegisterValue.connect(self.handle_loadRegisterValue)
        self.workerLoadTarget.signals.loadProcess.connect(self.handle_loadProcess)
        self.workerLoadTarget.signals.loadThread.connect(self.handle_loadThread)
        self.workerLoadTarget.signals.addInstructionNG.connect(self.handle_addInstructionNG)
        self.workerLoadTarget.signals.setTextColor.connect(self.handle_setTextColor)
        
        self.threadpool.start(self.workerLoadTarget)
    
    def handle_setTextColor(self, color = "black", lineNum = False):
        self.txtMultiline.setTextColor(color, lineNum)
        pass
        
    def handle_addInstructionNG(self, addr, instr, comment, data, addLineNum, newLine, bold, color, rip):
        if newLine:
            self.txtMultiline.appendAsmTextNG(addr, instr, comment, data.replace("                             ", "\t\t").replace("		            ", "\t\t\t").replace("		         ", "\t\t").replace("		      ", "\t\t").replace("			   ", "\t\t\t"), addLineNum, rip)
        else:
#           self.txtMultiline.insertText(txt, bold, color)
            pass
        
    def handle_loadRegisterValue(self, regIdx, regName, regValue, regMemory):
        registerDetailNode = QTreeWidgetItem(self.regTreeList[regIdx], [regName, regValue, regMemory])
    
    def handle_loadThread(self, idx, thread):
        self.threadNode = QTreeWidgetItem(self.processNode, ["#" + str(idx) + " " + str(thread.GetThreadID()), "0x" + hex(thread.GetThreadID()) + "", thread.GetQueueName()])
        
#       print(thread.GetNumFrames())
        for idx2 in range(thread.GetNumFrames()):
            frame = thread.GetFrameAtIndex(idx2)
#           print(dir(frame))
            frameNode = QTreeWidgetItem(self.threadNode, ["", "", "#" + str(frame.GetFrameID()) + " " + str(frame.GetPCAddress())]) # + " " + str(thread.GetThreadID()) + " (0x" + hex(thread.GetThreadID()) + ")", thread.GetQueueName()])
            
        self.processNode.setExpanded(True)
        if self.threadNode:
            self.threadNode.setExpanded(True)
        pass
        
    def handle_loadProcess(self, process):
        self.treThreads.clear()
        self.processNode = QTreeWidgetItem(self.treThreads, ["#0 " + str(process.GetProcessID()), "0x" + hex(process.GetProcessID()) + "", process.GetTarget().GetExecutable().GetFilename()])
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
            hex_string = binascii.hexlify(memory)
            # `memory` is a regular byte string
            print(f'BYTES:\n{memory}\nHEX:\n{hex_string}')
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
            
        print(substring)
        
    def handle_stepNext(self):
#       global thread
#       output_stream = thread.GetOutput()
        self.workerLoadTarget.thread.StepInstruction(True)
#       for line in output_stream.readlines():
#           print(f'>>>>>>> OUTPUT OF STEP: {line}')
            
        frame = thread.GetFrameAtIndex(0)
        print(f'NEXT STEP {frame.register["rip"].value}')
        
        # Get the current instruction
#       instruction = frame
        print(f'NEXT INSTRUCTION {hex(frame.GetPC())}')
        self.txtMultiline.setPC(frame.GetPC())
    
    def handle_stepInto(self):
        global thread
        thread.StepInstruction(False)
        frame = thread.GetFrameAtIndex(0)
        print(f'NEXT STEP INTO {frame.register["rip"].value}')
        
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
        
    
    
        
def close_application():
#   global process
    # Stop all running tasks in the thread pool
    if pymobiledevice3GUIWindow.workerLoadTarget.process:
        print("KILLING PROCESS")
        pymobiledevice3GUIWindow.workerLoadTarget.process.Kill()
    else:
        print("NO PROCESS TO KILL!!!")
#   global pymobiledevice3GUIApp
#   pymobiledevice3GUIApp.quit()
    
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