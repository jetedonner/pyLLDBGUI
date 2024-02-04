if __name__ == "__main__":
    print("Run only as script from LLDB... Not as standalone program!")

import lldb    
import sys
import re
import os
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

APP_NAME = "ConsoleTextEditWindow-TEST"
WINDOW_SIZE = 720

APP_VERSION = "v0.0.1"

try:
    import keystone
    CONFIG_KEYSTONE_AVAILABLE = 1
except ImportError:
    CONFIG_KEYSTONE_AVAILABLE = 0
    pass

VERSION = "3.1"
BUILD = "383"

#
# User configurable options
#
CONFIG_ENABLE_COLOR = 1
# light or dark mode
CONFIG_APPEARANCE = "light"
# display the instruction bytes in disassembler output
CONFIG_DISPLAY_DISASSEMBLY_BYTES = 1
# the maximum number of lines to display in disassembler output
CONFIG_DISASSEMBLY_LINE_COUNT = 8
# x/i and disas output customization - doesn't affect context disassembler output
CONFIG_USE_CUSTOM_DISASSEMBLY_FORMAT = 1
# enable all the register command shortcuts
CONFIG_ENABLE_REGISTER_SHORTCUTS = 1
# display stack contents on context stop
CONFIG_DISPLAY_STACK_WINDOW = 0
CONFIG_DISPLAY_FLOW_WINDOW = 0
# display data contents on context stop - an address for the data must be set with "datawin" command
CONFIG_DISPLAY_DATA_WINDOW = 0
# disassembly flavor 'intel' or 'att' - default is Intel unless AT&T syntax is your cup of tea
CONFIG_FLAVOR = "intel"

# setup the logging level, which is a bitmask of any of the following possible values (don't use spaces, doesn't seem to work)
#
# LOG_VERBOSE LOG_PROCESS LOG_THREAD LOG_EXCEPTIONS LOG_SHLIB LOG_MEMORY LOG_MEMORY_DATA_SHORT LOG_MEMORY_DATA_LONG LOG_MEMORY_PROTECTIONS LOG_BREAKPOINTS LOG_EVENTS LOG_WATCHPOINTS
# LOG_STEP LOG_TASK LOG_ALL LOG_DEFAULT LOG_NONE LOG_RNB_MINIMAL LOG_RNB_MEDIUM LOG_RNB_MAX LOG_RNB_COMM  LOG_RNB_REMOTE LOG_RNB_EVENTS LOG_RNB_PROC LOG_RNB_PACKETS LOG_RNB_ALL LOG_RNB_DEFAULT
# LOG_DARWIN_LOG LOG_RNB_NONE
#
# to see log (at least in macOS)
# $ log stream --process debugserver --style compact
# (or whatever style you like)
CONFIG_LOG_LEVEL = "LOG_NONE"

# removes the offsets and modifies the module name position
# reference: https://lldb.llvm.org/formats.html
CUSTOM_DISASSEMBLY_FORMAT = "\"{${function.initial-function}{${function.name-without-args}} @ {${module.file.basename}}:\n}{${function.changed}\n{${function.name-without-args}} @ {${module.file.basename}}:\n}{${current-pc-arrow} }${addr-file-or-load}: \""

# the colors definitions - don't mess with this
if CONFIG_ENABLE_COLOR:
    RESET =     "\033[0m"
    BOLD =      "\033[1m"
    UNDERLINE = "\033[4m"
    REVERSE =   "\033[7m"
    BLACK =     "\033[30m"
    RED =       "\033[31m"
    GREEN =     "\033[32m"
    YELLOW =    "\033[33m"
    BLUE =      "\033[34m"
    MAGENTA =   "\033[35m"
    CYAN =      "\033[36m"
    WHITE =     "\033[37m"
else:
    RESET =     ""
    BOLD =      ""
    UNDERLINE = ""
    REVERSE =   ""
    BLACK =     ""
    RED =       ""
    GREEN =     ""
    YELLOW =    ""
    BLUE =      ""
    MAGENTA =   ""
    CYAN =      ""
    WHITE =     ""

# default colors - modify as you wish
# since these are just strings modes can be combined
if CONFIG_APPEARANCE == "light":
    COLOR_REGVAL           = BLACK
    COLOR_REGNAME          = GREEN
    COLOR_CPUFLAGS         = BOLD + UNDERLINE + MAGENTA
    COLOR_SEPARATOR        = BOLD + BLUE
    COLOR_HIGHLIGHT_LINE   = RED
    COLOR_REGVAL_MODIFIED  = RED
    COLOR_SYMBOL_NAME      = BLUE
    COLOR_CURRENT_PC       = RED
    COLOR_CONDITIONAL_YES  = REVERSE + GREEN
    COLOR_CONDITIONAL_NO   = REVERSE + RED
    COLOR_HEXDUMP_HEADER   = BLUE
    COLOR_HEXDUMP_ADDR     = BLACK
    COLOR_HEXDUMP_DATA     = BLACK
    COLOR_HEXDUMP_ASCII    = BLACK
    COLOR_COMMENT          = GREEN
elif CONFIG_APPEARANCE == "dark":
    COLOR_REGVAL           = WHITE
    COLOR_REGNAME          = GREEN
    COLOR_CPUFLAGS         = BOLD + UNDERLINE + MAGENTA
    COLOR_SEPARATOR        = CYAN
    COLOR_HIGHLIGHT_LINE   = RED
    COLOR_REGVAL_MODIFIED  = RED
    COLOR_SYMBOL_NAME      = BLUE
    COLOR_CURRENT_PC       = RED
    COLOR_CONDITIONAL_YES  = REVERSE + GREEN
    COLOR_CONDITIONAL_NO   = REVERSE + RED
    COLOR_HEXDUMP_HEADER   = BLUE
    COLOR_HEXDUMP_ADDR     = WHITE
    COLOR_HEXDUMP_DATA     = WHITE
    COLOR_HEXDUMP_ASCII    = WHITE
    COLOR_COMMENT          = GREEN # XXX: test and change
else:
    print("[-] Invalid CONFIG_APPEARANCE value.")

# configure the separator character between the "windows" and their size
SEPARATOR = "-"
# minimum terminal width 120 chars
I386_TOP_SIZE = 81
I386_STACK_SIZE = I386_TOP_SIZE - 1
I386_BOTTOM_SIZE = 87
# minimum terminal width 125 chars
X64_TOP_SIZE = 119
X64_STACK_SIZE = X64_TOP_SIZE - 1
X64_BOTTOM_SIZE = 125
# minimum terminal width 108 chars
ARM_TOP_SIZE = 102
ARM_STACK_SIZE = ARM_TOP_SIZE - 1
ARM_BOTTOM_SIZE = 108

# turn on debugging output - you most probably don't need this
DEBUG = 0

#
# Don't mess after here unless you know what you are doing!
#

DATA_WINDOW_ADDRESS = 0
POINTER_SIZE = 8

old_x86 = { "eax": 0, "ecx": 0, "edx": 0, "ebx": 0, "esp": 0, "ebp": 0, "esi": 0, "edi": 0, "eip": 0,
            "eflags": 0, "cs": 0, "ds": 0, "fs": 0, "gs": 0, "ss": 0, "es": 0 }

old_x64 = { "rax": 0, "rcx": 0, "rdx": 0, "rbx": 0, "rsp": 0, "rbp": 0, "rsi": 0, "rdi": 0, "rip": 0,
            "r8": 0, "r9": 0, "r10": 0, "r11": 0, "r12": 0, "r13": 0, "r14": 0, "r15": 0,
            "rflags": 0, "cs": 0, "fs": 0, "gs": 0 }

old_arm64 = { "x0": 0, "x1": 0, "x2": 0, "x3": 0, "x4": 0, "x5": 0, "x6": 0, "x7": 0, "x8": 0, "x9": 0, "x10": 0, 
              "x11": 0, "x12": 0, "x13": 0, "x14": 0, "x15": 0, "x16": 0, "x17": 0, "x18": 0, "x19": 0, "x20": 0, 
              "x21": 0, "x22": 0, "x23": 0, "x24": 0, "x25": 0, "x26": 0, "x27": 0, "x28": 0, "fp": 0, "lr": 0, 
              "sp": 0, "pc": 0, "cpsr": 0 }

GlobalListOutput = []

int3patches = {}

crack_cmds = []
crack_cmds_noret = []
modules_list = []

g_current_target = ""
g_target_hash = ""
g_home = ""
g_db = ""
g_dbdata = {}

# dyld modes
dyld_mode_dict = { 
    0: "dyld_image_adding",
    1: "dyld_image_removing",
    2: "dyld_image_info_change",
    3: "dyld_image_dyld_moved"
}

MIN_COLUMNS = 125
MIN_ROWS = 25
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

class QConsoleTextEditWindow(QMainWindow):
    
    mytext = "thread #1: tid = 0xa8f62d, 0x0000000100003f40 hello_world_test_loop`main, queue = \x1b[32m'com.apple.main-thread'\x1b[0m, stop reason = \x1b[31mbreakpoint 1.1\x1b[0m\nthread #2: tid = 0xa8f62d, 0x0000000100003f40 hello_world_test_loop`main, queue = \x1b[35m'com.apple.main-thread'\x1b[0m, stop reason = \x1b[36mbreakpoint 1.1\x1b[0m"
    debugger = None

    def __init__(self, debugger):
        super().__init__()
        self.debugger = debugger
        self.setWindowTitle(APP_NAME + " " + APP_VERSION)
        self.setBaseSize(WINDOW_SIZE * 2, WINDOW_SIZE)
        self.setMinimumSize(WINDOW_SIZE * 2, WINDOW_SIZE + 72)
        
        self.layout = QVBoxLayout()
        # self.layoutV = QHBoxLayout()

        self.centralWidget = QWidget(self)
        self.centralWidget.setLayout(self.layout)
        self.setCentralWidget(self.centralWidget)
        self.txtConsole = QConsoleTextEdit()
        self.cmdTest = QPushButton("CONTINUE")
        self.cmdTest.clicked.connect(self.interruptProcess)
        self.cmdTest2 = QPushButton("STEP NEXT")
        self.cmdTest2.clicked.connect(self.stepNextProcess)
        self.cmdTest3 = QPushButton("RE READ")
        self.cmdTest3.clicked.connect(self.readProcess)
        self.cmdTest4 = QPushButton("DI")
        self.cmdTest4.clicked.connect(self.readProcess2)
        self.layout.addWidget(self.cmdTest)
        self.layout.addWidget(self.cmdTest2)
        self.layout.addWidget(self.cmdTest3)
        self.layout.addWidget(self.cmdTest4)
        self.txtOutput = QConsoleTextEdit()
        self.txtOutput.setFont(QFont("Courier New"))
        self.layout.addWidget(self.txtOutput)
        self.txtConsole.setText(self.mytext)
        # self.txtConsole.appendText(self.mytext)
        
    def interruptProcess(self):
        res = lldb.SBCommandReturnObject()
        ci = self.debugger.GetCommandInterpreter()
        # ci.HandleCommand("re read", res)
        ci.HandleCommand("continue", res)
        print(res.GetOutput())
        self.txtOutput.appendEscapedText(res.GetOutput())
        # ci.HandleCommand("n", res)

    def stepNextProcess(self):
        res = lldb.SBCommandReturnObject()
        ci = self.debugger.GetCommandInterpreter()
        # ci.HandleCommand("re read", res)
        ci.HandleCommand("n", res)
        print(res.GetOutput())
        self.txtOutput.appendEscapedText(res.GetOutput())
        # ci.HandleCommand("n", res)

    def readProcess(self):
        res = lldb.SBCommandReturnObject()
        ci = self.debugger.GetCommandInterpreter()
        # ci.HandleCommand("re read", res)
        ci.HandleCommand("re read", res)
        print(res.GetOutput())
        self.txtOutput.appendEscapedText(res.GetOutput())
        # ci.HandleCommand("n", res)

    def readProcess2(self):
        res = lldb.SBCommandReturnObject()
        ci = self.debugger.GetCommandInterpreter()
        # ci.HandleCommand("re read", res)
        ci.HandleCommand("di", res)
        print(res.GetOutput())
        self.txtOutput.appendEscapedText(res.GetOutput())

    # we hook this so we have a chance to initialize/reset some stuff when targets are (re)run

        

#def close_application():
#   pass
    
#global pymobiledevice3GUIApp
#pymobiledevice3GUIApp = QApplication([])
#pymobiledevice3GUIApp.aboutToQuit.connect(close_application)
#
#pymobiledevice3GUIWindow = QConsoleTextEditWindow()
#pymobiledevice3GUIWindow.show()
#
#sys.exit(pymobiledevice3GUIApp.exec())

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
    ci.HandleCommand("settings set prompt \"(lldbtest) \"", res)
    ci.HandleCommand("settings set stop-disassembly-count 0", res)
    # set the log level - must be done on startup?
    ci.HandleCommand("settings set target.process.extra-startup-command QSetLogging:bitmask=" + CONFIG_LOG_LEVEL + ";", res)
    if CONFIG_USE_CUSTOM_DISASSEMBLY_FORMAT == 1:
        ci.HandleCommand("settings set disassembly-format " + CUSTOM_DISASSEMBLY_FORMAT, res)

    # the hook that makes everything possible :-)
    ci.HandleCommand("command script add -h '(lldbtest)' -f lldbtest.TestCommand TestCommand", res)
    ci.HandleCommand("command alias -h '(lldbinit) Start the python GUI.' -- pygui TestCommand", res)

    ci.HandleCommand("command script add -h '(lldbtest) Start the target and stop at entrypoint.' -f lldbtest.cmd_run r", res)
    ci.HandleCommand("command alias -h '(lldbtest) Start the target and stop at entrypoint.' -- run r", res)


def TestCommand(debugger, command, result, dict):
    print("Hello World - TestCommand!!!")

    pymobiledevice3GUIApp = QApplication([])
    # pymobiledevice3GUIApp.aboutToQuit.connect(close_application)

    pymobiledevice3GUIWindow = QConsoleTextEditWindow(debugger)
    pymobiledevice3GUIWindow.show()

    sys.exit(pymobiledevice3GUIApp.exec())
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