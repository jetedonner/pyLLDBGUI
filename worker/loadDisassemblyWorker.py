#!/usr/bin/env python3
from lldb import *

from worker.baseWorker import *
from helper.dbgHelper import *

#class LoadDisassemblyWorkerReceiver(BaseWorkerReceiver):
#	interruptWorker = pyqtSignal()
	
class LoadDisassemblyWorkerSignals(BaseWorkerSignals):
	loadInstruction = pyqtSignal(object)
#	loadBreakpoints = pyqtSignal(str)
#	loadBreakpointsValue = pyqtSignal(int, int, str, str, int, str, bool, bool, object)
#	updateBreakpointsValue = pyqtSignal(int, int, str, str, int, str, bool, bool, object)
#	updateRegisterValue = pyqtSignal(int, str, str, str)
	pass
	
class LoadDisassemblyWorker(BaseWorker):
	
#	initTable = True
		
	def __init__(self, driver, initTable = True):
		super(LoadDisassemblyWorker, self).__init__(driver)
		self.initTable = initTable
		
		self.signals = LoadDisassemblyWorkerSignals()
		
	def workerFunc(self):
		super(LoadDisassemblyWorker, self).workerFunc()
		
		self.sendStatusBarUpdate("Reloading disassembly ...")
		self.target = self.driver.getTarget()
						
		# Get the target
#		target = lldb.debugger.GetSelectedTarget()
		
		# Disassemble the entire target
		self.disassemble_entire_target(self.target)
		
	def disassemble_entire_target(self, target):
		"""Disassembles instructions for the entire target.
	
		Args:
			target: The SBTarget object representing the debugged process.
		"""
		
		thread = self.target.GetProcess().GetSelectedThread()
#		print(f'thread.GetFrameAtIndex(0) => {thread.GetFrameAtIndex(0)}')
		
		idxOuter = 0
		for module in self.target.module_iter():
			if idxOuter != 0:
				idxOuter += 1
				continue
			idx = 0
			for section in module.section_iter():
				# Check if the section is readable
#				if not section.IsReadable():
#					continue
				
				if section.GetName() == "__TEXT":
#					print(f'section => {section}')
					# Get section start and size
#					start_address = section.GetLoadAddress(self.target)
#					print(f'start_address => {start_address} / {hex(start_address)}')
#					size = section.GetByteSize()
					if idx != 1:
						idx += 1
						continue
					
#					print('Number of subsections: %d' % section.GetNumSubSections())
					for subsec in section:
#						print(repr(subsec))
						if subsec.GetName() == "__text":
#							print("GOTIT!!!!!")
							
							idxSym = 0
							lstSym = module.symbol_in_section_iter(subsec)
							secLen = module.num_symbols #len(lstSym)
							for sym in lstSym:
#								print(f'get_instructions_from_current_target => {sym.get_instructions_from_current_target()}')
#								if idxSym != 0:
#									idxSym += 1
#									continue
#								print(sym)
#							continue
#								start_address = sym.GetStartAddress().GetLoadAddress(self.target)
#								end_address = sym.GetEndAddress().GetLoadAddress(self.target)
#								size = end_address - start_address
#								print(f'start_address => {start_address} / {hex(start_address)}, end_address => {end_address} / {hex(end_address)}  => SIZE: {size}')
#								print(sym)
								symFuncName = sym.GetStartAddress().GetFunction().GetName()
#								print(f'sym.GetName() => {sym.GetName()} / sym.GetStartAddress().GetFunction().GetName() => {sym.GetStartAddress().GetFunction().GetName()}')
###								start_address = subsec.GetLoadAddress(self.target)
###								print(f'start_address => {start_address} / {hex(start_address)}')
###								size = subsec.GetByteSize()
##								
###								print(f'start_address => {start_address} / {hex(start_address)} => SIZE: {size}')
##								# Disassemble instructions in chunks
#								chunk_size = 1024
#								remaining_bytes = size
##								while remaining_bytes > 0:  and start_address <= end_address:
#								while start_address < end_address:
#									# Read a chunk of data
#									data_size = min(remaining_bytes, chunk_size)
#									print(f'sym.GetName() => {sym.GetName()} / SBAddress(start_address, self.target).GetFunction().GetName() => {SBAddress(start_address, self.target).GetFunction().GetName()}')
#									instructions = self.target.ReadInstructions(SBAddress(start_address, self.target), data_size)
#									print(f'instructions-Len {len(instructions)}')
##									# Disassemble and handle instructions
#									for instruction in instructions:
#										if symFuncName == instruction.GetAddress().GetFunction().GetName():
#											print(f"Address: {instruction.GetAddress()}")
#											print(f"Instruction: {instruction}")
#											print(f'sym.GetName() => {sym.GetName()} / instruction.GetAddress().GetFunction().GetName() => {instruction.GetAddress().GetFunction().GetName()}')
#											self.signals.loadInstruction.emit(instruction)
#										
#									# Update addresses and remaining bytes
#									start_address += data_size
#									remaining_bytes -= data_size
#									print(f'start_address => {start_address} / remaining_bytes => {remaining_bytes} / data_size => {data_size}')
##								(50*100)/200
#								print(f'sym.GetStartAddress().GetFunction() => {sym.GetStartAddress().GetFunction()}')
								for instruction in sym.GetStartAddress().GetFunction().GetInstructions(self.target):
									if symFuncName == instruction.GetAddress().GetFunction().GetName():
#										print(f"Address: {instruction.GetAddress()}")
#										print(f"Instruction: {instruction}")
#										print(f'sym.GetName() => {sym.GetName()} / instruction.GetAddress().GetFunction().GetName() => {instruction.GetAddress().GetFunction().GetName()}')
#										print(f'COMMENT => {instruction.GetComment(self.target)}')
										self.signals.loadInstruction.emit(instruction)
								
								idxSym += 1
								self.sendProgressUpdate((idxSym * 100) / secLen, "Disassembling executable ...")
							break
					break
	#				# Disassemble instructions in chunks
	#				chunk_size = 1024
	#				remaining_bytes = size
	#				while remaining_bytes > 0:
	#					# Read a chunk of data
	#					data_size = min(remaining_bytes, chunk_size)
	#					instructions = self.target.ReadInstructions(SBAddress(start_address, self.target), data_size)
	#					
	#					# Disassemble and handle instructions
	#					for instruction in instructions:
	#						print(f"Address: {instruction.GetAddress()}")
	#						print(f"Instruction: {instruction}")
	#						
	#					# Update addresses and remaining bytes
	#					start_address += data_size
	#					remaining_bytes -= data_size
				idx += 1
			idxOuter += 1
#		target
#		frame = self.thread.GetFrameAtIndex(0)
#		if frame:
#			print(frame)
#			rip = lldbHelper.convert_address(frame.register["rip"].value)
#			
#			########################################################################
#			i = 0
#			addr = frame.GetPCAddress()
#			load_addr = addr.GetLoadAddress(target)
#			function = frame.GetFunction()
#			mod_name = frame.GetModule().GetFileSpec().GetFilename()
##							print(f'load_addr: {load_addr}')
#			if not function:
#				# No debug info for 'function'.
#				symbol = frame.GetSymbol()
#				file_addr = addr.GetFileAddress()
#				start_addr = symbol.GetStartAddress().GetFileAddress()
#				symbol_name = symbol.GetName()
#				symbol_offset = file_addr - start_addr
##								print(f'symbol_name: {symbol_name}')
##								with open("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/my_output.txt", "w") as output:
##								print('  frame #{num}: {addr:#016x} {mod}`{symbol} + {offset}'.format(num=i, addr=load_addr, mod=mod_name, symbol=symbol_name, offset=symbol_offset))
#			else:
#				# Debug info is available for 'function'.
#				func_name = frame.GetFunctionName()
#				file_name = frame.GetLineEntry().GetFileSpec().GetFilename()
#				line_num = frame.GetLineEntry().GetLine()
##								print(f'function.GetStartAddress().GetFileAddress(): {function.GetStartAddress().	GetFileAddress()}')
##								print(f'func_name: {func_name}')
###								with open("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/my_output.txt", "w") as output:
##								print('  frame #{num}: {addr:#016x} {mod}`{func} at {file}:{line} {args}'.format(num=i, addr=load_addr, mod=mod_name, func='%s [inlined]' % func_name if frame.IsInlined() else func_name, file=file_name, line=line_num, args=get_args_as_string(frame, showFuncName=False))) #args=get_args_as_string(frame, showFuncName=False)), output)
#				
#				
#				self.disassemble_instructions(function.GetInstructions(target), target, rip)
#		
##		idx = 0
##		for i in range(target.GetNumBreakpoints()):
##			idx += 1
##			bp_cur = target.GetBreakpointAtIndex(i)
##			for bl in bp_cur:
##				# Make sure the name list has the remaining name:
##				name_list = lldb.SBStringList()
##				bp_cur.GetNames(name_list)
##				num_names = name_list.GetSize()
##				
##				name = name_list.GetStringAtIndex(0)
##				if self.initTable:
##					self.signals.loadBreakpointsValue.emit(bp_cur.GetID(), bp_cur.GetID(), hex(bl.GetLoadAddress()), name, bp_cur.GetHitCount(), bp_cur.GetCondition(), self.initTable, bp_cur.IsEnabled(), bp_cur)
##				else:
##					self.signals.updateBreakpointsValue.emit(bp_cur.GetID(), bp_cur.GetID(), hex(bl.GetLoadAddress()), name, bp_cur.GetHitCount(), bp_cur.GetCondition(), self.initTable, bp_cur.IsEnabled(), bp_cur)
#								
##		self.signals.finished.emit()
#		pass
		

		