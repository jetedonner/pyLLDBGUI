#!/usr/bin/env python3

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

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

import lldbHelper

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
		
#		global debugger
		res = lldb.SBCommandReturnObject()
		
		
		# Get the command interpreter
		command_interpreter = lldbHelper.debugger.GetCommandInterpreter()
		
		# Execute the 'frame variable' command
		command_interpreter.HandleCommand(self.command, res)
#       print(f'{res}')
#       for i in dir(res):
#           print(i)
#       print(res.Succeeded())
#       print(res.GetError())
		
		self.isExecCommandActive = False
		self.signals.finished.emit(res)
		QCoreApplication.processEvents()
		
	def handle_interruptExecCommand(self):
#		print(f"Received interrupt in the sysLog worker thread")
#		self.isSysLogActive = False
		pass