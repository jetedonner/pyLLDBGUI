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

#import time
#from gi.repository import Gdk, Gtk, GObject

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

fname = "main"
exe = "/Users/dave/Downloads/hello_world/hello_world_test"

global debugger
debugger = None

global process
process = None

global target
target = None

global thread
thread = None

interruptTargetLoad = False

class TargetLoadReceiver(QObject):
	interruptTargetLoad = pyqtSignal()
	
class TargetLoadWorkerSignals(QObject):
	finished = pyqtSignal()
	sendProgressUpdate = pyqtSignal(int)
	loadRegister = pyqtSignal(str)
	loadRegisterValue = pyqtSignal(int, str, str, str)
	loadProcess = pyqtSignal(object)
	loadThread = pyqtSignal(int, object)
	addInstruction = pyqtSignal(str, bool, bool, bool, str)
	
	addInstructionNG = pyqtSignal(str, str, str, str, bool, bool, bool, str, str)
	
	setTextColor = pyqtSignal(str, bool)
	
class TargetLoadWorker(QRunnable):
	
	targetPath = "/Users/dave/Downloads/hello_world/hello_world_test"
	window = None
	inputHandler = None
	
	debugger = None
	target = None
	process = None
	thread = None
	
	def inputCallback(self, data):
		print(data)
		
	def __init__(self, window_obj, target = "/Users/dave/Downloads/hello_world/hello_world_test"):
		super(TargetLoadWorker, self).__init__()
		self.isTargetLoadActive = False
		self.window = window_obj
		self.targetPath = target
		self.signals = TargetLoadWorkerSignals()
		
	def run(self):
		QCoreApplication.processEvents()
		self.runTargetLoad()
		
	def convert_address(self, address):
		# Get the address to be converted
#       address = "0x0000000100003f5f"
		
		# Convert the address to hex
		converted_address = int(address, 16)
		
		# Print the converted address
#       print("Converted address:", hex(converted_address))
		return hex(converted_address)
	
#	def handle_readMemory(self, debugger, address = 0xdeadbeef, data_size = 0x1000):
#		#       my_address = 0xdeadbeef  # change for some real address
#		#       my_data_size = 0x1000  # change for some real memory size
#		
#		error_ref = lldb.SBError()
#		process = debugger.GetSelectedTarget().GetProcess()
#		memory = process.ReadMemory(address, data_size, error_ref)
#		if error_ref.Success():
#			# `memory` is a regular byte string
#			print(f'{memory}')
#			pass
#		else:
#			print(str(error_ref))
			
	def runTargetLoad(self):
		if self.isTargetLoadActive:
			interruptTargetLoad = True
			return
		else:
			interruptTargetLoad = False
		QCoreApplication.processEvents()
		self.isTargetLoadActive = True
		
		self.sendProgressUpdate(5)
		
		
		# Create a new debugger instance
		self.debugger = lldb.SBDebugger.Create()
		
		global debugger
		debugger = self.debugger
		
		# When we step or continue, don't return from the function until the process
		# stops. We do this by setting the async mode to false.
		debugger.SetAsync(False)
		
#       for i in dir(debugger):
#           print(i)
#       {lldb.getVersion()}
		print(f"VEARSION: {sys.modules['lldb'].__file__} / {debugger.GetVersionString()}")
		
#       print(lldb)
		
#       for i in dir(lldb):
#           print(i)
#       self.inputHandler = FBInputHandler(debugger, self.inputCallback)
		
		print(f'debugger: {debugger}')
		# Create a target from a file and arch
		print("Creating a target for '%s'" % self.targetPath)
		
		
		self.target = debugger.CreateTargetWithFileAndArch(self.targetPath, None) # lldb.LLDB_ARCH_DEFAULT)
		global target
		target = self.target
		
		if self.target:
			self.sendProgressUpdate(10)
#			print("Has target")
			
			# If the target is valid set a breakpoint at main
			main_bp = self.target.BreakpointCreateByName(fname, self.target.GetExecutable().GetFilename())
			error = main_bp.SetScriptCallbackBody("\
			print 'Hit breakpoint callback'")
#           main_bp.SetScriptCallbackFunction('disasm_ui.breakpoint_cb')
#           main_bp.SetAutoContinue(auto_continue=True)
			print(main_bp)
			
			# Launch the process. Since we specified synchronous mode, we won't return
			# from this function until we hit the breakpoint at main
			
			self.process = target.LaunchSimple(None, None, os.getcwd())
			global process
			process = self.process
#           process.Stop()
#           self.inputHandler.start()
#			print(self.process)
			
			# Make sure the launch went ok
			if self.process:
#				self.executeCmd()
#				self.handle_readMemory(self.debugger, 0x108a01b90, 0x100)
				
#				for fun in dir(self.process):
#					print(fun)
#               for module in process.GetLoadedModules():
#                   for symbol in module.GetSymbols():
#                       if symbol.GetType() == lldb.SBSymbolType.ST_Import:
#                           print(symbol.GetName())
					
					
				self.signals.loadProcess.emit(self.process)
				QCoreApplication.processEvents()
				self.sendProgressUpdate(15)
#				print("Process launched OK")
				# Print some simple process info
				state = self.process.GetState()
#				print(self.process)
				if state == lldb.eStateStopped:
					print("state == lldb.eStateStopped")
					
					
#					print(f'GetNumQueues: {self.process.GetNumQueues()}')
#					for que in range(self.process.GetNumQueues()):
#						print(f'process.GetQueueAtIndex({que}) {self.process.GetQueueAtIndex(que)}')
#						
#					print(f'GetNumThreads: {self.process.GetNumThreads()}')
#					# Get the first thread
#					for thrd in range(self.process.GetNumThreads()):
#						print(f'process.GetThreadAtIndex({thrd}) {self.process.GetThreadAtIndex(thrd).GetIndexID()}')
						
					idxThread = 0
					
					
					self.thread = self.process.GetThreadAtIndex(0)
					global thread
					thread = self.thread
					if self.thread:
						
						
						
#                       # Get the current register state
#                       register_state = thread.GetThreadState()
#                   
#                       # Get the RIP register value
#                       rip_value = register_state.GetRegisterValue("rip")
#                   
#                       # Print the RIP value
#                       print("Current RIP:", hex(rip_value))
						
#                       # Get the current instruction address
#                       instruction_address = thread.GetInstructionAddress()
#                   
#                       # Get the current instruction location
#                       instruction_location = lldb.SBInstructionLocation(process, instruction_address)
#                   
#                       # Get the file and line number where the instruction is located
#                       file_name, line_number = instruction_location.GetLineEntry().GetFileNameAndLine()
#                   
#                       # Print the file and line number
#                       print("Current instruction location:", file_name, line_number)
						
						self.signals.loadThread.emit(idxThread, self.thread)
						QCoreApplication.processEvents()
						idxThread += 1
						self.sendProgressUpdate(20)
						# Print some simple thread info
#						print(self.thread)
						print_stacktrace(self.thread)
						print(f'GetNumFrames: {self.thread.GetNumFrames()}')
						
						for idx2 in range(self.thread.GetNumFrames()):
							
							# Get the first frame
							frame = self.thread.GetFrameAtIndex(idx2)
							if frame:
								self.sendProgressUpdate(25)
								# Print some simple frame info
								print(frame)
								
								print(f'AAAAA >>>> {hex(frame.GetPC())}')
								
								if idx2 == 0:
									rip = self.convert_address(frame.register["rip"].value)
#									print(rip)
									function = frame.GetFunction()
									# See if we have debug info (a function)
									if function:
										# We do have a function, print some info for the
										# function
										print(function)
										
		#                               for functionNG2 in dir(function):
		#                                   print(functionNG2)
										
										# Now get all instructions for this function and print
										# them
										insts = function.GetInstructions(self.target)
										self.disassemble_instructions(insts, rip)
									else:
										# See if we have a symbol in the symbol table for where
										# we stopped
										symbol = frame.GetSymbol()
										if symbol:
											# We do have a symbol, print some info for the
											# symbol
											print(symbol)
											
		#                                   print(f'DisplayName: {symbol.GetName()}')
											# Now get all instructions for this symbol and
											# print them
											insts = symbol.GetInstructions(self.target)
											self.disassemble_instructions(insts, rip)
											
		#                                   for functionNG2 in dir(symbol):
		#   #                                   if functionNG2.startswith("__"):
		#   #                                       continue
		#                                       print(functionNG2)
											
									registerList = frame.GetRegisters()
									print(
										"Frame registers (size of register set = %d):"
										% registerList.GetSize()
									)
									self.sendProgressUpdate(30)
									currReg = 0
									for value in registerList:
										# print value
										print(
											"%s (number of children = %d):"
											% (value.GetName(), value.GetNumChildren())
										)
										self.signals.loadRegister.emit(value.GetName())
		#                               continue
		#                               registerNode = QTreeWidgetItem(self.treRegister, [value.GetName() + " (" + str(value.GetNumChildren()) + ")", '', ''])
		#                               QTreeWidgetItem(self.treRegister, ['Floating point register', 'eax', '0x5'])
										for child in value:
		#                                   print(
		#                                       "Name: ", child.GetName(), " Value: ", child.GetValue()
		#                                   )
											
		#                                   variable_type = type(child.GetValue())
											
		#                                   print(f"The type of child.GetValue() is: {variable_type}")
											
											memoryValue = ""
											try:
												
												# Specify the memory address and size you want to read
												size = 32  # Adjust the size based on your data type (e.g., int, float)
												
												# Read memory and print the result
												data = self.read_memory(self.process, target.ResolveLoadAddress(int(child.GetValue(), 16)), size)
												
												hex_string = ''.join("%02x" % byte for byte in data)
												
												formatted_hex_string = ' '.join(re.findall(r'.{2}', hex_string))
												memoryValue = formatted_hex_string
		#                                       if data:
		#                                           print(f"Data at address {hex(address)}: {data}\n{formatted_hex_string}")
											except Exception as e:
		#                                       print(f"Error getting memory for addr: {e}")
												pass
												
											self.signals.loadRegisterValue.emit(currReg, child.GetName(), child.GetValue(), memoryValue)
											QCoreApplication.processEvents()
											
										currProg = (registerList.GetSize() - currReg)
										self.sendProgressUpdate(30 + (70 / currProg))
										currReg += 1
										
			else:
				print("Process NOT launched!!!")
		else:
			print("Has NO target")
			
		self.isTargetLoadActive = False
#       self.treeWidget.setEnabled(True)
#       QCoreApplication.processEvents()
		self.signals.finished.emit()
		QCoreApplication.processEvents()
		
#	def executeCmd(self):
#		# This causes an error and the callback is never called.
#		opt = lldb.SBExpressionOptions()
#		opt.SetIgnoreBreakpoints(False)
#		
#		global target
#		print("EXECUTING COMMAND:")
#		# Execute the "re read" command
#		result = target.EvaluateExpression("re read", opt)
#		
#		# Print the result
#		print(result.GetSummary())
		
	def sendProgressUpdate(self, progress):
		self.signals.sendProgressUpdate.emit(int(progress))
		QCoreApplication.processEvents()
		
	def handle_interruptTargetLoad(self):
#		print(f"Received interrupt in the sysLog worker thread")
#		self.isSysLogActive = False
		pass
		
	def extract_address(self, string):
		pattern = r'\[0x([0-9a-fA-F]+)\]'
		
		# Use re.search to find the match
		match = re.search(pattern, string)
		
		if match:
			hex_value = match.group(1)
			return hex_value
		else:
			print("No hex value found in the string.")
			return ""
		
	def read_memory(self, process, address, size):
		error = lldb.SBError()
		target = process.GetTarget()
		
		# Read memory using ReadMemory function
		data = target.ReadMemory(address, size, error)
		
		if error.Success():
			return data
		else:
			print("Error reading memory:", error)
			return None
		
	def disassemble_instructions(self, insts, rip):
		global target
		for i in insts:
			address = self.extract_address(f'{i}')
#           self.signals.addInstruction(.emit(f'0x{address}:\t{i.GetMnemonic(target)}\t{i.GetOperands(target)}', True, True, False, "black")
			self.signals.addInstructionNG.emit(f'0x{address}', f'{i.GetMnemonic(target)}\t{i.GetOperands(target)}', f'{i.GetComment(target)}', f'{i.GetData(target)}', True, True, False, "black", rip)
			
			QCoreApplication.processEvents()