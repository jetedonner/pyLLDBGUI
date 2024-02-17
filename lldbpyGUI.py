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
import os

from threading import Thread

try:
  import queue
except ImportError:
  import Queue as queue

import debuggerdriver
from debuggerdriver import *

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from QConsoleTextEdit import *

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


def breakpointHandlerNG(dummy, frame, bpno, err):
#   print(dummy)
#   print(frame)
#   print(bpno)
#   print(err)
    global pymobiledevice3GUIWindow
    pymobiledevice3GUIWindow.bpcp("YESSSSS!!!!!")
#   print("MLIR debugger attaching...")
#   print("IIIIIIIIINNNNNNNN CCCCAAQALLLLLLBBBAAACCKKKK")
    
#def breakpointHandler(frame, bpno, err):
#   print("MLIR debugger attaching (KIM)...")
#   print("IIIIIIIIINNNNNNNN CCCCAAQALLLLLLBBBAAACCKKKK")

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
#   ci.HandleCommand("settings set target.process.extra-startup-command QSetLogging:bitmask=" + CONFIG_LOG_LEVEL + ";", res)
    if CONFIG_USE_CUSTOM_DISASSEMBLY_FORMAT == 1:
        ci.HandleCommand("settings set disassembly-format " + CUSTOM_DISASSEMBLY_FORMAT, res)

    # the hook that makes everything possible :-)
    ci.HandleCommand(f"command script add -h '({PROMPT_TEXT}) Start the python GUI.' -f lldbpyGUI.TestCommand TestCommand", res)
    ci.HandleCommand(f"command alias -h '({PROMPT_TEXT}) Start the python GUI.' -- pygui TestCommand", res)

    ci.HandleCommand(f"command script add -h '({PROMPT_TEXT}) Start the target and stop at entrypoint.' -f lldbpyGUI.cmd_run r", res)
    ci.HandleCommand(f"command alias -h '({PROMPT_TEXT}) Start the target and stop at entrypoint.' -- run r", res)
    
    ci.HandleCommand(f"command alias -h '({PROMPT_TEXT}) Start the python GUI.' -H '({PROMPT_TEXT}) Start the python GUI.' -- ng TestCommand", res)
    
    ci.HandleCommand("command script add -h '(lldbinit) Display lldbinit banner.' --function lldbpyGUI.cmd_banner banner", res)
    
    ci.HandleCommand("command script add -h '(lldbinit) The breakpoint callback function.' --function lldbpyGUI.breakpointHandlerNG bpcb", res)
    
    ci.HandleCommand("command script add -h '(lldbinit) The breakpoint callback function (driver).' --function debuggerdriver.breakpointHandlerDriver bpcbdriver", res)
    
    debugger.HandleCommand("banner")
    
#   debugger.HandleCommand("br com a -F lldbpyGUI.breakpointHandler")
    
    return

global pymobiledevice3GUIWindow
pymobiledevice3GUIWindow = None

global pymobiledevice3GUIApp
pymobiledevice3GUIApp = None

def close_application():
    global driver
    
  
#   pymobiledevice3GUIWindow.interruptEventListenerWorker.interruptEventListener.emit()
#   pymobiledevice3GUIWindow.interruptLoadSourceWorker.interruptLoadSource.emit()
#   QCoreApplication.processEvents()
    print("close_application()")
# # Stop all running tasks in the thread pool
    if pymobiledevice3GUIWindow.driver.getTarget().GetProcess(): #pymobiledevice3GUIWindow.process:
#   pymobiledevice3GUIWindow.interruptLoadWorker.interruptTargetLoadSignal.emit()
#   QCoreApplication.processEvents()
        print("KILLING PROCESS")
        
        driver.aborted = True
        print("Aborted sent")
        os._exit(1)
#       sys.exit(0)
#       pymobiledevice3GUIWindow.process.Kill()
#       global driver
#       driver.terminate()
#       pymobiledevice3GUIWindow.driver.getTarget().GetProcess().Stop()
#       print("Process stopped")        
        pymobiledevice3GUIWindow.driver.getTarget().GetProcess().Kill()
        print("Process killed")
#       QCoreApplication.processEvents()
    else:
        print("NO PROCESS TO KILL!!!")
    global pymobiledevice3GUIApp
    pymobiledevice3GUIApp.quit()
    driver.terminate()
#   sys.exit()

def cmd_banner(debugger,command,result,dict):    
  print(RED + "[+] Loaded " + APP_NAME + " version " + APP_VERSION + " (BUILD: " + APP_BUILD + ")" + RESET)
  
def TestCommand(debugger, command, result, dict):
    testTarget = "/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/LLDBPyGUI/testtarget/hello_world_test"
    
    print(f"" + GREEN + "#=================================================================================#")
    print(f"| Starting TEST ENVIRONMENT for LLDB-PyGUI (Development Mode, ver. {APP_VERSION})         |")
    print(f"|                                                                                 |")
    print(f"| Desc:                                                                           |")
    print(f"| This python script is for development and testing while development             |")
    print(f"| of the LLDB python GUI (LLDBPyGUI.py) - use at own risk! No Warranty!           |")
    print(f"|                                                                                 |")
    print(f"| Credits:                                                                        |")
    print(f"| - LLDB                                                                          |")
    print(f"| - lldbutil.py                                                                   |")
    print(f"| - lui.py                                                                        |")
    print(f"|                                                                                 |")
    print(f"| Author / Copyright:                                                             |")
    print(f"| Kim David Hauser (JeTeDonner), (C.) by kimhauser.ch 1991-2024                   |")
    print(f"#=================================================================================#" + RESET)
  
    print("LOADING TARGET: %s" % testTarget)
#   debugger.SetAsync(False)
    
    global event_queue
    event_queue = queue.Queue()

    global driver
    driver = debuggerdriver.createDriver(debugger, event_queue)
#   view = LLDBUI(screen, event_queue, driver)
    driver.createTarget(testTarget)
#   print(f"NUM-TARGETS: {debugger.GetNumTargets()}")
    if debugger.GetNumTargets() > 0:
#     print(f"TARGET-1: {debugger.GetTargetAtIndex(0)}")
      target = driver.getTarget()
      
      fname = "main"
      main_bp = target.BreakpointCreateByName(fname, target.GetExecutable().GetFilename())
      main_bp.AddName(fname)
#     print(main_bp)
      
#     loop_bp = target.BreakpointCreateByAddress(0x100003f6a) # 0x100003f85) # 0x100003c90) 
#     loop_bp.SetEnabled(True)
#     loop_bp.AddName("loop_bp")
#
##     breakpoint set -a 0x100003f6a
##     loop_bp.SetScriptCallbackFunction("lldbpyGUI.breakpointHandler")
##     loop_bp.SetCondition("$eax == 0x00000000")
##     loop_bp.SetScriptCallbackFunction("disasm_ui.breakpointHandler")
#     print(loop_bp)
      
#     loop_bp2 = target.BreakpointCreateByAddress(0x100003f6d) # 0x100003c90)
#     loop_bp2.SetEnabled(True)
#     loop_bp2.AddName("loop_bp2")
#     loop_bp2.SetCondition("$eax == 0x00000000")
#     loop_bp2.SetScriptCallbackFunction("lldbpyGUI.breakpointHandler")
#     print(loop_bp2)
      
      process = target.LaunchSimple(None, None, os.getcwd())
      
#     error = lldb.SBError()
#     #     (lldb::SBLaunchInfo
#     info = lldb.SBLaunchInfo(None)
#     info.SetLaunchFlags(lldb.eLaunchFlagStopAtEntry)
#     info.SetWorkingDirectory(os.getcwd())
      #     info.SetArguments(None)
      #     launchFlags = lldb.eLaunchFlagStopAtEntry
      
      
#     driver.handleCommand("breakpoint set -n main -N main")
#     driver.handleCommand("br com a -F lldbpyGUI.breakpointHandlerNG")
      
#     process.Continue()
      
      if process:
        state = process.GetState()
        if state == lldb.eStateStopped:
          print("state == lldb.eStateStopped")
          
#         driver.handleCommand("b 0x100003f85")
#         driver.handleCommand("br com a -F lldbpyGUI.breakpointHandlerNG")
        
        
  #       driver.start()
  #       print("AFTER START DRIVER!!!!")
        # hack to avoid hanging waiting for prompts!
        driver.handleCommand("settings set auto-confirm true")
  #       debugger.SetAsync(True)
    #   handle_args(driver, sys.argv)
    #   view.eventLoop()
        
#       winTrd = WindowDriver(debugger, driver)
#       winTrd.start()
        
        global pymobiledevice3GUIApp
        pymobiledevice3GUIApp = QApplication([])
        pymobiledevice3GUIApp.aboutToQuit.connect(close_application)
        #
        ConfigClass.initIcons()
        pymobiledevice3GUIApp.setWindowIcon(ConfigClass.iconBugGreen)
        
        global pymobiledevice3GUIWindow
        pymobiledevice3GUIWindow = LLDBPyGUIWindow(debugger, driver) # QConsoleTextEditWindow(debugger)
        #     pymobiledevice3GUIWindow.loadTarget()
        pymobiledevice3GUIWindow.show()
        
#       pymobiledevice3GUIWindow.move(650, 20)
#       pymobiledevice3GUIWindow.tabWidgetMain.setCurrentIndex(2)
#       driver.start()
#       interctive_loop(debugger)
        print("AFTER START DRIVER!!!!")
        #     process = target.Launch(info, error)
        #     if error:
        #       print(error)
        pymobiledevice3GUIWindow.loadTarget()
        #     process.Continue()
        #       driver.handleCommand("br com a -F lldbpyGUI.breakpointHandlerNG")
        ##   sys.exit(pymobiledevice3GUIApp.exec())
        #   sys.exit(pymobiledevice3GUIApp.exec())
        #         process = debugger.GetSelectedTarget().GetProcess()
        
#       global event_thread
        event_thread = LLDBListenerThread(process)
        event_thread.start()
#       interctive_loop(debugger)
        pymobiledevice3GUIApp.exec()
        
        
        
      #   gui_thread = threading.Thread(target=run_gui_thread)
      #   gui_thread.start()
#       stdout_stream = process.GetSTDOUT(lldb.eStreamBytes)
#       stderr_stream = process.GetSTDERR(lldb.eStreamBytes)
#       while process.IsRunning():
#         data = stdout_stream.ReadBytes(1024)
#         if data:
#           print("STDOUT:", data.decode())
#         data = stderr_stream.ReadBytes(1024)
#         if data:
#           print("STDERR:", data.decode())
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
#   debugger.SetAsync(True)
    # imitate the original 'r' alias plus the stop at entry and pass everything else as target argv[]
    debugger.GetCommandInterpreter().HandleCommand("process launch -s -X true -- {}".format(command), res)
    
    
class WindowDriver(Thread):
    """ Drives the debugger and responds to events. """
  
    def __init__(self, debugger, driver):
        Thread.__init__(self)
        self.debugger = debugger
        self.driver = driver
        self.daemon = True
        self.initialize(debugger)
      
    def initialize(self, debugger):
        self.done = False
  
    def eventLoop(self):
#       global process
        while not self.isDone():
          pass
#           event = lldb.SBEvent()
#           got_event = self.listener.WaitForEvent(lldb.UINT32_MAX, event)
#           print(f'GOT-EVENT: {event} / {event.GetType()}')
#           desc = lldbutil.get_description(event)
#           print('Event description:', desc)
#           print('Event data flavor:', event.GetDataFlavor())
##           if event.GetDataFlavor() == "Breakpoint::BreakpointEventData":
##             print("GOT BREAKPOINT CHANGE!!!")
##           global process
##           print('Process state:', lldbutil.state_type_to_str(process.GetState()))
#           print()
#         
#           # eBroadcastBitSTDOUT
##           if event.GetType() == lldb.SBProcess.eBroadcastBitSTDOUT:
##             stdout = process.GetSTDOUT(256)
##             if stdout is not None and len(stdout) > 0:
##               message = {"status":"event", "type":"stdout", "output": "".join(["%02x" % ord(i) for i in stdout])}
#           if got_event and not event.IsValid():
#               self.winAddStr("Warning: Invalid or no event...")
#               continue
#           elif not event.GetBroadcaster().IsValid():
#               continue
#         
#           self.event_queue.put(event)
#           self.signals.event_queued.emit(event)
          
    def run(self):
        global pymobiledevice3GUIApp
        pymobiledevice3GUIApp = QApplication([])
#       pymobiledevice3GUIApp.aboutToQuit.connect(close_application)
        #
        ConfigClass.initIcons()
        pymobiledevice3GUIApp.setWindowIcon(ConfigClass.iconBugGreen)
      
        global pymobiledevice3GUIWindow
        pymobiledevice3GUIWindow = LLDBPyGUIWindow(self. debugger, self.driver) # QConsoleTextEditWindow(debugger)
  #     pymobiledevice3GUIWindow.loadTarget()
        pymobiledevice3GUIWindow.show()
        pymobiledevice3GUIWindow.move(650, 20)
        pymobiledevice3GUIWindow.tabWidgetMain.setCurrentIndex(2)
        self.driver.start()
        print("AFTER START DRIVER!!!!")
  #     process = target.Launch(info, error)
  #     if error:
  #       print(error)
        pymobiledevice3GUIWindow.loadTarget()
  #     process.Continue()
  #       driver.handleCommand("br com a -F lldbpyGUI.breakpointHandlerNG")
    ##   sys.exit(pymobiledevice3GUIApp.exec())
    #   sys.exit(pymobiledevice3GUIApp.exec())
        pymobiledevice3GUIApp.exec()
        self.eventLoop()
      
    def terminate(self):
#       lldb.SBDebugger.Terminate()
        sys.exit(0)