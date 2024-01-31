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

interruptLoadSourceCode = False

class LoadSourceCodeReceiver(QObject):
	interruptLoadSourceCode = pyqtSignal()
	
class LoadSourceCodeWorkerSignals(QObject):
	finished = pyqtSignal(str)
#	addLine = pyqtSignal(int, str)
	
class LoadSourceCodeWorker(QRunnable):
	
	sourceFile = ''
	
	def __init__(self, sourceFile):
		super(LoadSourceCodeWorker, self).__init__()
		self.isLoadSourceCodeActive = False
		self.sourceFile = sourceFile
		self.signals = LoadSourceCodeWorkerSignals()
		
	def run(self):
		self.runLoadSourceCode()
		
	def runLoadSourceCode(self):
		if self.isLoadSourceCodeActive:
			interruptLoadSourceCode = True
			return
		else:
			interruptLoadSourceCode = False
		QCoreApplication.processEvents()
		self.isLoadSourceCodeActive = True
		
#		global debugger
#		res = lldb.SBCommandReturnObject()
#		
#		
#		# Get the command interpreter
#		command_interpreter = lldbHelper.debugger.GetCommandInterpreter()
#		
#		# Execute the 'frame variable' command
#		command_interpreter.HandleCommand(self.command, res)
##       print(f'{res}')
##       for i in dir(res):
##           print(i)
##       print(res.Succeeded())
##       print(res.GetError())
		
		# Create the filespec for 'main.c'.
		filespec = lldb.SBFileSpec(self.sourceFile, False)
		source_mgr = lldbHelper.debugger.GetSourceManager()
		# Use a string stream as the destination.
		stream = lldb.SBStream()
		source_mgr.DisplaySourceLinesWithLineNumbers(filespec, 1, 0, 64, '=>', stream)
#		print(stream.GetData())
		
		
		self.isLoadSourceCodeActive = False
		self.signals.finished.emit(stream.GetData())
		QCoreApplication.processEvents()
		
	def handle_interruptLoadSourceCode(self):
#		print(f"Received interrupt in the sysLog worker thread")
#		self.isSysLogActive = False
		pass