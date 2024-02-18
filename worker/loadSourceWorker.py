#!/usr/bin/env python3

import lldb
from lldbutil import print_stacktrace
from helper.inputHelper import FBInputHandler
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

import helper.lldbHelper

interruptLoadSourceCode = False

class LoadSourceCodeReceiver(QObject):
	interruptLoadSource = pyqtSignal()
	
class LoadSourceCodeWorkerSignals(QObject):
	finished = pyqtSignal(str)
#	addLine = pyqtSignal(int, str)
	
class LoadSourceCodeWorker(QRunnable):
	
	sourceFile = ''
	debugger = None
	lineNum = 1
	
	def __init__(self, debugger, sourceFile, data_receiver, lineNum):
		super(LoadSourceCodeWorker, self).__init__()
		self.isLoadSourceCodeActive = False
		self.debugger = debugger
		self.sourceFile = sourceFile
		self.data_receiver = data_receiver
		self.lineNum = lineNum
		self.signals = LoadSourceCodeWorkerSignals()
		self.data_receiver.interruptLoadSource.connect(self.handle_interruptLoadSourceCode)
		
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
		
		# Create the filespec for 'main.c'.
		filespec = lldb.SBFileSpec(self.sourceFile, False)
		source_mgr = self.debugger.GetSourceManager()
		# Use a string stream as the destination.
		stream = lldb.SBStream()
		source_mgr.DisplaySourceLinesWithLineNumbers(filespec, self.lineNum, self.lineNum, 85, '=>', stream)
#		print(stream.GetData())
		
		
		self.isLoadSourceCodeActive = False
		self.signals.finished.emit(stream.GetData())
		QCoreApplication.processEvents()
		
	def handle_interruptLoadSourceCode(self):
#		print(f"Received interrupt in the sysLog worker thread")
		interruptLoadSourceCode = True
		QCoreApplication.processEvents()
		pass