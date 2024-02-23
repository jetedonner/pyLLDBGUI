#!/usr/bin/env python3

import lldb
from lldb import *
import lldbutil
from lldbutil import *
import sys
from threading import Thread

import sys
import os
import subprocess
from sys import stdin, stdout
from threading import Thread

from PyQt6.QtCore import *
from PyQt6 import *

#from PyQt6.QtGui import *
#from PyQt6.QtCore import *
#
#from PyQt6 import uic, QtWidgets, QtCore
#
#from QConsoleTextEdit import *
#
#from lldbpyGUIConfig import *
#from lldbpyGUIWindow import *
#
#from config import *

class LLDBListener(QtCore.QObject, Thread):
	should_quit = False
	
	breakpointEvent = pyqtSignal(object)
	stdoutEvent = pyqtSignal(object)
	
	def __init__(self, process):
		super(LLDBListener, self).__init__()
		Thread.__init__(self)
		print('INITING LISTENER!!!!')
		self.listener = lldb.SBListener('Chrome Dev Tools Listener')
		self._add_listener_to_process(process)
		self._broadcast_process_state(process)
		self._add_listener_to_target(process.target)
		
	def _add_listener_to_target(self, target):
		# Listen for breakpoint/watchpoint events (Added/Removed/Disabled/etc).
		broadcaster = target.GetBroadcaster()
		mask = SBTarget.eBroadcastBitBreakpointChanged | SBTarget.eBroadcastBitWatchpointChanged | SBTarget.eBroadcastBitModulesLoaded | SBThread.eBroadcastBitThreadSuspended 
		broadcaster.AddListener(self.listener, mask)
		
	def _add_listener_to_process(self, process):
		# Listen for process events (Start/Stop/Interrupt/etc).
		broadcaster = process.GetBroadcaster()
		mask = SBProcess.eBroadcastBitStateChanged | SBProcess.eBroadcastBitSTDOUT
		broadcaster.AddListener(self.listener, mask)
		
	def _broadcast_process_state(self, process):
		state = 'stopped'
		if process.state == eStateStepping or process.state == eStateRunning:
			state = 'running'
		elif process.state == eStateExited:
			state = 'exited'
			self.should_quit = True
		thread = process.selected_thread
		print('Process event: %s, reason: %d' % (state, thread.GetStopReason()))
		if thread.GetStopReason() == lldb.eStopReasonBreakpoint:
			print(f'REASON BP RFEACHED => Continuing...')
#     error = lldb.SBError()
#     thread.Resume(error)
#     process.Continue()
			
			
			
			
	def _breakpoint_event(self, event):
		breakpoint = SBBreakpoint.GetBreakpointFromEvent(event)
		bpEventType = SBBreakpoint.GetBreakpointEventTypeFromEvent(event)
		self.breakpointEvent.emit(event)
		print(event)
		print(f'EVENTTYPE: {SBBreakpoint.GetBreakpointEventTypeFromEvent(event)}')
		print(dir(event))
		print(breakpoint)
		print(dir(breakpoint))
		print(f'==========>>>>>>>> ISENABLED: {breakpoint.IsEnabled()}')
		print('Breakpoint event: %s' % str(breakpoint))
		
	def run(self):
		print('STARTING LISTENER!!!!')
		while not self.should_quit:
			event = SBEvent()
			print("GOING to WAIT 4 EVENT...")
			if self.listener.WaitForEvent(lldb.UINT32_MAX, event):
				print("GOT NEW EVENT LISTENER!!")
				if event.GetType() == SBThread.eBroadcastBitThreadSuspended:
					print('THREAD SUSPENDED: %s' % str(event))
				elif event.GetType() == SBTarget.eBroadcastBitModulesLoaded:
					print('Module load: %s' % str(event))
					
				
				elif event.GetType() == lldb.SBProcess.eBroadcastBitSTDOUT:
					print("STD OUT EVENT LISTENER!!!")
					stdout = SBProcess.GetProcessFromEvent(event).GetSTDOUT(256)
					print(SBProcess.GetProcessFromEvent(event))
					print(stdout)
					if stdout is not None and len(stdout) > 0:
						message = {"status":"event", "type":"stdout", "output": "".join(["%02x" % ord(i) for i in stdout])}
						print(message)
						print("".join(["%02x" % ord(i) for i in stdout]))
						self.stdoutEvent.emit("".join(["%02x" % ord(i) for i in stdout]))
#             self.signals.event_output.emit("".join(["%02x" % ord(i) for i in stdout]))
						QCoreApplication.processEvents()
				elif SBProcess.EventIsProcessEvent(event):
					self._broadcast_process_state(SBProcess.GetProcessFromEvent(event))
					print("STD OUT EVENT ALT!!!")
				elif SBBreakpoint.EventIsBreakpointEvent(event):
					print("GOT BREAKPOINT EVENT YESSSSS!!!")
					self._breakpoint_event(event)
				elif event.GetType() == lldb.SBTarget.eBroadcastBitWatchpointChanged:
					wp = lldb.SBWatchpoint.GetWatchpointFromEvent(event)
					print(f"WATCHPOINT CHANGED!!!! => {wp}")
				else:
					print("OTHER EVENT!!!!")
		print("END LISTENER!!!")