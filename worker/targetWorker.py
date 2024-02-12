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

#import time
#from gi.repository import Gdk, Gtk, GObject

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

import helper.lldbHelper

fname = "main"
exe = "./hello_world_test"

interruptTargetLoad = False
#interruptTargetLoadSignal

def breakpointHandler(frame, bp_loc, dict):
	print("IIIIIIIIINNNNNNNN CCCCAAQALLLLLLBBBAAACCKKKK")
	
class TargetLoadReceiver(QObject):
	interruptTargetLoadSignal = pyqtSignal()
	
class TargetLoadWorkerSignals(QObject):
	finished = pyqtSignal()
	sendProgressUpdate = pyqtSignal(int)
	loadStats = pyqtSignal(str)
	loadRegister = pyqtSignal(str)
	loadSections = pyqtSignal(object)
	loadRegisterValue = pyqtSignal(int, str, str, str)
	loadProcess = pyqtSignal(object)
	loadThread = pyqtSignal(int, object)
	addInstruction = pyqtSignal(str, bool, bool, bool, str)
	
	addInstructionNG = pyqtSignal(str, str, str, str, bool, bool, bool, str, str)
	
	setTextColor = pyqtSignal(str, bool)
	
class TargetLoadWorker(QRunnable):
	
	interruptTargetLoad = False
	targetPath = "/Users/dave/Downloads/hello_world/hello_world"
	window = None
	inputHandler = None
	data_receiver = None
	
	def inputCallback(self, data):
		print(data)
		
	def __init__(self, window_obj, data_receiver, target = "/Users/dave/Downloads/hello_world/hello_world"):
		super(TargetLoadWorker, self).__init__()
		self.isTargetLoadActive = False
		self.window = window_obj
		self.targetPath = target
		self.data_receiver = data_receiver
		self.data_receiver.interruptTargetLoadSignal.connect(self.handle_interrupt)
		if lldbHelper.exec2Dbg is not None:
			self.targetPath = lldbHelper.exec2Dbg
#			print(f'loading TARGETPATH: {self.targetPath}')
			
		self.signals = TargetLoadWorkerSignals()
		
	def run(self):
		QCoreApplication.processEvents()
		self.runTargetLoad()
		
	def handle_interrupt(self):
		self.interruptTargetLoad = True
		pass
		
#	def convert_address(self, address):
#		# Get the address to be converted
##       address = "0x0000000100003f5f"
#		
#		# Convert the address to hex
#		converted_address = int(address, 16)
#		
#		# Print the converted address
##       print("Converted address:", hex(converted_address))
#		return hex(converted_address)
	
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
	
	def print_source_code_for_frame(self, frame):
		# Create the filespec for 'main.c'.
		filespec = lldb.SBFileSpec('/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/LLDBPyGUI/testtarget/hello_world_test.c', False)
		source_mgr = lldbHelper.debugger.GetSourceManager()
		# Use a string stream as the destination.
		stream = lldb.SBStream()
		source_mgr.DisplaySourceLinesWithLineNumbers(filespec, 1, 0, 64, '=>', stream)
		print(stream.GetData())
#		# Get the current source file and line number
#		file_spec = frame.GetLineEntry().GetFileSpec()
#		line_num = frame.GetLineEntry().GetLine()
#		
#		symbol_context = frame.GetSymbolContext(lldb.eSymbolContextLineEntry)
#		
#		# Get the compile unit for the module
#		compile_unit = symbol_context.GetCompileUnit()
#	
#		for lineEntry in compile_unit:
##			print('line entry: %s:%d' % (str(lineEntry.GetFileSpec()),
#			# Get the source manager
#			source_manager = lineEntry.GetFileSpec().GetSymbolFile().GetSourceManager()
#		
#		
#			# Get the file content
#			file_content = source_manager.ReadFileContents(lineEntry.GetFileSpec())
#				
#	#		# Get the source manager
#	#		source_manager = frame.GetModule().GetSymbolFile().GetSourceManager()
#			
#			# Get the file content
#	#		file_content = source_manager.ReadFileContents(file_spec)
#			
#			# Print the relevant source code lines
#			if file_content:
#				lines = file_content.splitlines()
#				start_line = max(1, line_num - 5)  # Print 5 lines before and after the current line
#				end_line = min(len(lines), line_num + 5)
#				
#				for i in range(start_line, end_line + 1):
#					print(f"{i}: {lines[i - 1]}")
				
	def runTargetLoad(self):
		if self.isTargetLoadActive:
			self.interruptTargetLoad = True
			return
		else:
			self.interruptTargetLoad = False
		QCoreApplication.processEvents()
		self.isTargetLoadActive = True
		
		self.sendProgressUpdate(5)
		
		
		# Create a new debugger instance
		lldbHelper.debugger = lldb.SBDebugger.Create()
		
#		global debugger
#		debugger = self.debugger
		
		# When we step or continue, don't return from the function until the process
		# stops. We do this by setting the async mode to false.
#		lldbHelper.debugger.SetAsync(False)
		
#       for i in dir(debugger):
#           print(i)
#       {lldb.getVersion()}
		print(f"VEARSION: {sys.modules['lldb'].__file__} / {lldbHelper.debugger.GetVersionString()}")
		
#       print(lldb)
		
#       for i in dir(lldb):
#           print(i)
#       self.inputHandler = FBInputHandler(debugger, self.inputCallback)
		
		print(f'debugger: {lldbHelper.debugger}')
		# Create a target from a file and arch
		print("Creating a target for '%s'" % self.targetPath)
		
		
		lldbHelper.target = lldbHelper.debugger.CreateTargetWithFileAndArch(self.targetPath, None) # lldb.LLDB_ARCH_DEFAULT)
#		global target
#		target = self.target
		
		if lldbHelper.target:
			self.sendProgressUpdate(10)
			
			
			# If the target is valid set a breakpoint at main
			main_bp = lldbHelper.target.BreakpointCreateByName(fname, lldbHelper.target.GetExecutable().GetFilename())
			main_bp.AddName(fname)
			#			error = main_bp.SetScriptCallbackBody("\
			#			print 'Hit breakpoint callback'")
			#           main_bp.SetScriptCallbackFunction('disasm_ui.breakpoint_cb')
			#           main_bp.SetAutoContinue(auto_continue=True)
			main_bp.SetScriptCallbackFunction("disasm_ui.breakpointHandler")
#			main_bp.SetAutoContinue(auto_continue=True)
			print(main_bp)
			
			
			loop_bp = lldbHelper.target.BreakpointCreateByAddress(0x100003f64) # 0x100003c90)
			loop_bp.SetEnabled(True)
			loop_bp.AddName("loop_bp")
			loop_bp.SetCondition("$eax == 0x00000005")
			loop_bp.SetScriptCallbackFunction("disasm_ui.breakpointHandler")
			print(loop_bp)
			
			# Launch the process. Since we specified synchronous mode, we won't return
			# from this function until we hit the breakpoint at main
			
			lldbHelper.process = lldbHelper.target.LaunchSimple(None, None, os.getcwd())
			
#			global process
#			process = self.process
#           process.Stop()
#           self.inputHandler.start()
#			print(self.process)
			
			# Make sure the launch went ok
			if lldbHelper.process:
				
##################################################
#				pid = lldbHelper.process.GetProcessID()
#				
#				listener = lldbHelper.debugger.GetListener()
#				# sign up for process state change events
#				stop_idx = 0
#				done = False
#				while not done:
#					event = lldb.SBEvent()
#					if listener.WaitForEvent(lldb.UINT32_MAX, event): # options.event_timeout
#						if lldb.SBProcess.EventIsProcessEvent(event):
#							state = lldb.SBProcess.GetStateFromEvent(event)
#							if state == lldb.eStateInvalid:
#								# Not a state event
#								print('process event = %s' % (event))
#							else:
#								print("process state changed event: %s" % (lldb.SBDebugger.StateAsCString(state)))
#								if state == lldb.eStateStopped:
#									self.signals.loadProcess.emit(lldbHelper.process)
#									QCoreApplication.processEvents()
#									self.sendProgressUpdate(15)
#									
#									state = lldbHelper.process.GetState()
#					#				print(self.process)
#									if True: #state == lldb.eStateStopped:
#										print("state == lldb.eStateStopped")
#									
#									
#					#					print(f'GetNumQueues: {self.process.GetNumQueues()}')
#					#					for que in range(self.process.GetNumQueues()):
#					#						print(f'process.GetQueueAtIndex({que}) {self.process.GetQueueAtIndex(que)}')
#					#						
#					#					print(f'GetNumThreads: {self.process.GetNumThreads()}')
#					#					# Get the first thread
#					#					for thrd in range(self.process.GetNumThreads()):
#					#						print(f'process.GetThreadAtIndex({thrd}) {self.process.GetThreadAtIndex(thrd).GetIndexID()}')
#									
#										idxThread = 0
#									
#									
#										lldbHelper.thread = lldbHelper.process.GetThreadAtIndex(0)
#					#					global thread
#					#					thread = self.thread
#										if lldbHelper.thread:
#											
#											
#											
#					#                       # Get the current register state
#					#                       register_state = thread.GetThreadState()
#					#                   
#					#                       # Get the RIP register value
#					#                       rip_value = register_state.GetRegisterValue("rip")
#					#                   
#					#                       # Print the RIP value
#					#                       print("Current RIP:", hex(rip_value))
#											
#					#                       # Get the current instruction address
#					#                       instruction_address = thread.GetInstructionAddress()
#					#                   
#					#                       # Get the current instruction location
#					#                       instruction_location = lldb.SBInstructionLocation(process, instruction_address)
#					#                   
#					#                       # Get the file and line number where the instruction is located
#					#                       file_name, line_number = instruction_location.GetLineEntry().GetFileNameAndLine()
#					#                   
#					#                       # Print the file and line number
#					#                       print("Current instruction location:", file_name, line_number)
#											
#											self.signals.loadThread.emit(idxThread, lldbHelper.thread)
#											QCoreApplication.processEvents()
#											idxThread += 1
#											self.sendProgressUpdate(20)
#											# Print some simple thread info
#					#						print(self.thread)
#					#						print_stacktrace(lldbHelper.thread)
#					#						print(f'GetNumFrames: {lldbHelper.thread.GetNumFrames()}')
#											
#											for idx2 in range(lldbHelper.thread.GetNumFrames()):
#												
#												# Get the first frame
#												frame = lldbHelper.thread.GetFrameAtIndex(idx2)
#												if frame:
#													self.sendProgressUpdate(25)
#													# Print some simple frame info
#													print(frame)
#													
#													print(f'AAAAA >>>> {hex(frame.GetPC())}')
#													print(f'LANGUAGE >>>> {lldbHelper.GuessLanguage(frame)}')
#													
#													if idx2 == 0:
#														
#														import traceback
#														
#														try:
#															
#															self.print_source_code_for_frame(frame)
#										#					process = lldb.SBProcess.CreateProcess(None, None, None)
#										#					process.AttachToProcess(pid)
#															
#					#										pc = frame.GetPC()
#					#										source_index = frame.GetModule().FindAddress(pc).GetLineEntry().GetLineIndex()
#					#										source = frame.GetModule().GetSourceLines(source_index, 1, False)
#															
#															symbol_context = frame.GetSymbolContext(lldb.eSymbolContextLineEntry)
#															compileUnit = symbol_context.GetCompileUnit()
#															for lineEntry in compileUnit:
#																print('line entry: %s:%d' % (str(lineEntry.GetFileSpec()),
#																							lineEntry.GetLine()))
#																print('start addr: %s' % str(lineEntry.GetStartAddress()))
#																print('end   addr: %s' % str(lineEntry.GetEndAddress()))
#																
#																source = str(lineEntry.GetLine()) + " " + str(lineEntry.GetColumn())
#																print(source)
#																
#																source = frame.GetModule().GetSourceLines(lineEntry.GetLine(), 1, False)
#																print(source[0])
#																
#															source_index = compileUnit.GetLineEntryAtIndex(0).GetLine() #.GetLineIndex()
#															source = frame.GetModule().GetSourceLines(source_index, 1, False)
#															print(source[0])
#														except Exception as e:
#															print(f'Error SOURCE CODE: {e}')
#															
#														print(f'11111 >>>> {frame.GetModule()}')
#														for symbol in frame.GetModule():
#															name = symbol.GetName()
#															saddr = symbol.GetStartAddress()
#															eaddr = symbol.GetEndAddress()
#															type = symbol.GetType()
#															
#															print(f'- SYM: {name} => {saddr} - {eaddr} ({type})')
#															
#															
#														self.signals.loadSections.emit(frame.GetModule())
#														QCoreApplication.processEvents()
#														
#					#									print('Number of sections: %d' % frame.GetModule().GetNumSections())
#					#									for sec in frame.GetModule().section_iter():
#					#										print(sec.GetName())
#					##										for jete in dir(sec):
#					##											print(jete)
#					#										for jete2 in range(sec.GetNumSubSections()):
#					#											print(sec.GetSubSectionAtIndex(jete2).GetName())
#														
#														rip = self.convert_address(frame.register["rip"].value)
#					#									print(rip)
#														function = frame.GetFunction()
#														# See if we have debug info (a function)
#														if function:
#															# We do have a function, print some info for the
#															# function
#															print(function)
#															
#							#                               for functionNG2 in dir(function):
#							#                                   print(functionNG2)
#															
#															# Now get all instructions for this function and print
#															# them
#															insts = function.GetInstructions(lldbHelper.target)
#															self.disassemble_instructions(insts, rip)
#														else:
#															# See if we have a symbol in the symbol table for where
#															# we stopped
#															symbol = frame.GetSymbol()
#															if symbol:
#																# We do have a symbol, print some info for the
#																# symbol
#																print(symbol)
#																
#							#                                   print(f'DisplayName: {symbol.GetName()}')
#																# Now get all instructions for this symbol and
#																# print them
#																insts = symbol.GetInstructions(lldbHelper.target)
#																self.disassemble_instructions(insts, rip)
#																
#							#                                   for functionNG2 in dir(symbol):
#							#   #                                   if functionNG2.startswith("__"):
#							#   #                                       continue
#							#                                       print(functionNG2)
#																
#														registerList = frame.GetRegisters()
#														print(
#															"Frame registers (size of register set = %d):"
#															% registerList.GetSize()
#														)
#														self.sendProgressUpdate(30)
#														currReg = 0
#														for value in registerList:
#															# print value
#															print(
#																"%s (number of children = %d):"
#																% (value.GetName(), value.GetNumChildren())
#															)
#															self.signals.loadRegister.emit(value.GetName())
#							#                               continue
#							#                               registerNode = QTreeWidgetItem(self.treRegister, [value.GetName() + " (" + str(value.GetNumChildren()) + ")", '', ''])
#							#                               QTreeWidgetItem(self.treRegister, ['Floating point register', 'eax', '0x5'])
#															for child in value:
#							#                                   print(
#							#                                       "Name: ", child.GetName(), " Value: ", child.GetValue()
#							#                                   )
#																
#							#                                   variable_type = type(child.GetValue())
#																
#							#                                   print(f"The type of child.GetValue() is: {variable_type}")
#																
#																memoryValue = ""
#																try:
#																	
#																	# Specify the memory address and size you want to read
#																	size = 32  # Adjust the size based on your data type (e.g., int, float)
#																	
#																	# Read memory and print the result
#																	data = self.read_memory(lldbHelper.process, lldbHelper.target.ResolveLoadAddress(int(child.GetValue(), 16)), size)
#																	
#																	hex_string = ''.join("%02x" % byte for byte in data)
#																	
#																	formatted_hex_string = ' '.join(re.findall(r'.{2}', hex_string))
#																	memoryValue = formatted_hex_string
#							#                                       if data:
#							#                                           print(f"Data at address {hex(address)}: {data}\n{formatted_hex_string}")
#																except Exception as e:
#							#                                       print(f"Error getting memory for addr: {e}")
#																	pass
#																	
#																self.signals.loadRegisterValue.emit(currReg, child.GetName(), child.GetValue(), memoryValue)
#																QCoreApplication.processEvents()
#																
#															currProg = (registerList.GetSize() - currReg)
#															self.sendProgressUpdate(30 + (70 / currProg))
#															currReg += 1
#															
##									if stop_idx == 0:
###										if launch_info:
###											print("process %u launched" % (pid))
###											run_commands(
###												command_interpreter, ['breakpoint list'])
###										else:
###											print("attached to process %u" % (pid))
###											for m in target.modules:
###												print(m)
###											if options.breakpoints:
###												for bp in options.breakpoints:
###													debugger.HandleCommand(
###														"_regexp-break %s" % (bp))
###												run_commands(
###													command_interpreter, ['breakpoint list'])
###										run_commands(
###											command_interpreter, options.launch_commands)
##									else:
##										if options.verbose:
##											print("process %u stopped" % (pid))
##										run_commands(
##											command_interpreter, options.stop_commands)
##									stop_idx += 1
##									print_threads(process, options)
#									print("continuing process %u" % (pid))
#									lldbHelper.process.Continue()
#								elif state == lldb.eStateExited:
#									exit_desc = lldbHelper.process.GetExitDescription()
#									if exit_desc:
#										print("process %u exited with status %u: %s" % (pid, lldbHelper.process.GetExitStatus(), exit_desc))
#									else:
#										print("process %u exited with status %u" % (pid, lldbHelper.process.GetExitStatus()))
##									run_commands(
##										command_interpreter, options.exit_commands)
#									done = True
#								elif state == lldb.eStateCrashed:
#									print("process %u crashed" % (pid))
##									print_threads(lldbHelper.process, options)
##									run_commands(
##										command_interpreter, options.crash_commands)
#									done = True
#								elif state == lldb.eStateDetached:
##									print("process %u detached" % (pid))
#									done = True
#								elif state == lldb.eStateRunning:
#									# process is running, don't say anything,
#									# we will always get one of these after
#									# resuming
##									if options.verbose:
##										print("process %u resumed" % (pid))
#									pass
#								elif state == lldb.eStateUnloaded:
##									print("process %u unloaded, this shouldn't happen" % (pid))
#									done = True
#								elif state == lldb.eStateConnected:
#									print("process connected")
#								elif state == lldb.eStateAttaching:
#									print("process attaching")
#								elif state == lldb.eStateLaunching:
#									print("process launching")
#						else:
#							print('event = %s' % (event))
#					else:
#						# timeout waiting for an event
##						print("no process event for %u seconds, killing the process..." % (options.event_timeout))
#						done = True
				
##################################################				
				
					
				print("GETPLATFORM:")
				print(lldbHelper.target.GetPlatform().GetWorkingDirectory())
				print(lldbHelper.target.GetPlatform().GetOSBuild())
				print(lldbHelper.target.GetPlatform().GetHostname())
				print(lldbHelper.target.GetTriple())
				print(lldbHelper.target.GetPlatform().GetTriple())
				print(lldbHelper.target.GetPlatform().GetOSDescription())
				print(lldbHelper.target.GetPlatform().IsConnected())
				
				li = lldbHelper.target.GetLaunchInfo()
				statistics = lldbHelper.target.GetStatistics()
				stream = lldb.SBStream()
				success = statistics.GetAsJSON(stream)
				if success:
					self.signals.loadStats.emit(str(stream.GetData()))
					QCoreApplication.processEvents()
#					print(stream.GetData())
				
#				print(li.GetProcessID())
#				for info in dir(lldbHelper.target.GetStatistics()):
#					print(info)
					
#				executable = lldbHelper.process.GetExecutable()
#				self.executeCmd()
#				self.handle_readMemory(self.debugger, 0x108a01b90, 0x100)
				
#				for fun in dir(self.process):
#					print(fun)
#               for module in process.GetLoadedModules():
#                   for symbol in module.GetSymbols():
#                       if symbol.GetType() == lldb.SBSymbolType.ST_Import:
#                           print(symbol.GetName())
					
					
				self.signals.loadProcess.emit(lldbHelper.process)
				QCoreApplication.processEvents()
				self.sendProgressUpdate(15)
#				print("Process launched OK")
				# Print some simple process info
				state = lldbHelper.process.GetState()
#				print(self.process)
				if True: #state == lldb.eStateStopped:
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
					
					
					lldbHelper.thread = lldbHelper.process.GetThreadAtIndex(0)
#					global thread
#					thread = self.thread
					if lldbHelper.thread:
						
						
						
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
						
						self.signals.loadThread.emit(idxThread, lldbHelper.thread)
						QCoreApplication.processEvents()
						idxThread += 1
						self.sendProgressUpdate(20)
						# Print some simple thread info
#						print(self.thread)
#						print_stacktrace(lldbHelper.thread)
#						print(f'GetNumFrames: {lldbHelper.thread.GetNumFrames()}')
						
						for idx2 in range(lldbHelper.thread.GetNumFrames()):
							
							# Get the first frame
							frame = lldbHelper.thread.GetFrameAtIndex(idx2)
							if frame:
								self.sendProgressUpdate(25)
								# Print some simple frame info
								print(frame)
								
								print(f'AAAAA >>>> {hex(frame.GetPC())}')
								print(f'LANGUAGE >>>> {lldbHelper.GuessLanguage(frame)}')
								
								if idx2 == 0:
									
									import traceback
									
									try:
										
										self.print_source_code_for_frame(frame)
					#					process = lldb.SBProcess.CreateProcess(None, None, None)
					#					process.AttachToProcess(pid)
										
#										pc = frame.GetPC()
#										source_index = frame.GetModule().FindAddress(pc).GetLineEntry().GetLineIndex()
#										source = frame.GetModule().GetSourceLines(source_index, 1, False)
										
										symbol_context = frame.GetSymbolContext(lldb.eSymbolContextLineEntry)
										compileUnit = symbol_context.GetCompileUnit()
										for lineEntry in compileUnit:
											print('line entry: %s:%d' % (str(lineEntry.GetFileSpec()),
																		lineEntry.GetLine()))
											print('start addr: %s' % str(lineEntry.GetStartAddress()))
											print('end   addr: %s' % str(lineEntry.GetEndAddress()))
										
											source = str(lineEntry.GetLine()) + " " + str(lineEntry.GetColumn())
											print(source)
											
											source = frame.GetModule().GetSourceLines(lineEntry.GetLine(), 1, False)
											print(source[0])
											
										source_index = compileUnit.GetLineEntryAtIndex(0).GetLine() #.GetLineIndex()
										source = frame.GetModule().GetSourceLines(source_index, 1, False)
										print(source[0])
									except Exception as e:
										print(f'Error SOURCE CODE: {e}')
										
									print(f'11111 >>>> {frame.GetModule()}')
									for symbol in frame.GetModule():
										name = symbol.GetName()
										saddr = symbol.GetStartAddress()
										eaddr = symbol.GetEndAddress()
										type = symbol.GetType()
										
										print(f'- SYM: {name} => {saddr} - {eaddr} ({type})')
									
									
									self.signals.loadSections.emit(frame.GetModule())
									QCoreApplication.processEvents()
									
#									print('Number of sections: %d' % frame.GetModule().GetNumSections())
#									for sec in frame.GetModule().section_iter():
#										print(sec.GetName())
##										for jete in dir(sec):
##											print(jete)
#										for jete2 in range(sec.GetNumSubSections()):
#											print(sec.GetSubSectionAtIndex(jete2).GetName())
										
									rip = lldbHelper.convert_address(frame.register["rip"].value)
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
										insts = function.GetInstructions(lldbHelper.target)
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
											insts = symbol.GetInstructions(lldbHelper.target)
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
												data = self.read_memory(lldbHelper.process, lldbHelper.target.ResolveLoadAddress(int(child.GetValue(), 16)), size)
												
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
										
#				lldbHelper.process.Continue()							
			else:
				print("Process NOT launched!!!")
		else:
			print("Has NO target")
			
		self.isTargetLoadActive = False
#       self.treeWidget.setEnabled(True)
#       QCoreApplication.processEvents()
		self.signals.finished.emit()
		QCoreApplication.processEvents()
		
		while not self.interruptTargetLoad:
			time.sleep(1)
			pass
		
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
#		global target
		for i in insts:
			address = self.extract_address(f'{i}')
#           self.signals.addInstruction(.emit(f'0x{address}:\t{i.GetMnemonic(target)}\t{i.GetOperands(target)}', True, True, False, "black")
			self.signals.addInstructionNG.emit(f'0x{address}', f'{i.GetMnemonic(lldbHelper.target)}\t{i.GetOperands(lldbHelper.target)}', f'{i.GetComment(lldbHelper.target)}', f'{i.GetData(lldbHelper.target)}', True, True, False, "black", rip)
			
			QCoreApplication.processEvents()