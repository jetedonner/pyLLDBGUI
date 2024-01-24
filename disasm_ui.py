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
import os
import os.path
import sys
import re
import binascii
import webbrowser

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from assemblerTextEdit import *
from registerTreeView import *
from config import *

APP_NAME = "LLDB-GUI"
WINDOW_SIZE = 620

APP_VERSION = "v0.0.1"

fname = "main"
exe = "/Users/dave/Downloads/hello_world/hello_world_test"

global debugger
debugger = None

global process
process = None

global target
target = None

interruptExecCommand = False

        
class ExecCommandReceiver(QObject):
    interruptExecCommand = pyqtSignal()
    
class ExecCommandWorkerSignals(QObject):
    finished = pyqtSignal(object)
    
class ExecCommandWorker(QRunnable):
    
    def __init__(self, command):
        super(ExecCommandWorker, self).__init__()
        self.isExecCommandActive = False
        self.command = command
        self.signals = ExecCommandWorkerSignals()
        
    def run(self):
        self.runExecCommand()
        
    def runExecCommand(self):
        if self.isExecCommandActive:
            interruptExecCommand = True
            return
        else:
            interruptExecCommand = False
        QCoreApplication.processEvents()
        self.isExecCommandActive = True
        
        global debugger
        res = lldb.SBCommandReturnObject()
        
        # Get the command interpreter
        command_interpreter = debugger.GetCommandInterpreter()
        
        # Execute the 'frame variable' command
        command_interpreter.HandleCommand(self.command, res)
        print(f'{res}')
        for i in dir(res):
            print(i)
        print(res.Succeeded())
        print(res.GetError())
        
        self.isExecCommandActive = False
        self.signals.finished.emit(res)
        QCoreApplication.processEvents()
    
    def handle_interruptExecCommand(self):
#		print(f"Received interrupt in the sysLog worker thread")
#		self.isSysLogActive = False
        pass
        
interruptTargetLoad = False

class UserInputListener:
    def __init__(self, process, queue):
#       super(UserInputListener, self).__init__()
        self.process = process
        self.queue = queue
        
    def input_received(self, data):
        # Process user input data
        # Update the program state based on the input
        # Send commands to LLDB to continue execution or interact with the program
        self.queue.put(data)
        

class ProcessThreadObject(QObject):
    process = None
    threads = []
    
    def __init__(self, process):
        super(ProcessThreadObject, self).__init__()
        self.process = process
#       self.threads = threads
        
    def addThread(self, thread):
        self.threads.append(thread)

class TargetLoadReceiver(QObject):
    interruptTargetLoad = pyqtSignal()
    
class TargetLoadWorkerSignals(QObject):
    finished = pyqtSignal()
    sendProgressUpdate = pyqtSignal(int)
    loadRegister = pyqtSignal(str)
    loadRegisterValue = pyqtSignal(int, str, str, str)
    loadProcess = pyqtSignal(object)
    loadThread = pyqtSignal(int, object)
    addInstruction = pyqtSignal(str, bool, bool, bool, str)
    
    addInstructionNG = pyqtSignal(str, str, str, str, bool, bool, bool, str)
    
    setTextColor = pyqtSignal(str, bool)

class TargetLoadWorker(QRunnable):
    
    targetPath = "/Users/dave/Downloads/hello_world/hello_world_test"
    window = None
    inputHandler = None
    
    def inputCallback(self, data):
        print(data)
        
    def __init__(self, window_obj, target = "/Users/dave/Downloads/hello_world/hello_world_test"):
        super(TargetLoadWorker, self).__init__()
        self.isTargetLoadActive = False
        self.window = window_obj
        self.targetPath = target
        self.signals = TargetLoadWorkerSignals()
        
    def run(self):
        QCoreApplication.processEvents()
        self.runTargetLoad()
        
    def runTargetLoad(self):
        if self.isTargetLoadActive:
            interruptTargetLoad = True
            return
        else:
            interruptTargetLoad = False
        QCoreApplication.processEvents()
        self.isTargetLoadActive = True
        
        self.sendProgressUpdate(5)
        
        global debugger
        # Create a new debugger instance
        debugger = lldb.SBDebugger.Create()
        
        # When we step or continue, don't return from the function until the process
        # stops. We do this by setting the async mode to false.
        debugger.SetAsync(False)
        
        for i in dir(debugger):
            print(i)
#       {lldb.getVersion()}
        print(f"VEARSION: {sys.modules['lldb'].__file__} / {debugger.GetVersionString()}")
        
#       print(lldb)
        
        for i in dir(lldb):
            print(i)
#       self.inputHandler = FBInputHandler(debugger, self.inputCallback)
        
        print(f'debugger: {debugger}')
        # Create a target from a file and arch
        print("Creating a target for '%s'" % self.targetPath)
        
        global target
        target = debugger.CreateTargetWithFileAndArch(self.targetPath, None) # lldb.LLDB_ARCH_DEFAULT)
        
        if target:
            self.sendProgressUpdate(10)
            print("Has target")
            
            # If the target is valid set a breakpoint at main
            main_bp = target.BreakpointCreateByName(fname, target.GetExecutable().GetFilename())
            error = main_bp.SetScriptCallbackBody("\
            print 'Hit breakpoint callback'")
#           main_bp.SetScriptCallbackFunction('disasm_ui.breakpoint_cb')
#           main_bp.SetAutoContinue(auto_continue=True)
            print(main_bp)
            
            # Launch the process. Since we specified synchronous mode, we won't return
            # from this function until we hit the breakpoint at main
            global process
            process = target.LaunchSimple(None, None, os.getcwd())
#           process.Stop()
#           self.inputHandler.start()
            print(process)
            
            # Make sure the launch went ok
            if process:
                self.executeCmd()
                
                self.signals.loadProcess.emit(process)
                QCoreApplication.processEvents()
                self.sendProgressUpdate(15)
                print("Process launched OK")
                # Print some simple process info
                state = process.GetState()
                print(process)
                if state == lldb.eStateStopped:
                    print("state == lldb.eStateStopped")

                    print(f'GetNumThreads: {process.GetNumThreads()}')
                    # Get the first thread
                    for thrd in range(process.GetNumThreads()):
                        print(f'process.GetThreadAtIndex({thrd}) {process.GetThreadAtIndex(thrd).GetIndexID()}')
                    
                    idxThread = 0
                    thread = process.GetThreadAtIndex(0)
                    if thread:
                        
                        self.signals.loadThread.emit(idxThread, thread)
                        QCoreApplication.processEvents()
                        idxThread += 1
                        self.sendProgressUpdate(20)
                        # Print some simple thread info
                        print(thread)
                        print_stacktrace(thread)
                        print(f'GetNumFrames: {thread.GetNumFrames()}')
                        
                        for idx2 in range(thread.GetNumFrames()):
                            
                            # Get the first frame
                            frame = thread.GetFrameAtIndex(idx2)
                            if frame:
                                self.sendProgressUpdate(25)
                                # Print some simple frame info
                                print(frame)
                                
                                if idx2 == 0:
                                    function = frame.GetFunction()
                                    # See if we have debug info (a function)
                                    if function:
                                        # We do have a function, print some info for the
                                        # function
                                        print(function)
                                        
        #                               for functionNG2 in dir(function):
        #                                   print(functionNG2)
                                            
                                        # Now get all instructions for this function and print
                                        # them
                                        insts = function.GetInstructions(target)
                                        self.disassemble_instructions(insts)
                                    else:
                                        # See if we have a symbol in the symbol table for where
                                        # we stopped
                                        symbol = frame.GetSymbol()
                                        if symbol:
                                            # We do have a symbol, print some info for the
                                            # symbol
                                            print(symbol)
                                            
        #                                   print(f'DisplayName: {symbol.GetName()}')
                                            # Now get all instructions for this symbol and
                                            # print them
                                            insts = symbol.GetInstructions(target)
                                            self.disassemble_instructions(insts)
                                            
        #                                   for functionNG2 in dir(symbol):
        #   #                                   if functionNG2.startswith("__"):
        #   #                                       continue
        #                                       print(functionNG2)
                                                    
                                    registerList = frame.GetRegisters()
                                    print(
                                        "Frame registers (size of register set = %d):"
                                        % registerList.GetSize()
                                    )
                                    self.sendProgressUpdate(30)
                                    currReg = 0
                                    for value in registerList:
                                        # print value
                                        print(
                                            "%s (number of children = %d):"
                                            % (value.GetName(), value.GetNumChildren())
                                        )
                                        self.signals.loadRegister.emit(value.GetName())
        #                               continue
        #                               registerNode = QTreeWidgetItem(self.treRegister, [value.GetName() + " (" + str(value.GetNumChildren()) + ")", '', ''])
        #                               QTreeWidgetItem(self.treRegister, ['Floating point register', 'eax', '0x5'])
                                        for child in value:
        #                                   print(
        #                                       "Name: ", child.GetName(), " Value: ", child.GetValue()
        #                                   )
                                            
        #                                   variable_type = type(child.GetValue())
                                            
        #                                   print(f"The type of child.GetValue() is: {variable_type}")
                                            
                                            memoryValue = ""
                                            try:
                                                
                                                # Specify the memory address and size you want to read
                                                size = 32  # Adjust the size based on your data type (e.g., int, float)
                                                
                                                # Read memory and print the result
                                                data = self.read_memory(process, target.ResolveLoadAddress(int(child.GetValue(), 16)), size)
                                                
                                                hex_string = ''.join("%02x" % byte for byte in data)
                                                
                                                formatted_hex_string = ' '.join(re.findall(r'.{2}', hex_string))
                                                memoryValue = formatted_hex_string
        #                                       if data:
        #                                           print(f"Data at address {hex(address)}: {data}\n{formatted_hex_string}")
                                            except Exception as e:
        #                                       print(f"Error getting memory for addr: {e}")
                                                pass
                                                
                                            self.signals.loadRegisterValue.emit(currReg, child.GetName(), child.GetValue(), memoryValue)
                                            QCoreApplication.processEvents()
                                            
                                        currProg = (registerList.GetSize() - currReg)
                                        self.sendProgressUpdate(30 + (70 / currProg))
                                        currReg += 1
                            
            else:
                print("Process NOT launched!!!")
        else:
            print("Has NO target")
            
        self.isTargetLoadActive = False
#       self.treeWidget.setEnabled(True)
#       QCoreApplication.processEvents()
        self.signals.finished.emit()
        QCoreApplication.processEvents()
    
    def executeCmd(self):
        # This causes an error and the callback is never called.
        opt = lldb.SBExpressionOptions()
        opt.SetIgnoreBreakpoints(False)
        
        global target
        print("EXECUTING COMMAND:")
        # Execute the "re read" command
        result = target.EvaluateExpression("re read", opt)
        
        # Print the result
        print(result.GetSummary())
        
    def sendProgressUpdate(self, progress):
        self.signals.sendProgressUpdate.emit(int(progress))
        QCoreApplication.processEvents()
        
    def handle_interruptTargetLoad(self):
#		print(f"Received interrupt in the sysLog worker thread")
#		self.isSysLogActive = False
        pass
        
    def extract_address(self, string):
        pattern = r'\[0x([0-9a-fA-F]+)\]'
        
        # Use re.search to find the match
        match = re.search(pattern, string)
        
        if match:
            hex_value = match.group(1)
            return hex_value
        else:
            print("No hex value found in the string.")
            return ""

    def read_memory(self, process, address, size):
        error = lldb.SBError()
        target = process.GetTarget()
        
        # Read memory using ReadMemory function
        data = target.ReadMemory(address, size, error)
        
        if error.Success():
            return data
        else:
            print("Error reading memory:", error)
            return None
        
    def disassemble_instructions(self, insts):
        global target
        for i in insts:
            address = self.extract_address(f'{i}')
#           self.signals.addInstruction(.emit(f'0x{address}:\t{i.GetMnemonic(target)}\t{i.GetOperands(target)}', True, True, False, "black")
            self.signals.addInstructionNG.emit(f'0x{address}', f'{i.GetMnemonic(target)}\t{i.GetOperands(target)}', f'{i.GetComment(target)}', f'{i.GetData(target)}', True, True, False, "black")
            
            QCoreApplication.processEvents()
        
def breakpoint_cb(frame, bpno, err):
    print('>>> breakpoint callback')
    
class HistoryLineEdit(QLineEdit):
    
    lstCommands = []
    currCmd = 0
    
    def __init__(self):
        super().__init__()
        
    def keyPressEvent(self, event):
        
        if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            print("Up or down key pressed")
            if event.key() == Qt.Key.Key_Up:
                if self.currCmd > 0:
                    self.currCmd -= 1
                    if self.currCmd < len(self.lstCommands):
                        self.setText(self.lstCommands[self.currCmd])
            else:
                if self.currCmd < len(self.lstCommands) - 1:
                    self.currCmd += 1
                    self.setText(self.lstCommands[self.currCmd])
            event.accept()  # Prevent event from being passed to QLineEdit for default behavior
        else:
            super(HistoryLineEdit, self).keyPressEvent(event)
        
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
        
        run_action = QAction(QIcon(os.path.join("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/resources/", 'play.png')), '&Run', self)
        run_action.setStatusTip('Run Debugging')
        run_action.setShortcut('Ctrl+P')
#       new_action.triggered.connect(self.new_document)
#       file_menu.addAction(new_action)
        self.toolbar.addAction(run_action)
        
        step_over_action = QAction(QIcon(os.path.join("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/resources/", 'step_over_ng2.png')), '&Step Over', self)
        step_over_action.setStatusTip('Step over')
        step_over_action.setShortcut('Ctrl+T')
#       new_action.triggered.connect(self.new_document)
#       file_menu.addAction(new_action)
        self.toolbar.addAction(step_over_action)
        
        step_into_action = QAction(QIcon(os.path.join("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/resources/", 'step_into.png')), '&Step Into', self)
        step_into_action.setStatusTip('Step Into')
        step_into_action.setShortcut('Ctrl+I')
#       new_action.triggered.connect(self.new_document)
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
        self.treThreads.setHeaderLabels(['Process / Threads', 'Hex ID', 'Frames'])
        self.treThreads.header().resizeSection(0, 128)
        self.treThreads.header().resizeSection(1, 128)
#       self.tabRegisters.addTab(tabDet, regType)
        
        self.tabThreads = QWidget()
        self.tabThreads.setLayout(QVBoxLayout())
        self.tabThreads.layout().addWidget(self.treThreads)
        self.tabWidget.addTab(self.tabThreads, "Threads")
        
        self.tabFrames = QWidget()
        self.tabFrames.setLayout(QVBoxLayout())
#       tabDet.layout().addWidget(treDet)
        self.tabWidget.addTab(self.tabFrames, "Frames")
        
        self.tabMemory = QWidget()
        self.tabMemory.setLayout(QVBoxLayout())
#       tabDet.layout().addWidget(treDet)
        self.tabWidget.addTab(self.tabMemory, "Memory")
        
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
        
        self.cmdExecuteCmd = QPushButton("Execute")
        self.cmdExecuteCmd.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.cmdExecuteCmd.clicked.connect(self.click_execCommand)
        
        self.layCmd.addWidget(self.lblCmd)
        self.layCmd.addWidget(self.txtCmd)
        self.layCmd.addWidget(self.cmdExecuteCmd)
        
        self.txtConsole = QTextEdit()
        self.txtConsole.setReadOnly(True)
        self.txtConsole.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.txtConsole.setFont(ConfigClass.font)
        self.layCmdParent.addWidget(self.txtConsole)
        self.layCmdParent.addWidget(self.wdgCmd)
        
        self.tabConsole.layout().addWidget(self.wdgConsole)
        
        centralWidget = QWidget(self)
        centralWidget.setLayout(self.layout)
        
        self.setCentralWidget(centralWidget)
        
        self.threadpool = QThreadPool()
        
        self.start_workerLoadTarget(exe)
    
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
        self.txtConsole.append(res.GetOutput())
    
    def start_workerLoadTarget(self, target):
        
        self.setWindowTitle(APP_NAME + " " + APP_VERSION + " - " + os.path.basename(target))
        
        self.updateStatusBar("Loading target '%s' ..." % target)
        
        self.txtMultiline.clear()
        self.regTreeList.clear()
        self.tabRegisters.clear()
        
        workerLoadTarget = TargetLoadWorker(self, target)
        workerLoadTarget.signals.sendProgressUpdate.connect(self.handle_progressUpdate)
        workerLoadTarget.signals.finished.connect(self.handle_progressFinished)
        workerLoadTarget.signals.loadRegister.connect(self.handle_loadRegister)
        workerLoadTarget.signals.loadRegisterValue.connect(self.handle_loadRegisterValue)
        workerLoadTarget.signals.loadProcess.connect(self.handle_loadProcess)
        workerLoadTarget.signals.loadThread.connect(self.handle_loadThread)
        workerLoadTarget.signals.addInstructionNG.connect(self.handle_addInstructionNG)
        workerLoadTarget.signals.setTextColor.connect(self.handle_setTextColor)
        
        self.threadpool.start(workerLoadTarget)
    
    def handle_setTextColor(self, color = "black", lineNum = False):
        self.txtMultiline.setTextColor(color, lineNum)
        pass
        
    def handle_addInstructionNG(self, addr, instr, comment, data, addLineNum, newLine, bold, color):
        if newLine:
            self.txtMultiline.appendAsmTextNG(addr, instr, comment, data.replace("                             ", "\t\t").replace("		            ", "\t\t\t").replace("		         ", "\t\t").replace("		      ", "\t\t").replace("			   ", "\t\t\t"), addLineNum)
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
            print(dir(frame))
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
        
def close_application():
    global process
    # Stop all running tasks in the thread pool
    if process:
        print("KILLING PROCESS")
        process.Kill()
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