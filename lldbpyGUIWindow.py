#!/usr/bin/env python3

#import lldb
#from lldbutil import *
#from inputHelper import FBInputHandler
#import psutil
import os
#import os.path
#import sys
#import sre_constants
#import re
#import binascii
#import webbrowser
#import ctypes
#import time
#import signal

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from PyQt6.QConsoleTextEdit import *

from ui.assemblerTextEdit import *
from ui.registerTreeView import *
from ui.fileInfoTableWidget import *
from ui.fileStructureTreeView import *
from ui.statisticsTreeWidget import *
from ui.breakpointTableWidget import *

from worker.eventListenerWorker import *
from worker.loadSourceWorker import *

import lldbHelper
from lldbutil import *
from config import *
from dbgHelper import *

APP_NAME = "LLDB-PyGUI"
WINDOW_SIZE = 680

APP_VERSION = "v0.0.1"

class LLDBPyGUIWindow(QMainWindow):
	"""PyMobiledevice3GUI's main window (GUI or view)."""
	
#	regTreeList = []
	
	debugger = None
	interruptEventListenerWorker = None
	interruptLoadSourceWorker = None
	process = None
	
	def __init__(self, debugger):
		super().__init__()
		self.debugger = debugger
		
		self.setWindowTitle(APP_NAME + " " + APP_VERSION)
		self.setBaseSize(WINDOW_SIZE * 2, WINDOW_SIZE)
		self.setMinimumSize(WINDOW_SIZE * 2, WINDOW_SIZE + 72)
		
		self.toolbar = QToolBar('Main ToolBar')
		self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)
		self.toolbar.setIconSize(QSize(ConfigClass.toolbarIconSize, ConfigClass.toolbarIconSize))
		
		# new menu item
		self.load_action = QAction(ConfigClass.iconBug, '&Load Target', self)
		self.load_action.setStatusTip('Load Target')
		self.load_action.setShortcut('Ctrl+L')
		self.load_action.triggered.connect(self.load_clicked)
		self.toolbar.addAction(self.load_action)
		
		self.statusBar = QStatusBar()
		self.setStatusBar(self.statusBar)
		
		self.progressbar = QProgressBar()
		self.progressbar.setMinimum(0)
		self.progressbar.setMaximum(100)
		self.progressbar.setValue(0)
		self.progressbar.setFixedWidth(100)
		# Add the progress bar to the status bar
		self.statusBar.addPermanentWidget(self.progressbar)
		
		self.layout = QVBoxLayout()
		
		self.txtMultiline = AssemblerTextEditNG()
#		self.txtMultiline.table.actionShowMemory.triggered.connect(self.handle_showMemory)
#		self.txtMultiline.table.sigEnableBP.connect(self.handle_enableBP)
#		self.txtMultiline.table.sigBPOn.connect(self.handle_BPOn)
		
		self.txtMultiline.setContentsMargins(0, 0, 0, 0)
		
		self.splitter = QSplitter()
		self.splitter.setContentsMargins(0, 0, 0, 0)
		self.splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.splitter.setOrientation(Qt.Orientation.Vertical)
		
		self.splitter.addWidget(self.txtMultiline)
		
		self.tabWidgetDbg = QTabWidget()
		
		self.splitter.addWidget(self.tabWidgetDbg)
		
		self.tabWidgetReg = QTabWidget()
		
		self.tabWidgetDbg.addTab(self.tabWidgetReg, "Register")
		self.txtSource = QConsoleTextEdit()
		self.txtSource.setFont(ConfigClass.font)
		self.gbpSource = QGroupBox("Source")
		self.gbpSource.setLayout(QHBoxLayout())
		self.gbpSource.layout().addWidget(self.txtSource)
		self.tabWidgetDbg.addTab(self.gbpSource, "Source")
		
		self.tblBPs = BreakpointsTableWidget(self)
#		self.tabBPs = QWidget()
#		self.tabBPs.setLayout(QVBoxLayout())
#		self.tabBPs.layout().addWidget(self.tblBPs)
#		self.tabWidget.addTab(self.tabBPs, "Breakpoints")
		
		self.tabWidgetDbg.addTab(self.tblBPs, "Break-/Watchpoints")
		self.tabWidgetDbg.addTab(QTextEdit(), "Threads/Frames")
		
		self.tabWidgetMain = QTabWidget()
		self.tabWidgetMain.addTab(self.splitter, "Debugger")
		
		self.tblFileInfos = FileInfosTableWidget()
		self.tabWidgetFileInfos = QWidget()
		self.tabWidgetFileInfos.setLayout(QVBoxLayout())
		
		
		self.gbFileInfo = QGroupBox("File Header")
		self.gbFileInfo.setLayout(QHBoxLayout())
		self.gbFileInfo.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
		self.gbFileInfo.layout().addWidget(self.tblFileInfos)
		
		self.splitterFileInfos = QSplitter()
		self.splitterFileInfos.setContentsMargins(0, 0, 0, 0)
		self.splitterFileInfos.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.splitterFileInfos.setOrientation(Qt.Orientation.Vertical)
		
		self.splitterFileInfos.addWidget(self.gbFileInfo)
		
		
		
		self.gbFileStruct = QGroupBox("File Structure")
		self.gbFileStruct.setLayout(QHBoxLayout())
		self.gbFileStruct.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
		
		self.treFile = FileStructureTreeWidget()
#		self.treFile.actionShowMemoryFrom.triggered.connect(self.handle_showMemoryFileStructureFrom)
#		self.treFile.actionShowMemoryTo.triggered.connect(self.handle_showMemoryFileStructureTo)
		
		self.tabWidgetStruct = QWidget()
		self.tabWidgetStruct.setLayout(QVBoxLayout())
		self.tabWidgetStruct.layout().addWidget(self.treFile)
		
		self.gbFileStruct.layout().addWidget(self.tabWidgetStruct)
		
		self.splitterFileInfos.addWidget(self.gbFileStruct)
		
		self.gbFileStats = QGroupBox("File Statistics")
		self.gbFileStats.setLayout(QHBoxLayout())
		self.gbFileStats.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
		
		self.splitterFileInfos.addWidget(self.gbFileStats)
		self.treStats = QStatisticsTreeWidget()
		self.tabWidgetStats = QWidget()
		self.tabWidgetStats.setLayout(QVBoxLayout())
		self.tabWidgetStats.layout().addWidget(self.treStats)
		
		self.gbFileStats.layout().addWidget(self.tabWidgetStats)
		
		self.splitterFileInfos.addWidget(self.gbFileStats)
		
		self.tabWidgetFileInfos.layout().addWidget(self.splitterFileInfos)
		
		self.tabWidgetMain.addTab(self.tabWidgetFileInfos, "File Info")
		
		self.layout.addWidget(self.tabWidgetMain)
		
		self.centralWidget = QWidget(self)
		self.centralWidget.setLayout(self.layout)        
		self.setCentralWidget(self.centralWidget)
		
		self.interruptEventListenerWorker = EventListenerReceiver()
		self.interruptLoadSourceWorker = LoadSourceCodeReceiver()
		
		self.threadpool = QThreadPool()
		
		print(f"NUM-TARGETS: {self.debugger.GetNumTargets()}")
		if self.debugger.GetNumTargets() > 0:
			
			print(f"TARGET-1: {self.debugger.GetTargetAtIndex(0)}")
			target = self.debugger.GetTargetAtIndex(0)
			
			if target:
				print("======== START BP INTER =========")
				for b in target.breakpoint_iter():
					print(b)
				print("========= END BP INTER ==========")
				
				idx = 0
				for i in range(target.GetNumBreakpoints()):
					idx += 1
		#           print(dir(lldbHelper.target.GetBreakpointAtIndex(i)))
					bp_cur = target.GetBreakpointAtIndex(i)
					print(bp_cur)
					for bl in bp_cur:
						# Make sure the name list has the remaining name:
						name_list = lldb.SBStringList()
						bp_cur.GetNames(name_list)
		#               print(name_list)
		#               print(len(name_list))
		#               print(name_list.GetSize())
						num_names = name_list.GetSize()
		#               self.assertEquals(
		#                   num_names, 1, "Name list has %d items, expected 1." % (num_names)
		#               )
						
						name = name_list.GetStringAtIndex(0)
		#               self.assertEquals(
		#                   name,
		#                   other_bkpt_name,
		#                   "Remaining name was: %s expected %s." % (name, other_bkpt_name),
		#               )
		#               print(dir(bl))
		#               bp_cur = lldbHelper.target.GetBreakpointAtIndex(i)
		#               print(bl)
		#               print(dir(bl))
		#               print(bl.GetQueueName())
		#               print(get_description(bp_cur))
		#               print(dir(get_description(bp_cur)))
						
						
						self.txtMultiline.table.toggleBPAtAddress(hex(bl.GetLoadAddress()), False)
						
						
#						self.tblBPs.resetContent()
						self.tblBPs.addRow(bp_cur.GetID(), idx, hex(bl.GetLoadAddress()), name, str(bp_cur.GetHitCount()), bp_cur.GetCondition())
		#               print(f'LOADING BREAKPOINT AT ADDRESS: {hex(bl.GetLoadAddress())}')
				
				self.loadFileInfo(target.GetExecutable().GetFilename())
				self.loadFileStats(target)
				
				self.process = target.GetProcess()
				if self.process:
					thread = self.process.GetThreadAtIndex(0)
					if thread:
		#				pass
						frame = thread.GetFrameAtIndex(0)
						if frame:
							########################################################################
							i = 0
							addr = frame.GetPCAddress()
							load_addr = addr.GetLoadAddress(target)
							function = frame.GetFunction()
							mod_name = frame.GetModule().GetFileSpec().GetFilename()
							print(f'load_addr: {load_addr}')
							if not function:
								# No debug info for 'function'.
								symbol = frame.GetSymbol()
								file_addr = addr.GetFileAddress()
								start_addr = symbol.GetStartAddress().GetFileAddress()
								symbol_name = symbol.GetName()
								symbol_offset = file_addr - start_addr
								print(f'symbol_name: {symbol_name}')
#								with open("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/my_output.txt", "w") as output:
								print('  frame #{num}: {addr:#016x} {mod}`{symbol} + {offset}'.format(num=i, addr=load_addr, mod=mod_name, symbol=symbol_name, offset=symbol_offset))
							else:
								# Debug info is available for 'function'.
								func_name = frame.GetFunctionName()
								file_name = frame.GetLineEntry().GetFileSpec().GetFilename()
								line_num = frame.GetLineEntry().GetLine()
								print(f'function.GetStartAddress().GetFileAddress(): {function.GetStartAddress().	GetFileAddress()}')
								print(f'func_name: {func_name}')
#								with open("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/my_output.txt", "w") as output:
								print('  frame #{num}: {addr:#016x} {mod}`{func} at {file}:{line} {args}'.format(num=i, addr=load_addr, mod=mod_name, func='%s [inlined]' % func_name if frame.IsInlined() else func_name, file=file_name, line=line_num, args=get_args_as_string(frame, showFuncName=False))) #args=get_args_as_string(frame, showFuncName=False)), output)
								
								
								self.disassemble_instructions(function.GetInstructions(target), target)
							
							
							for symbol in frame.GetModule():
								name = symbol.GetName()
								saddr = symbol.GetStartAddress()
								eaddr = symbol.GetEndAddress()
								type = symbol.GetType()
								
								print(f'- SYM: {name} => {saddr} - {eaddr} ({type})')
							
							
							module = frame.GetModule()
#								self.signals.loadSections.emit(frame.GetModule())
#								QCoreApplication.self.processEvents()
							
							print('Number of sections: %d' % module.GetNumSections())
							for sec in module.section_iter():
								print(sec)
								print(sec.GetName())
								print(f'GetFileByteSize() == {hex(sec.GetFileByteSize())}')
								print(f'GetByteSize() == {hex(sec.GetByteSize())}')
								
								print(f'GetSectionType: {sec.GetSectionType()} / {lldbHelper.SectionTypeString(sec.GetSectionType())}')
								
					#           for inin in dir(sec):
					#               print(inin)
								
								sectionNode = QTreeWidgetItem(self.treFile, [sec.GetName(), str(hex(sec.GetFileAddress())), str(hex(sec.GetFileAddress() + sec.GetByteSize())), hex(sec.GetFileByteSize()), hex(sec.GetByteSize()), lldbHelper.SectionTypeString(sec.GetSectionType()) + " (" + str(sec.GetSectionType()) + ")"])
					#           for jete in dir(sec):
					#               print(jete)
								INDENT = "\t"
								INDENT2 = "\t\t"
					#           if sec.GetName() == "__TEXT":
								# Iterates the text section and prints each symbols within each sub-section.
					#           for subsec2 in sec:
					#               print(subsec2.GetName())
					#               print(INDENT + repr(subsec2))
					#               for sym in module.symbol_in_section_iter(subsec2):
					#                   print(sym.GetName())
					#                   print(INDENT2 + repr(sym))
					#                   print(INDENT2 + 'symbol type: %s' % str(sym.GetType())) # symbol_type_to_str
								
								for jete2 in range(sec.GetNumSubSections()):
									print(sec.GetSubSectionAtIndex(jete2).GetName())
									
									subSec = sec.GetSubSectionAtIndex(jete2)
									
									subSectionNode = QTreeWidgetItem(sectionNode, [subSec.GetName(), str(hex(subSec.GetFileAddress())), str(hex(subSec.GetFileAddress() + subSec.GetByteSize())), hex(subSec.GetFileByteSize()) + " / " + hex(subSec.GetByteSize()), lldbHelper.SectionTypeString(subSec.GetSectionType()) + " (" + str(subSec.GetSectionType()) + ")"])
									
									for sym in module.symbol_in_section_iter(subSec):
										subSectionNode2 = QTreeWidgetItem(subSectionNode, [sym.GetName(), str(hex(sym.GetStartAddress().GetFileAddress())), str(hex(sym.GetEndAddress().GetFileAddress())), hex(sym.GetSize()), 'Symbol'])
										print(dir(sym))
										print(sym.GetName())
										print(INDENT2 + repr(sym))
										print(INDENT2 + 'symbol type: %s' % str(sym.GetType())) # symbol_type_to_str
							pass
								
							########################################################################
#							...
		#					self.sendProgressUpdate(25)
			
		#					if idx2 == 0:
							registerList = frame.GetRegisters()
							print(
								"Frame registers (size of register set = %d):"
								% registerList.GetSize()
							)
		#					self.sendProgressUpdate(30)
							currReg = 0
							for value in registerList:
								# print value
								print(
									"%s (number of children = %d):"
									% (value.GetName(), value.GetNumChildren())
								)
								tabDet = QWidget()
								treDet = RegisterTreeWidget()
		#						self.regTreeList.append(treDet)
								tabDet.setLayout(QVBoxLayout())
								tabDet.layout().addWidget(treDet)
								
								treDet.setFont(ConfigClass.font)
								treDet.setHeaderLabels(['Registername', 'Value', 'Memory'])
								treDet.header().resizeSection(0, 128)
								treDet.header().resizeSection(1, 256)
								self.tabWidgetReg.addTab(tabDet, value.GetName())
								
								for child in value:
									memoryValue = ""
									try:
										
										# Specify the memory address and size you want to read
										size = 32  # Adjust the size based on your data type (e.g., int, float)
										
										# Read memory and print the result
										data = self.read_memory(self.process, target.ResolveLoadAddress(int(child.GetValue(), 16)), size)
										
										hex_string = ''.join("%02x" % byte for byte in data)
										
										formatted_hex_string = ' '.join(re.findall(r'.{2}', hex_string))
										memoryValue = formatted_hex_string
		
									except Exception as e:
#                              				print(f"Error getting memory for addr: {e}")
										pass
										
#									self.signals.loadRegisterValue.emit(currReg, child.GetName(), child.GetValue(), memoryValue)
#									QCoreApplication.self.processEvents()
									registerDetailNode = QTreeWidgetItem(treDet, [child.GetName(), child.GetValue(), memoryValue])
						
						self.start_eventListenerWorker(self.debugger, self.interruptEventListenerWorker)
						self.start_loadSourceWorker(self.debugger, "/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/hello_world/hello_world_test.c", self.interruptLoadSourceWorker)
#						self.process.Continue()
				

		
	def load_clicked(self, s):
		dialog = QFileDialog(None, "Select executable or library", "", "All Files (*.*)")
		dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
		dialog.setNameFilter("Executables (*.exe *.com *.bat *);;Libraries (*.dll *.so *.dylib)")
		
		if dialog.exec():
			filename = dialog.selectedFiles()[0]
			print(filename)
#			self.start_workerLoadTarget(filename)
		else:
			return None
	
	def loadFileInfo(self, target):
		self.setWindowTitle(APP_NAME + " " + APP_VERSION + " - " + os.path.basename(target))
		
		mach_header = lldbHelper.GetFileHeader(target)
		
		self.tblFileInfos.addRow("Magic", lldbHelper.MachoMagic.to_str(lldbHelper.MachoMagic.create_magic_value(mach_header.magic)), hex(mach_header.magic))
		self.tblFileInfos.addRow("CPU Type", lldbHelper.MachoCPUType.to_str(lldbHelper.MachoCPUType.create_cputype_value(mach_header.cputype)), hex(mach_header.cputype))
		self.tblFileInfos.addRow("CPU SubType", str(mach_header.cpusubtype), hex(mach_header.cpusubtype))
		self.tblFileInfos.addRow("File Type", lldbHelper.MachoFileType.to_str(lldbHelper.MachoFileType.create_filetype_value(mach_header.filetype)), hex(mach_header.filetype))
		self.tblFileInfos.addRow("Num CMDs", str(mach_header.ncmds), hex(mach_header.ncmds))
		self.tblFileInfos.addRow("Size CMDs", str(mach_header.sizeofcmds), hex(mach_header.sizeofcmds))
		self.tblFileInfos.addRow("Flags", lldbHelper.MachoFlag.to_str(lldbHelper.MachoFlag.create_flag_value(mach_header.flags)), hex(mach_header.flags))
	
	def disassemble_instructions(self, insts, target):
		idx = 0
		for i in insts:
			if idx == 0:
				print(dir(i))
			print(i)
			idx += 1
			print(i.GetData(target))
			self.txtMultiline.appendAsmTextNG(hex(i.GetAddress().GetFileAddress()), i.GetMnemonic(target),  i.GetOperands(target), i.GetComment(target), str(i.GetData(target)).replace("                             ", "\t\t").replace("		            ", "\t\t\t").replace("		         ", "\t\t").replace("		      ", "\t\t").replace("			   ", "\t\t\t"), True, "")
			
#	def disassemble_instruction(self, insts, target):
#		idx = 0
#		for i in insts:
#			if idx == 0:
#				print(dir(i))
#			print(i)
#			idx += 1
#			
#			self.txtMultiline.appendAsmTextNG(hex(i.GetAddress().GetFileAddress()), i.GetMnemonic(target) + " " + i.GetOperands(target), "", "".replace("                             ", "\t\t").replace("		            ", "\t\t\t").replace("		         ", "\t\t").replace("		      ", "\t\t").replace("			   ", "\t\t\t"), True, "")
			
			
	def loadFileStats(self, target):
		statistics = target.GetStatistics()
		stream = lldb.SBStream()
		success = statistics.GetAsJSON(stream)
		if success:
#			self.signals.loadStats.emit(str(stream.GetData()))
			
			self.treStats.loadJSON(str(stream.GetData()))
		
	def start_eventListenerWorker(self, debugger, event_listener):
		workerEventListener = EventListenerWorker(debugger, event_listener)
#		workerEventListener.signals.finished.connect(self.handle_commandFinished)
		
		self.threadpool.start(workerEventListener)
		
	def start_loadSourceWorker(self, debugger, sourceFile, event_listener):
		self.workerLoadSource = LoadSourceCodeWorker(debugger, sourceFile, event_listener)
		self.workerLoadSource.signals.finished.connect(self.handle_loadSourceFinished)
		
		self.threadpool.start(self.workerLoadSource)
		
	def handle_loadSourceFinished(self, sourceCode):
		if sourceCode != "":
			log(sourceCode)
			self.txtSource.setEscapedText(sourceCode) # 
		else:
			self.txtSource.setText("<Source code NOT available>")
		
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
							