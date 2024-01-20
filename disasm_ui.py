#!/usr/bin/env python

# ----------------------------------------------------------------------
# Be sure to add the python path that points to the LLDB shared library.
# On MacOSX csh, tcsh:
#   setenv PYTHONPATH /Developer/Library/PrivateFrameworks/LLDB.framework/Resources/Python
# On MacOSX sh, bash:
#   export PYTHONPATH=/Developer/Library/PrivateFrameworks/LLDB.framework/Resources/Python
# ----------------------------------------------------------------------

import lldb
import os
import sys
import re

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

APP_NAME = "LLDB-GUI"
WINDOW_SIZE = 620
#DISPLAY_HEIGHT = 35
#BUTTON_SIZE = 40

APP_VERSION = "v0.0.1"

fname = "main"
exe = "/Users/dave/Downloads/hello_world/hello_world_test"
global process
process = None

global target
target = None

#def disassemble_instructions(insts):
#   for i in insts:
#       print(i)

class AssemblerTextEdit(QWidget):
    
    lineCount = 0
    
    def setAsmText(self, txt):
        self.txtCode.append(txt)
        self.txtLineCount.append(str(self.lineCount) + ":")
        self.lineCount += 1
        
    def __init__(self):
        super().__init__()
        
        self.setLayout(QHBoxLayout())
        
        self.txtLineCount = QTextEdit()
        self.txtLineCount.setFixedWidth(70)
#       self.lineCount.setContentsMargins(0)
#       self.lineCount.setTextBackgroundColor(QColor("lightgray"))
        self.txtLineCount.setTextColor(QColor("black"))
        self.txtLineCount.setStyleSheet("background-color: rgb(200, 200, 200); padding-left:0; padding-top:0; padding-bottom:0; padding-right:0; margin-left:0px; margin-right:0px;")
        self.txtLineCount.setReadOnly(True)
#       self.layout().addWidget(self.lineCount)
        
        self.txtCode = QTextEdit()
        self.txtCode.setTextColor(QColor("black"))
        self.txtCode.setStyleSheet("background-color: rgb(200, 200, 200); padding-left:0; padding-top:0; padding-bottom:0; padding-right:0; margin-left:0px; margin-right:0px;")
        self.txtCode.setReadOnly(True)
#       self.layout().addWidget(self.txtCode)
        self.txtLineCount.verticalScrollBar().setVisible(False)
        self.txtLineCount.verticalScrollBar().hide()
        self.txtLineCount.horizontalScrollBar().setVisible(False)
        self.txtLineCount.horizontalScrollBar().hide()
        
        self.txtLineCount.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.txtLineCount.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.txtLineCount.horizontalScrollBar().valueChanged.connect(
            self.txtCode.horizontalScrollBar().setValue)
        self.txtLineCount.verticalScrollBar().valueChanged.connect(
            self.txtCode.verticalScrollBar().setValue)
        self.txtCode.horizontalScrollBar().valueChanged.connect(
            self.txtLineCount.horizontalScrollBar().setValue)
        self.txtCode.verticalScrollBar().valueChanged.connect(
            self.txtLineCount.verticalScrollBar().setValue)
        
        self.frame = QFrame()
        
        self.vlayout = QHBoxLayout()
        self.frame.setLayout(self.vlayout)
        
        self.vlayout.addWidget(self.txtLineCount)
        self.vlayout.addWidget(self.txtCode)
        self.vlayout.setSpacing(0)
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        
        self.frame.setFrameShape(QFrame.Shape.NoFrame)
        self.frame.setFrameStyle(QFrame.Shape.NoFrame)
        self.frame.setContentsMargins(0, 0, 0, 0)
#       self.frame.spac
        # .setSpacing(0)
        
        self.widget = QWidget()
        self.layFrame = QHBoxLayout()
        self.layFrame.addWidget(self.frame)
        self.widget.setLayout(self.layFrame)
        
        self.layout().addWidget(self.widget)
        
class CustomTextEdit(QTextEdit):
    
    def __init__(self):
        super().__init__()
        
        self.cursorPositionChanged.connect(self.updateLineNumberArea)
#       self.setWordWrapMode(Qt) # .setWordWrapMode(QTextEdit.WordWrapMode.NoWrap)
        self.highlightCurrentLine()
        
        self.lineNumberArea = QWidget(self)
        self.lineNumberArea.setGeometry(QRect(0, 0, self.width(), 20))
        self.lineNumberArea.setObjectName("lineNumberArea")
#       self.lineNumberArea.setAlignment(Qt.AlignRight)
        
        self.updateLineNumberAreaWidth()
#       self.connect(self, &QTextEdit::cursorPositionChanged, self.updateLineNumberArea)
#       self.connect(self, &QTextEdit::updateRequest, self.updateLineNumberArea)
        
    def paintEvent(self, event):
        super().paintEvent(event)
        
        self.lineNumberArea.update()
        
        painter = QPainter(self.viewport())
#       painter.fillRect(event.rect(), QColor("lightgray"))
    
    def updateLineNumberAreaWidth(self):
        metrics = QFontMetrics(self.font())
#       lineNumberWidth = metrics.horizontalAdvance("0") * self.blockCount()
        lineNumberWidth = 20
        self.lineNumberArea.setFixedWidth(lineNumberWidth + 10)
        
    def updateLineNumberArea(self):
        cursor = self.textCursor()
        block = cursor.block()
        blockNumber = block.blockNumber() + 1
        
        if blockNumber < 0:
            blockNumber = 0
            
        cursorEnd = cursor.position() + cursor.block().length()
        lineCount = self.document().lastBlock().blockNumber() + 1
        
        self.lineNumberArea.update(0, 0, self.lineNumberArea.width(), lineCount * 20)
        
    def highlightCurrentLine(self):
        cursor = self.textCursor()
        
        if not cursor.hasSelection():
            lineColor = QColor("gray")
            selectionColor = Qt.BrushStyle.NoBrush
        else:
            selectionColor = Qt.highlightSelection()
            lineColor = self.palette().color(QPalette.Text)
            
        format = QTextCharFormat()
        format.setBackground(lineColor)
        
#       cursor.setBlockFormat(format)
        
    
class RegisterTreeWidget(QTreeWidget):
    def __init__(self):
        super().__init__()
#       self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        
class Pymobiledevice3GUIWindow(QMainWindow):
    """PyMobiledevice3GUI's main window (GUI or view)."""
    
    def extract_address(self, string):
        pattern = r'\[0x([0-9a-fA-F]+)\]'
        
        # Use re.search to find the match
        match = re.search(pattern, string)
        
        if match:
            hex_value = match.group(1)
            print("Hex value:", hex_value)
            return hex_value
        else:
            print("No hex value found in the string.")
            return ""
#       pattern = r"0x\d+"
#       match = re.search(pattern, string)
#       if match:
#           return match.group(0)
#       else:
#           return None
#   def extract_address(self, string):
#       pattern = r"0x(?P<address>\d+)"
#       match = re.search(pattern, string)
#       if match:
#           return match.group("address")
#       else:
#           return None
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
        
    def breakpoint_cb(self, frame, bpno, err):
        print('breakpoint callback')
        return False
    
    def disassemble_instructions(self, insts):
        global target
        for i in insts:
#           for function in dir(i):
##               if function.startswith("__file_addr_property__"):
##                   for function2 in dir(function):
##                       print(f'>>> {function2}')
##               if function.startswith("__"):
##                   continue
#               
##               print(function)
#               pass
                
            print(i)
            address = self.extract_address(f'{i}')
            self.txtMultiline.setTextColor(QColor("white"))
            self.txtMultiline.insertPlainText(f'0x{address}:\t')
            self.txtMultiline.setTextColor(QColor("green"))
            self.txtMultiline.insertPlainText(f'{i.GetMnemonic(target)}\t{i.GetOperands(target)}\n') # \t{i.GetData(target)}
            self.txtMultilineNG.setAsmText(f'0x{address}:\t{i.GetMnemonic(target)}\t{i.GetOperands(target)}')
            
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME + " " + APP_VERSION)
        self.setBaseSize(WINDOW_SIZE * 2, WINDOW_SIZE)
        self.setMinimumSize(WINDOW_SIZE * 2, WINDOW_SIZE)

        self.toolbar = QToolBar('Main ToolBar')
        self.addToolBar(self.toolbar)
        self.toolbar.setIconSize(QSize(32, 32))
        
        # new menu item
        new_action = QAction(QIcon(os.path.join("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/resources/", 'bug.png')), '&Bug', self)
        new_action.setStatusTip('Start Debugging')
        new_action.setShortcut('Ctrl+R')
#       new_action.triggered.connect(self.new_document)
#       file_menu.addAction(new_action)
        self.toolbar.addAction(new_action)
        
        run_action = QAction(QIcon(os.path.join("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/resources/", 'play.png')), '&Run', self)
        run_action.setStatusTip('Run Debugging')
        run_action.setShortcut('Ctrl+P')
#       new_action.triggered.connect(self.new_document)
#       file_menu.addAction(new_action)
        self.toolbar.addAction(run_action)
        
        step_over_action = QAction(QIcon(os.path.join("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/resources/", 'step_over_ng2.png')), '&StepOver', self)
        step_over_action.setStatusTip('Step over')
        step_over_action.setShortcut('Ctrl+T')
#       new_action.triggered.connect(self.new_document)
#       file_menu.addAction(new_action)
        self.toolbar.addAction(step_over_action)
        
        step_into_action = QAction(QIcon(os.path.join("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/resources/", 'step_into.png')), '&StepInto', self)
        step_into_action.setStatusTip('Step Into')
        step_into_action.setShortcut('Ctrl+I')
#       new_action.triggered.connect(self.new_document)
#       file_menu.addAction(new_action)
        self.toolbar.addAction(step_into_action)
        
        step_out_action = QAction(QIcon(os.path.join("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/resources/", 'step_out_ng.png')), '&StepOut', self)
        step_out_action.setStatusTip('Step out')
        step_out_action.setShortcut('Ctrl+O')
#       new_action.triggered.connect(self.new_document)
#       file_menu.addAction(new_action)
        self.toolbar.addAction(step_out_action)
        
        self.txtMultiline = CustomTextEdit()
        self.txtMultiline.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.txtMultiline.setReadOnly(True)
        
        font = QFont("Courier New")
        font.setFixedPitch(True)
        
        self.txtMultiline.setFont(font)
#       self.txtMultiline.append(f'HELLO')
        
        self.splitter = QSplitter()
        self.splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
#       self.splitter.setLayout(QHBoxLayout())
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        
        self.layout = QVBoxLayout()
        
        self.txtMultilineNG = AssemblerTextEdit()
        
        self.splitter.addWidget(self.txtMultilineNG)
        
        self.tabWidget = QTabWidget()
        
        self.splitter.addWidget(self.tabWidget)
        
        self.layout.addWidget(self.splitter)
        
        self.wdgCmd = QWidget()
        self.layCmd = QHBoxLayout()
        self.wdgCmd.setLayout(self.layCmd)
        
        self.lblCmd = QLabel("Command: ")
        self.lblCmd.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        
        self.txtCmd = QLineEdit()
        self.txtCmd.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        
        self.cmdExecuteCmd = QPushButton("Execute")
        self.cmdExecuteCmd.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        
        self.layCmd.addWidget(self.lblCmd)
        self.layCmd.addWidget(self.txtCmd)
        self.layCmd.addWidget(self.cmdExecuteCmd)
        
        self.layout.addWidget(self.wdgCmd)
        
#       self.treRegister = RegisterTreeWidget()
#       self.layout.addWidget(self.treRegister)
#       
#       self.treRegister.setFont(font)
#       self.treRegister.setHeaderLabels(['Register Group', 'Registername', 'Value'])
#       self.treRegister.header().resizeSection(0, 306)
        
        
#       self.root_item = QTreeWidgetItem(self.treRegister, ['General purpose register', 'eax', '0x5'])
#       self.root_item2 = QTreeWidgetItem(self.treRegister, ['Floating point register', 'eax', '0x5'])
        # Set the layout of the dialog
#       self.setLayout(self.layout)
        
        centralWidget = QWidget(self)
        centralWidget.setLayout(self.layout)
        
        self.setCentralWidget(centralWidget)
        
#       return
        # Create a new debugger instance
        debugger = lldb.SBDebugger.Create()
        
        # When we step or continue, don't return from the function until the process
        # stops. We do this by setting the async mode to false.
        debugger.SetAsync(False)
        
        print(f'debugger: {debugger}')
        # Create a target from a file and arch
        print("Creating a target for '%s'" % exe)
        
        global target
        target = debugger.CreateTargetWithFileAndArch(exe, None) # lldb.LLDB_ARCH_DEFAULT)
        
        if target:
            print("Has target")
            
        
            # If the target is valid set a breakpoint at main
            main_bp = target.BreakpointCreateByName(fname, target.GetExecutable().GetFilename())
#           main_bp.SetScriptCallbackFunction('breakpoint_cb')
            print(main_bp)
            
            #   breakpoint = target.BreakpointCreateByAddress(0x100003f60) # 0x100003c90)
            #   breakpoint.SetEnabled(True)
            #   breakpoint.SetScriptCallbackFunction('breakpoint_cb')
            #   print(breakpoint)
            
            # Launch the process. Since we specified synchronous mode, we won't return
            # from this function until we hit the breakpoint at main
            global process
            process = target.LaunchSimple(None, None, os.getcwd())
            print(process)
            
            
#           
##           pymobiledevice3GUIApp.exec()
#           # This causes an error and the callback is never called.
#       #   opt = lldb.SBExpressionOptions()
#       #   opt.SetIgnoreBreakpoints(False)
#       #   v = target.EvaluateExpression('main()', opt)
#       #   err = v.GetError()
#       #   if err.fail:
#       #       print(err.GetCString())
#       #   else:
#       #       print(v.value)
#       #   error = lldb.SBError()
#       #   
#       #   sb_launch_info = lldb.SBLaunchInfo(None)
#       #   # sb_launch_info.SetExecutableFile(exe, True)
#       #   
#       #   process = target.Launch(sb_launch_info, error) #debugger.GetListener(), None, None, None, '/tmp/stdout.txt', None, None, 0, True, error)
#           
            # Make sure the launch went ok
            if process:
                print("Process launched OK")
                # Print some simple process info
                state = process.GetState()
                print(process)
                if state == lldb.eStateStopped:
                    print("state == lldb.eStateStopped")
                    
                    print(f'GetNumThreads: {process.GetNumThreads()}')
                    # Get the first thread
                    thread = process.GetThreadAtIndex(0)
                    if thread:
                        # Print some simple thread info
                        print(thread)
#                   else:
#                       print("NO THREAD")
#           return
                        print(f'GetNumFrames: {thread.GetNumFrames()}')
                        # Get the first frame
                        frame = thread.GetFrameAtIndex(0)
                        if frame:
                            # Print some simple frame info
                            print(frame)
                            function = frame.GetFunction()
                            # See if we have debug info (a function)
                            if function:
                                # We do have a function, print some info for the
                                # function
                                print(function)
                                
#                           else:
#                               print("NO FUCNTION")
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
                                    # Now get all instructions for this symbol and
                                    # print them
                                    insts = symbol.GetInstructions(target)
                                    self.disassemble_instructions(insts)
                            
#                           0x0000000108a01910
                            
#                           # Specify the memory address and size you want to read
#                           address = 0x0000000108a01b90
#                           size = 32  # Adjust the size based on your data type (e.g., int, float)
#                           
#                           # Read memory and print the result
#                           data = self.read_memory(process, target.ResolveLoadAddress(address), size)
#                           
#                           hex_string = ''.join("%02x" % byte for byte in data)
##                           formatted_hex_string = re.sub(r"<\d{3}", r"\g ", hex_string)
#                           formatted_hex_string = ' '.join(re.findall(r'.{4}', hex_string))
#                           
#                           if data:
#                               print(f"Data at address {hex(address)}: {data}\n{formatted_hex_string}")
                            
                            registerList = frame.GetRegisters()
                            print(
                                "Frame registers (size of register set = %d):"
                                % registerList.GetSize()
                            )
                            for value in registerList:
                                # print value
                                print(
                                    "%s (number of children = %d):"
                                    % (value.GetName(), value.GetNumChildren())
                                )
                                tabDet = QWidget()
                                treDet = RegisterTreeWidget()
                                tabDet.setLayout(QVBoxLayout())
                                tabDet.layout().addWidget(treDet)
                                
                                treDet.setFont(font)
                                treDet.setHeaderLabels(['Registername', 'Value', 'Memory'])
                                treDet.header().resizeSection(0, 306)
                                treDet.header().resizeSection(1, 256)
                                self.tabWidget.addTab(tabDet, value.GetName())
                                
#                               registerNode = QTreeWidgetItem(self.treRegister, [value.GetName() + " (" + str(value.GetNumChildren()) + ")", '', ''])
#                               QTreeWidgetItem(self.treRegister, ['Floating point register', 'eax', '0x5'])
                                for child in value:
                                    print(
                                        "Name: ", child.GetName(), " Value: ", child.GetValue()
                                    )
                                    
                                    variable_type = type(child.GetValue())
                                    
                                    print(f"The type of child.GetValue() is: {variable_type}")
                                    
                                    memoryValue = ""
                                    try:
                                        
                                        # Specify the memory address and size you want to read
                                        address = 0x0000000108a01b90
                                        addr2 = 0x0000000108a01910
                                        size = 32  # Adjust the size based on your data type (e.g., int, float)
                                        
                                        # Read memory and print the result
                                        data = self.read_memory(process, target.ResolveLoadAddress(int(child.GetValue(), 16)), size)
#                                       data = self.read_memory(process, child.GetValue(), size)
                                        
                                        hex_string = ''.join("%02x" % byte for byte in data)
            #                           formatted_hex_string = re.sub(r"<\d{3}", r"\g ", hex_string)
                                        formatted_hex_string = ' '.join(re.findall(r'.{4}', hex_string))
                                        memoryValue = formatted_hex_string
#                                       if data:
#                                           print(f"Data at address {hex(address)}: {data}\n{formatted_hex_string}")
                                    except Exception as e:
                                        print(f"Error getting memory for addr: {e}")
                                        pass
                                    registerDetailNode = QTreeWidgetItem(treDet, [child.GetName(), child.GetValue(), memoryValue])
                                    
#                   print(
#                       "Hit the breakpoint at main, enter to continue and wait for program to exit or 'Ctrl-D'/'quit' to terminate the program"
#                   )
#                   next = sys.stdin.readline()
#                   if not next or next.rstrip("\n") == "quit":
#                       print("Terminating the inferior process...")
#                       process.Kill()
#                   else:
#                       # Now continue to the program exit
#                       process.Continue()
#                       # When we return from the above function we will hopefully be at the
#                       # program exit. Print out some process info
#                       print(process)
#               elif state == lldb.eStateExited:
#                   print("Didn't hit the breakpoint at main, program has exited...")
#               else:
#                   print(
#                       "Unexpected process state: %s, killing process..."
#                       % debugger.StateAsCString(state)
#                   )
#                   process.Kill()
            else:
                print("Process NOT launched!!!")
        else:
            print("Has NO target")
#           
#       #sys.exit(pymobiledevice3GUIApp.exec())
#           
##       lldb.SBDebugger.Terminate()

#def breakpoint_cb(frame, bpno, err):
#   print('breakpoint callback')
#   return False
#
#def disassemble_instructions(insts):
#   for i in insts:
#       print(i)

#
#def usage():
#   print("Usage: disasm.py [-n name] executable-image")
#   print("       By default, it breaks at and disassembles the 'main' function.")
#   sys.exit(0)
#
#
#if len(sys.argv) == 2:
#   fname = "main"
#   exe = sys.argv[1]
#elif len(sys.argv) == 4:
#   if sys.argv[1] != "-n":
#       usage()
#   else:
#       fname = sys.argv[2]
#       exe = sys.argv[3]
#else:
#   usage()

#class PyMobiledevice3GUI:
#   """PyMobiledevice3GUI's controller class."""
#   
#   def __init__(self, view): # model, 
#       # self._evaluate = model
#       self._view = view
        
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

#   IconHelper.initIcons()
#   
#   # Set the app icon
#pymobiledevice3GUIApp.setWindowIcon(IconHelper.iconApp) #QIcon(icon))
pymobiledevice3GUIApp.setWindowIcon(QIcon(os.path.join("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/resources/", 'bug.png')))
pymobiledevice3GUIWindow = Pymobiledevice3GUIWindow()
pymobiledevice3GUIWindow.show()
#PyMobiledevice3GUI(view=pymobiledevice3GUIWindow)
#pymobiledevice3GUIApp.setQuitOnLastWindowClosed(True)

sys.exit(pymobiledevice3GUIApp.exec())

## Create a new debugger instance
#debugger = lldb.SBDebugger.Create()
#
## When we step or continue, don't return from the function until the process
## stops. We do this by setting the async mode to false.
#debugger.SetAsync(False)
#
#print(f'debugger: {debugger}')
## Create a target from a file and arch
#print("Creating a target for '%s'" % exe)
#
#target = debugger.CreateTargetWithFileAndArch(exe, None) # lldb.LLDB_ARCH_DEFAULT)
#
#if target:
#   print("Has target")
#   # If the target is valid set a breakpoint at main
#   main_bp = target.BreakpointCreateByName(fname, target.GetExecutable().GetFilename())
#   main_bp.SetScriptCallbackFunction('breakpoint_cb')
#   print(main_bp)
#   
##   breakpoint = target.BreakpointCreateByAddress(0x100003f60) # 0x100003c90)
##   breakpoint.SetEnabled(True)
##   breakpoint.SetScriptCallbackFunction('breakpoint_cb')
##   print(breakpoint)
#       
#   # Launch the process. Since we specified synchronous mode, we won't return
#   # from this function until we hit the breakpoint at main
#   process = target.LaunchSimple(None, None, os.getcwd())
#   print(process)
#   
#   pymobiledevice3GUIApp.exec()
#   # This causes an error and the callback is never called.
##   opt = lldb.SBExpressionOptions()
##   opt.SetIgnoreBreakpoints(False)
##   v = target.EvaluateExpression('main()', opt)
##   err = v.GetError()
##   if err.fail:
##       print(err.GetCString())
##   else:
##       print(v.value)
##   error = lldb.SBError()
##   
##   sb_launch_info = lldb.SBLaunchInfo(None)
##   # sb_launch_info.SetExecutableFile(exe, True)
##   
##   process = target.Launch(sb_launch_info, error) #debugger.GetListener(), None, None, None, '/tmp/stdout.txt', None, None, 0, True, error)
#                           
#   # Make sure the launch went ok
#   if process:
#       print("Process launched OK")
#       # Print some simple process info
#       state = process.GetState()
#       print(process)
#       if state == lldb.eStateStopped:
#           print("state == lldb.eStateStopped")
#           # Get the first thread
#           thread = process.GetThreadAtIndex(0)
#           if thread:
#               # Print some simple thread info
#               print(thread)
#               # Get the first frame
#               frame = thread.GetFrameAtIndex(0)
#               if frame:
#                   # Print some simple frame info
#                   print(frame)
#                   function = frame.GetFunction()
#                   # See if we have debug info (a function)
#                   if function:
#                       # We do have a function, print some info for the
#                       # function
#                       print(function)
#                       # Now get all instructions for this function and print
#                       # them
#                       insts = function.GetInstructions(target)
#                       disassemble_instructions(insts)
#                   else:
#                       # See if we have a symbol in the symbol table for where
#                       # we stopped
#                       symbol = frame.GetSymbol()
#                       if symbol:
#                           # We do have a symbol, print some info for the
#                           # symbol
#                           print(symbol)
#                           # Now get all instructions for this symbol and
#                           # print them
#                           insts = symbol.GetInstructions(target)
#                           disassemble_instructions(insts)
#
#                   registerList = frame.GetRegisters()
#                   print(
#                       "Frame registers (size of register set = %d):"
#                       % registerList.GetSize()
#                   )
#                   for value in registerList:
#                       # print value
#                       print(
#                           "%s (number of children = %d):"
#                           % (value.GetName(), value.GetNumChildren())
#                       )
#                       for child in value:
#                           print(
#                               "Name: ", child.GetName(), " Value: ", child.GetValue()
#                           )
#
#           print(
#               "Hit the breakpoint at main, enter to continue and wait for program to exit or 'Ctrl-D'/'quit' to terminate the program"
#           )
#           next = sys.stdin.readline()
#           if not next or next.rstrip("\n") == "quit":
#               print("Terminating the inferior process...")
#               process.Kill()
#           else:
#               # Now continue to the program exit
#               process.Continue()
#               # When we return from the above function we will hopefully be at the
#               # program exit. Print out some process info
#               print(process)
#       elif state == lldb.eStateExited:
#           print("Didn't hit the breakpoint at main, program has exited...")
#       else:
#           print(
#               "Unexpected process state: %s, killing process..."
#               % debugger.StateAsCString(state)
#           )
#           process.Kill()
#   else:
#       print("Process NOT launched!!!")
#else:
#   print("Has NO target")
#
##sys.exit(pymobiledevice3GUIApp.exec())
#
#lldb.SBDebugger.Terminate()
