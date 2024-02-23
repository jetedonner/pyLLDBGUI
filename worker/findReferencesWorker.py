#!/usr/bin/env python3
from worker.baseWorker import *
from helper.dbgHelper import *

#class FindReferencesWorkerReceiver(BaseWorkerReceiver):
#	interruptWorker = pyqtSignal()
	
class FindReferencesWorkerSignals(BaseWorkerSignals):
	pass
	referenceFound = pyqtSignal(str, object)
#	loadBreakpoints = pyqtSignal(str)
#	loadBreakpointsValue = pyqtSignal(int, int, str, str, int, str, bool, bool, object)
#	updateBreakpointsValue = pyqtSignal(int, int, str, str, int, str, bool, bool, object)
#	updateRegisterValue = pyqtSignal(int, str, str, str)

class FindReferencesWorker(BaseWorker):
	
	initTable = True
	address = ""
	
	def __init__(self, driver, address, initTable = True):
		super(FindReferencesWorker, self).__init__(driver)
		
		self.address = address
		self.initTable = initTable
		
		self.signals = FindReferencesWorkerSignals()
		
	def workerFunc(self):
		super(FindReferencesWorker, self).workerFunc()
		
		self.sendStatusBarUpdate("Finding references to address: '{self.address}' ...")
		self.target = self.driver.getTarget()

		print(f"Finding references to address: '{self.address}'")
		
		thread = self.target.GetProcess().GetSelectedThread()
		idxOuter = 0
		for module in self.target.module_iter():
			if idxOuter != 0:
				idxOuter += 1
				continue
			idx = 0
			for section in module.section_iter():
				if section.GetName() == "__TEXT":
					if idx != 1:
						idx += 1
						continue
					for subsec in section:
						if subsec.GetName() == "__text":
							idxSym = 0
							lstSym = module.symbol_in_section_iter(subsec)
							secLen = module.num_symbols #len(lstSym)
							for sym in lstSym:
								print(sym)
								symFuncName = sym.GetStartAddress().GetFunction().GetName()
#								print(f'sym.GetStartAddress().GetFunction() => {sym.GetStartAddress().GetFunction()}')
								for instruction in sym.GetStartAddress().GetFunction().GetInstructions(self.target):
									if symFuncName == instruction.GetAddress().GetFunction().GetName():
#										print(str(instruction.GetOperands(self.target)))
										if self.address in str(instruction.GetOperands(self.target)):
											print(f"Reference to '{self.address}' found at address: {hex(int(str(instruction.GetAddress().GetFileAddress()), 10))}")
											self.signals.referenceFound.emit(self.address, instruction)
#										print(f"Address: {instruction.GetAddress()}")
#										print(f"Instruction: {instruction}")
#										print(f'sym.GetName() => {sym.GetName()} / instruction.GetAddress().GetFunction().GetName() => {instruction.GetAddress().GetFunction().GetName()}')
#										print(f'COMMENT => {instruction.GetComment(self.target)}')
#										self.signals.loadInstruction.emit(instruction)
#										for i in range(self.rowCount()):
#							#				if self.item(i, 5) != None and self.address in self.item(i, 5).text():
#							#					print(f'Reference found at address: {self.item(i, 3).text()}')
								idxSym += 1
								self.sendProgressUpdate((idxSym * 100) / secLen, "Finding reference to {self.address} ...")
							break
					break
				idx += 1
			idxOuter += 1
		pass
		

		