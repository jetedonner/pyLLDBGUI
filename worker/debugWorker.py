#!/usr/bin/env python3
from worker.baseWorker import *
from helper.dbgHelper import *

#class DebugWorkerReceiver(BaseWorkerReceiver):
#	interruptWorker = pyqtSignal()
	
from enum import Enum
#import re

class StepKind(Enum):
	StepOver = 1
	StepInto = 2
	StepOut = 4
	Continue = 8
	
class DebugWorkerSignals(BaseWorkerSignals):
	debugStepCompleted = pyqtSignal(object, bool, str, object)
#	debugValue = pyqtSignal(int, str, str, str)
	updateRegisterValue = pyqtSignal(int, str, str, str)
#	setPC = pyqtSignal(str)

class DebugWorker(BaseWorker):
	
	kind = StepKind.StepOver
	isRunning = False
	def __init__(self, driver, kind):
		super(DebugWorker, self).__init__(driver)
		self.kind = kind
		self.signals = DebugWorkerSignals()
		
	def workerFunc(self):
		super(DebugWorker, self).workerFunc()
		if not self.isRunning:
			self.isRunning = True
		else:
			return
		
		self.sendStatusBarUpdate("Debug step ...")
		target = self.driver.getTarget()
		process = target.GetProcess()
		if process:
			thread = process.GetThreadAtIndex(0)
			if thread:
				if self.kind == StepKind.StepInto:
					print("Trying to StepInto ...")
					thread.StepInstruction(False)
					if thread.GetStopReason() == lldb.eStopReasonBreakpoint:
						self.isRunning = False
					print("After StepInto ...")
				elif self.kind == StepKind.StepOut:
					print("Trying to StepOut ...")
					thread.StepOut()
					if thread.GetStopReason() == lldb.eStopReasonBreakpoint:
						self.isRunning = False
					print("After StepOut ...")
				elif self.kind == StepKind.StepOver:
					print("Trying to StepOver ...")
					thread.StepInstruction(True)
					print("After StepOver ...")
#					ID = thread.GetThreadID()
					if thread.GetStopReason() == lldb.eStopReasonBreakpoint:
						
#						print(f'GOT if thread.GetStopReason() == lldb.eStopReasonBreakpoint:')
#						frame = thread.GetFrameAtIndex(0)
#						self.signals.setPC.emit(frame.register["rip"].value)
#						QCoreApplication.processEvents()
						
#						from lldbutil import print_stacktrace
#						print_stacktrace(thread)
						self.isRunning = False
#					print("After StepOver ...")
				elif self.kind == StepKind.Continue:
					print("Trying to Continue ...")
					if thread.IsSuspended():
						print("thread.IsSuspended() => Trying to Resume ...")
						thread.Resume()
					error = process.Continue()
					print("After Continue ...")
					if error:
						print(error)

					if thread.GetStopReason() == lldb.eStopReasonBreakpoint:
						self.isRunning = False
				else:
					print("Trying to StepOver ...")
					thread.StepInstruction(True)
					print("After StepOver ...")
#					ID = thread.GetThreadID()
					if thread.GetStopReason() == lldb.eStopReasonBreakpoint:
#						print(f'GOT if thread.GetStopReason() == lldb.eStopReasonBreakpoint:')
#						from lldbutil import print_stacktrace
#						print_stacktrace(thread)
						self.isRunning = False
#					frame = thread.GetFrameAtIndex(0)
#					self.signals.setPC.emit(frame.register["rip"].value)
#					QCoreApplication.processEvents()
				
				
				frame = thread.GetFrameAtIndex(0)
				if frame:
					registerList = frame.GetRegisters()
					numRegisters = registerList.GetSize()
					if numRegisters > 0:
#						print(f'GetPCAddress => {hex(frame.GetPCAddress().GetFileAddress())}')
						self.signals.debugStepCompleted.emit(self.kind, True, frame.register["rip"].value, frame)
						self.isRunning = False
#						pass
					else:
						self.signals.debugStepCompleted.emit(self.kind, False, '', frame)
						self.isRunning = False
#						pass
				else:
					print("NO FRAME")
			else:
				print("NO THREAD")
		else:
			print("NO PROCESS")
#		self.signals.finished.emit()
		self.isRunning = False
#		pass