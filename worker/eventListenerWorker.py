#!/usr/bin/env python3

import lldb
#from lldbutil import print_stacktrace
#from inputHelper import FBInputHandler
#import psutil
#import os
#import os.path
#import sys
#import re
#import binascii
#import webbrowser
#import ctypes
#import time

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

#import lldbHelper

interruptEventListener = False

class EventListenerReceiver(QObject):
	interruptEventListener = pyqtSignal()
	
class EventListenerWorkerSignals(QObject):
	finished = pyqtSignal(object)
	
class EventListenerWorker(QRunnable):
	
	debugger = None
	
	def __init__(self, debugger, data_receiver):
		super(EventListenerWorker, self).__init__()
		self.debugger = debugger
		self.isEventListenerActive = False
		self.signals = EventListenerWorkerSignals()
		self.data_receiver = data_receiver
		self.data_receiver.interruptEventListener.connect(self.handle_interruptEventListener)
		
	def run(self):
		self.runEventListener()
		
	def runEventListener(self):
		if self.isEventListenerActive:
			interruptEventListener = True
			return
		else:
			interruptEventListener = False
		QCoreApplication.processEvents()
		self.isEventListenerActive = True
		
##		global debugger
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
#		
#		self.isEventListenerActive = False
#		self.signals.finished.emit(res)
#		QCoreApplication.processEvents()
		listener = self.debugger.GetListener()
		self.debugger.GetTargetAtIndex(0).GetProcess().Continue()
		# sign up for process state change events
		stop_idx = 0
		interruptEventListener = False
		while not interruptEventListener:
			event = lldb.SBEvent()
			if listener.WaitForEvent(lldb.UINT32_MAX, event):
				if lldb.SBProcess.EventIsProcessEvent(event):
					state = lldb.SBProcess.GetStateFromEvent(event)
					if state == lldb.eStateInvalid:
						# Not a state event
						print('process event = %s' % (event))
					else:
						print("process state changed event: %s" % (lldb.SBDebugger.StateAsCString(state)))
		self.signals.finished.emit(None)
		QCoreApplication.processEvents()

		
	def handle_interruptEventListener(self):
#		print(f"Received interrupt in the sysLog worker thread")
#		self.isSysLogActive = False
		interruptEventListener = True
		pass