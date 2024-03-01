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

interruptBreakpoint = False

#class BreakpointReceiver(BaseWorkerSignals):
#	interruptBreakpoint = pyqtSignal()
	
class BreakpointWorkerSignals(BaseWorkerSignals):
	gotEvent = pyqtSignal(object)
	
class BreakpointWorker(BaseWorker):
	
	debugger = None
	queue = None
	
	def __init__(self, driver, queue):
#	def __init__(self, debugger, command):
		super(BreakpointWorker, self).__init__(driver)
#		super(BreakpointWorker, self).__init__()
#		self.isBreakpointActive = False
		self.debugger = driver.debugger
		self.queue = queue
#		self.command = command
		self.signals = BreakpointWorkerSignals()
		
#	def run(self):
#		self.runBreakpoint()
#		
#	def runBreakpoint(self):
	def workerFunc(self):
#		if self.isBreakpointActive:
#			interruptBreakpoint = True
#			return
#		else:
#			interruptBreakpoint = False
##		QCoreApplication.processEvents()
#		self.isBreakpointActive = True
		super(BreakpointWorker, self).workerFunc()
		
		while True:
#			global event_queueBP
#			item = event_queueBP.get()
			print("GETTING QUEUE EVENT !!!!!!!")
			item = self.queue.get()
			print(f'Working on {item}')
			self.signals.gotEvent.emit(item)
			QCoreApplication.processEvents()
			
#		res = lldb.SBCommandReturnObject()
#		# Get the command interpreter
#		command_interpreter = self.debugger.GetCommandInterpreter()
#		
#		# Execute the 'frame variable' command
#		command_interpreter.HandleCommand(self.command, res)
##		print(res)
#		self.isBreakpointActive = False
#		self.signals.commandCompleted.emit(res)
#		QCoreApplication.processEvents()
		
#	def handle_interruptBreakpoint(self):
#		print(f"Received interrupt in the exec command worker thread")
#		self.interruptBreakpoint = True
#		pass