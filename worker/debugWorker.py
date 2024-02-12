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
	debugStepCompleted = pyqtSignal(object, bool, str)
#	debugValue = pyqtSignal(int, str, str, str)
	updateRegisterValue = pyqtSignal(int, str, str, str)

class DebugWorker(BaseWorker):
	
	kind = StepKind.StepOver
	
	def __init__(self, driver, kind):
		super(DebugWorker, self).__init__(driver)
#		print("INIT DEBUGWORKER")
		self.kind = kind
#		self.initTabs = initTabs
#		self.driver = drivers
		
		self.signals = DebugWorkerSignals()
		
	def workerFunc(self):
		super(DebugWorker, self).workerFunc()
		
		self.sendStatusBarUpdate("Debug step ...")
		target = self.driver.getTarget()
		process = target.GetProcess()
		if process:
#			print("HAS PROCESS")
			thread = process.GetThreadAtIndex(0)
			if thread:
#				print("HAS THREAD")
				
				if self.kind == StepKind.StepInto:
					thread.StepInstruction(False)
				elif self.kind == StepKind.Continue:
#					thread.Continue()
					error = process.Continue()
#					self.start_debugWorker(self.driver, StepKind.Continue)
					print("After Continue ...")
					if error:
						print(error)
				else:
					thread.StepInstruction(True)
					
#				print("HAS THREAD - STEPPED")
				frame = thread.GetFrameAtIndex(0)
				if frame:
#					print("HAS FRAME")
					registerList = frame.GetRegisters()
#					print(
#						"Frame registers (size of register set = %d):"
#						% registerList.GetSize()
#					)
					numRegisters = registerList.GetSize()
					if numRegisters > 0:
#						print(f"DEBUGGER GOT NEXT REGISTER: {frame.register['rip'].value}")
						self.signals.debugStepCompleted.emit(self.kind, True, frame.register["rip"].value)
						pass
					else:
#						print("DEBUGGER HAS NOOOOOOO REGISTER")
						self.signals.debugStepCompleted.emit(self.kind, False, '')
						pass
#					numRegSeg = 100 / numRegisters
#					currReg = 0
#					for value in registerList:
#						currReg += 1
#						currRegSeg = 100 / numRegisters * currReg
#						self.sendProgressUpdate(100 / numRegisters * currReg, f'Loading registers for {value.GetName()} ...')
#						# print value
##						print(
##							"%s (number of children = %d):"
##							% (value.GetName(), value.GetNumChildren())
##						)
#						if self.initTabs:
#							self.signals.Debug.emit(value.GetName())
#						
#						numChilds = len(value)
#						idx = 0
#						for child in value:
#							idx += 1
#							self.sendProgressUpdate((100 / numRegisters * currReg) + (numRegSeg / numChilds * idx), f'Loading registers value {child.GetName()} ...')
#							if self.initTabs:
#								self.signals.DebugValue.emit(currReg - 1, child.GetName(), child.GetValue(), getMemoryValueAtAddress(target, process, child.GetValue()))
#							else:
#								self.signals.updateRegisterValue.emit(currReg - 1, child.GetName(), child.GetValue(), getMemoryValueAtAddress(target, process, child.GetValue()))
				else:
					print("NO FRAME")
			else:
				print("NO THREAD")
		else:
			print("NO PROCESS")
		self.signals.finished.emit()
		pass