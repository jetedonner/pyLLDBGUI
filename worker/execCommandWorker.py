#!/usr/bin/env python3

import lldb
#from lldbutil import print_stacktrace
#from helper.inputHelper import FBInputHandler
#import psutil
#import os
#import os.path
#import sys
#import re
#import binascii
#import webbrowser
#import ctypes
#import time
#
#from PyQt6.QtGui import *
#from PyQt6.QtCore import *
#
#from PyQt6.QtWidgets import *
#from PyQt6 import uic, QtWidgets

from worker.baseWorker import *
from helper.dbgHelper import *

interruptExecCommand = False

#class ExecCommandReceiver(BaseWorkerSignals):
#	interruptExecCommand = pyqtSignal()
	
class ExecCommandWorkerSignals(BaseWorkerSignals):
	commandCompleted = pyqtSignal(object)
	
class ExecCommandWorker(BaseWorker):
	
	debugger = None
	
	def __init__(self, driver, command):
#	def __init__(self, debugger, command):
		super(ExecCommandWorker, self).__init__(driver)
#		super(ExecCommandWorker, self).__init__()
		self.isExecCommandActive = False
		self.debugger = driver.debugger
		self.command = command
		self.signals = ExecCommandWorkerSignals()
		
#	def run(self):
#		self.runExecCommand()
#		
#	def runExecCommand(self):
	def workerFunc(self):
#		if self.isExecCommandActive:
#			interruptExecCommand = True
#			return
#		else:
#			interruptExecCommand = False
##		QCoreApplication.processEvents()
#		self.isExecCommandActive = True
		super(ExecCommandWorker, self).workerFunc()
		res = lldb.SBCommandReturnObject()
		# Get the command interpreter
		command_interpreter = self.debugger.GetCommandInterpreter()
		
		# Execute the 'frame variable' command
		command_interpreter.HandleCommand(self.command, res)
#		print(res)
		self.isExecCommandActive = False
		self.signals.commandCompleted.emit(res)
		QCoreApplication.processEvents()
		
#	def handle_interruptExecCommand(self):
#		print(f"Received interrupt in the exec command worker thread")
#		self.interruptExecCommand = True
#		pass