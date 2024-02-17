#!/usr/bin/env python3

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

from QConsoleTextEdit import *

#APP_NAME = "ConsoleTextEditWindow-TEST"
#VERSION = "0.0.1"

APP_NAME = "LLDB-PyGUI"
APP_VERSION = "0.0.1"
APP_BUILD = "689"
PROMPT_TEXT = "LLDB-PyGUI"
#WINDOW_SIZE = 512
WINDOW_SIZE = 680

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