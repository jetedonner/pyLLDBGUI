if __name__ == "__main__":
    print("Run only as script from LLDB... Not as standalone program!")

import lldb    
import sys
import re
import os
import threading
import time
import struct
import argparse
import subprocess
import tempfile
import termios
import fcntl
import json
import hashlib

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from PyQt6.QConsoleTextEdit import *

from lldbpyGUIConfig import *
from lldbpyGUIWindow import *

from config import *

# test terminal - idea from https://github.com/ant4g0nist/lisa.py/
try:
    tty_rows, tty_columns = struct.unpack("hh", fcntl.ioctl(1, termios.TIOCGWINSZ, "1234"))
    # i386 is fine with 87x21
    # x64 is fine with 125x23
    # aarch64 is fine with 108x26
    if tty_columns < MIN_COLUMNS or tty_rows < MIN_ROWS:
        print("\033[1m\033[31m[!] current terminal size is {:d}x{:d}".format(tty_columns, tty_rows))
        print("[!] lldbinit is best experienced with a terminal size at least {}x{}\033[0m".format(MIN_COLUMNS, MIN_ROWS))
except Exception as e:
    print("\033[1m\033[31m[-] failed to find out terminal size.")
    print("[!] lldbinit is best experienced with a terminal size at least {}x{}\033[0m".format(MIN_COLUMNS, MIN_ROWS))

#def breakpointHandler(frame, bpno, err):
# print("MLIR debugger attaching...")
# print("IIIIIIIIINNNNNNNN CCCCAAQALLLLLLBBBAAACCKKKK")
# 
#class QConsoleTextEditWindow(QMainWindow):
#   
#   mytext = "thread #1: tid = 0xa8f62d, 0x0000000100003f40 hello_world_test_loop`main, queue = \x1b[32m'com.apple.main-thread'\x1b[0m, stop reason = \x1b[31mbreakpoint 1.1\x1b[0m\nthread #2: tid = 0xa8f62d, 0x0000000100003f40 hello_world_test_loop`main, queue = \x1b[35m'com.apple.main-thread'\x1b[0m, stop reason = \x1b[36mbreakpoint 1.1\x1b[0m"
#   debugger = None
#
#   def __init__(self, debugger):
#       super().__init__()
#       self.debugger = debugger
#       self.setWindowTitle(APP_NAME + " " + APP_VERSION)
#       self.setBaseSize(WINDOW_SIZE * 2, WINDOW_SIZE)
#       self.setMinimumSize(WINDOW_SIZE * 2, WINDOW_SIZE + 72)
#       
#       self.layout = QVBoxLayout()
#       # self.layoutV = QHBoxLayout()
#
#       self.centralWidget = QWidget(self)
#       self.centralWidget.setLayout(self.layout)
#       self.setCentralWidget(self.centralWidget)
#       self.txtConsole = QConsoleTextEdit()
#       self.cmdTest = QPushButton("CONTINUE")
#       self.cmdTest.clicked.connect(self.interruptProcess)
#       self.cmdTest2 = QPushButton("STEP NEXT")
#       self.cmdTest2.clicked.connect(self.stepNextProcess)
#       self.cmdTest3 = QPushButton("RE READ")
#       self.cmdTest3.clicked.connect(self.readProcess)
#       self.cmdTest4 = QPushButton("DI")
#       self.cmdTest4.clicked.connect(self.disassembleLocation)
#       self.cmdTest5 = QPushButton("Clear")
#       self.cmdTest5.clicked.connect(self.clearTxt)
#       self.layout.addWidget(self.cmdTest)
#       self.layout.addWidget(self.cmdTest2)
#       self.layout.addWidget(self.cmdTest3)
#       self.layout.addWidget(self.cmdTest4)
#       self.layout.addWidget(self.cmdTest5)
#       self.txtOutput = QConsoleTextEdit()
#       self.txtOutput.setFont(QFont("Courier New"))
#       self.layout.addWidget(self.txtOutput)
#       self.txtConsole.setText(self.mytext)
#       # self.txtConsole.appendText(self.mytext)
#       
#   def interruptProcess(self):
#       res = lldb.SBCommandReturnObject()
#       ci = self.debugger.GetCommandInterpreter()
#       # ci.HandleCommand("re read", res)
#       ci.HandleCommand("continue", res)
#       print(res.GetOutput())
#       self.txtOutput.appendEscapedText(res.GetOutput())
#       # ci.HandleCommand("n", res)
#
#   def stepNextProcess(self):
#       res = lldb.SBCommandReturnObject()
#       ci = self.debugger.GetCommandInterpreter()
#       # ci.HandleCommand("re read", res)
#       ci.HandleCommand("n", res)
#       print(res.GetOutput())
#       self.txtOutput.appendEscapedText(res.GetOutput())
#       # ci.HandleCommand("n", res)
#
#   def readProcess(self):
#       res = lldb.SBCommandReturnObject()
#       ci = self.debugger.GetCommandInterpreter()
#       # ci.HandleCommand("re read", res)
#       ci.HandleCommand("re read", res)
#       print(res.GetOutput())
#       self.txtOutput.appendEscapedText(res.GetOutput())
#       # ci.HandleCommand("n", res)
#
#   def disassembleLocation(self):
#       res = lldb.SBCommandReturnObject()
#       ci = self.debugger.GetCommandInterpreter()
#       # ci.HandleCommand("re read", res)
#       ci.HandleCommand("di", res)
#       print(res.GetOutput())
#       self.txtOutput.appendEscapedText(res.GetOutput())
#       
#   def clearTxt(self):
#       self.txtOutput.setEscapedText("")
#   
#
#   # we hook this so we have a chance to initialize/reset some stuff when targets are (re)run
#
#
##def close_application():
##   pass


def __lldb_init_module(debugger, internal_dict):
    ''' we can execute lldb commands using debugger.HandleCommand() which makes all output to default
    lldb console. With SBDebugger.GetCommandinterpreter().HandleCommand() we can consume all output
    with SBCommandReturnObject and parse data before we send it to output (eg. modify it);

    in practice there is nothing here in initialization or anywhere else that we want to modify
    '''

    # don't load if we are in Xcode since it is not compatible and will block Xcode
    if os.getenv('PATH').startswith('/Applications/Xcode'):
        return

    global g_home
    if g_home == "":
        g_home = os.getenv('HOME')
    
    res = lldb.SBCommandReturnObject()
    ci = debugger.GetCommandInterpreter()
    
    # settings
    ci.HandleCommand("settings set target.x86-disassembly-flavor " + CONFIG_FLAVOR, res)
    ci.HandleCommand(f"settings set prompt \"({PROMPT_TEXT}) \"", res)
    ci.HandleCommand("settings set stop-disassembly-count 0", res)
    # set the log level - must be done on startup?
    ci.HandleCommand("settings set target.process.extra-startup-command QSetLogging:bitmask=" + CONFIG_LOG_LEVEL + ";", res)
    if CONFIG_USE_CUSTOM_DISASSEMBLY_FORMAT == 1:
        ci.HandleCommand("settings set disassembly-format " + CUSTOM_DISASSEMBLY_FORMAT, res)

    # the hook that makes everything possible :-)
    ci.HandleCommand(f"command script add -h '({PROMPT_TEXT})' -f lldbpyGUI.TestCommand TestCommand", res)
    ci.HandleCommand(f"command alias -h '({PROMPT_TEXT}) Start the python GUI.' -- pygui TestCommand", res)

    ci.HandleCommand(f"command script add -h '({PROMPT_TEXT}) Start the target and stop at entrypoint.' -f lldbpyGUI.cmd_run r", res)
    ci.HandleCommand(f"command alias -h '({PROMPT_TEXT}) Start the target and stop at entrypoint.' -- run r", res)

    ci.HandleCommand(f"command script add -h '({PROMPT_TEXT})' -f lldbpyGUI.StartTestingEnv test", res)

processGlob = None

def StartTestingEnv(debugger, command, result, dict):
  print(f"#=================================================================================#")
  print(f"| Starting TEST ENVIRONMENT for LLDB-PyGUI (Development Mode, ver. {APP_VERSION})        |")
  print(f"|                                                                                 |")
  print(f"| Desc:                                                                           |")
  print(f"| This python script is for development of the LLDB python GUI - use at own risk! |")
  print(f"|                                                                                 |")
  print(f"| Author / Copyright:                                                             |")
  print(f"| Kim David Hauser (JeTeDonner), (c) by kimhauser.ch 1991-2024                    |")
  print(f"#=================================================================================#")
  res = lldb.SBCommandReturnObject()    
  # must be set to true otherwise we don't get any output on the first stop hook related to this
  debugger.SetAsync(False)
  # imitate the original 'r' alias plus the stop at entry and pass everything else as target argv[]
  print(f"NUM-TARGETS: {debugger.GetNumTargets()}")
  if debugger.GetNumTargets() > 0:
    print(f"TARGET-1: {debugger.GetTargetAtIndex(0)}")
    target = debugger.GetTargetAtIndex(0)
    
    fname = "main"
    main_bp = target.BreakpointCreateByName(fname, target.GetExecutable().GetFilename())
    main_bp.AddName(fname)
    print(main_bp)
    
    loop_bp = target.BreakpointCreateByAddress(0x100003f85) # 0x100003c90)
    loop_bp.SetEnabled(True)
    loop_bp.AddName("loop_bp")
    loop_bp.SetScriptCallbackFunction("lldbpyGUI.breakpointHandler")
#   loop_bp.SetCondition("$eax == 0x00000005")
#   loop_bp.SetScriptCallbackFunction("disasm_ui.breakpointHandler")
    print(loop_bp)
    
    loop_bp2 = target.BreakpointCreateByAddress(0x100003f6d) # 0x100003c90)
    loop_bp2.SetEnabled(True)
    loop_bp2.AddName("loop_bp2")
    loop_bp2.SetCondition("$eax == 0x00000005")
    loop_bp2.SetScriptCallbackFunction("lldbpyGUI.breakpointHandler")
    print(loop_bp2)
    
    process = target.LaunchSimple(None, None, os.getcwd())
    if process:
#     pass
      processGlob = process
      state = process.GetState()
#				print(self.process)
      if state == lldb.eStateStopped:
        print("state == lldb.eStateStopped")
        
#       TestCommand(debugger, command, result, dict)
# debugger.GetCommandInterpreter().HandleCommand("r", res)
# print(f"Command 'r' succeeded? => {res.Succeeded()}")
# print(res.GetOutput())
# debugger.SetAsync(False)
# debugger.GetCommandInterpreter().HandleCommand("b 4294983557", res)
# print(f"Command 'b 4294983557' succeeded? => {res.Succeeded()}")
# print(res.GetOutput())
# debugger.GetCommandInterpreter().HandleCommand("continue", res)
# print(f"Command 'continue' succeeded? => {res.Succeeded()}")
# print(res.GetOutput())
# debugger.GetCommandInterpreter().HandleCommand("pygui", res)
# print(f"Command 'pygui' succeeded? => {res.Succeeded()}")
# print(res.GetOutput())
# pass

#pymobiledevice3GUIWindow = None
#pymobiledevice3GUIApp = None
#debuggerNG = None
    
#def run_gui_thread():
#   pymobiledevice3GUIApp = QApplication([])
#   # pymobiledevice3GUIApp.aboutToQuit.connect(close_application)
#   
#   pymobiledevice3GUIWindow = QConsoleTextEditWindow(debuggerNG)
#   pymobiledevice3GUIWindow.show()
# 
##   sys.exit(pymobiledevice3GUIApp.exec())
#   pymobiledevice3GUIApp.exec()
  

def close_application():
##   global process
# # Stop all running tasks in the thread pool
# if lldbHelper.process:
#   pymobiledevice3GUIWindow.interruptLoadWorker.interruptTargetLoadSignal.emit()
#   QCoreApplication.processEvents()
#   print("KILLING PROCESS")
#   lldbHelper.process.Kill()
# else:
#   print("NO PROCESS TO KILL!!!")
##   global pymobiledevice3GUIApp
##   pymobiledevice3GUIApp.quit()
    pass
    
def TestCommand(debugger, command, result, dict):
    print("STARTING LLDB-PyGUI!!!")
#   debuggerNG = debugger
#   debugger.SetAsync(True)
    pymobiledevice3GUIApp = QApplication([])
    pymobiledevice3GUIApp.aboutToQuit.connect(close_application)
    
    #
    ConfigClass.initIcons()
    pymobiledevice3GUIApp.setWindowIcon(ConfigClass.iconBugGreen)
    
    pymobiledevice3GUIWindow = LLDBPyGUIWindow(debugger) # QConsoleTextEditWindow(debugger)
    pymobiledevice3GUIWindow.show()
##   sys.exit(pymobiledevice3GUIApp.exec())
    sys.exit(pymobiledevice3GUIApp.exec())
    
#   gui_thread = threading.Thread(target=run_gui_thread)
#   gui_thread.start()
# 
#   # Continue with other script tasks
#   time.sleep(5)  # Simulate other work
#   print("Script continues while GUI runs in a separate thread.")
    
    return 0
    # also modify to stop at entry point since we can't set breakpoints before

# we hook this so we have a chance to initialize/reset some stuff when targets are (re)run
# also modify to stop at entry point since we can't set breakpoints before
def cmd_run(debugger, command, result, dict):
    '''Run the target and stop at entry. Everything else after the command is considered target arguments.'''
    help = """
Run the target, stopping at entry (dyld).

Syntax: r

Note: 'r' is an abbreviation for 'process launch -s -X true --'.
Replaces the original r/run alias.
 """
    # reset internal state variables

    res = lldb.SBCommandReturnObject()    
    # must be set to true otherwise we don't get any output on the first stop hook related to this
    debugger.SetAsync(True)
    # imitate the original 'r' alias plus the stop at entry and pass everything else as target argv[]
    debugger.GetCommandInterpreter().HandleCommand("process launch -s -X true -- {}".format(command), res)