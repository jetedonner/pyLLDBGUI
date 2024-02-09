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
from PyQt6.QSwitch import *
from PyQt6.QHEXTextEditSplitter import *

from ui.assemblerTextEdit import *
from ui.registerTreeView import *
from ui.fileInfoTableWidget import *
from ui.fileStructureTreeView import *
from ui.statisticsTreeWidget import *
from ui.breakpointTableWidget import *
from ui.historyLineEdit import *
from ui.threadFrameTreeView import *

from worker.eventListenerWorker import *
from worker.loadSourceWorker import *
from worker.execCommandWorker import *

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
	
	driver = None
	debugger = None
	interruptEventListenerWorker = None
	interruptLoadSourceWorker = None
	process = None
	
	def __init__(self, debugger, driver = None):
		super().__init__()
		self.driver = driver
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
		
		
		self.load_resume = QAction(ConfigClass.iconResume, '&Resume', self)
		self.load_resume.setStatusTip('Resume')
#		self.load_resume.setShortcut('Ctrl+L')
		self.load_resume.triggered.connect(self.handle_resumeThread)
		self.toolbar.addAction(self.load_resume)
		
		self.step_over = QAction(ConfigClass.iconStepOver, '&Step Over', self)
		self.step_over.setStatusTip('Step Over')
#		self.load_resume.setShortcut('Ctrl+L')
		self.step_over.triggered.connect(self.stepOver_clicked)
		self.toolbar.addAction(self.step_over)
		
		self.step_into = QAction(ConfigClass.iconStepInto, '&Step Into', self)
		self.step_into.setStatusTip('Step Into')
#		self.load_resume.setShortcut('Ctrl+L')
		self.step_into.triggered.connect(self.stepInto_clicked)
		self.toolbar.addAction(self.step_into)
		
		self.step_out = QAction(ConfigClass.iconStepOut, '&Step Out', self)
		self.step_out.setStatusTip('Step Out')
#		self.load_resume.setShortcut('Ctrl+L')
		self.step_out.triggered.connect(self.stepOut_clicked)
		self.toolbar.addAction(self.step_out)
		
		self.step_restart = QAction(ConfigClass.iconRestart, '&Restart', self)
		self.step_restart.setStatusTip('Restart')
#		self.load_resume.setShortcut('Ctrl+L')
#		self.load_resume.triggered.connect(self.load_clicked)
		self.toolbar.addAction(self.step_restart)
		
		self.stop = QAction(ConfigClass.iconStop, '&Stop', self)
		self.stop.setStatusTip('Stop')
#		self.load_resume.setShortcut('Ctrl+L')
		self.stop.triggered.connect(self.handle_stopThread)
		self.toolbar.addAction(self.stop)
		
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
		self.txtMultiline.table.sigEnableBP.connect(self.handle_enableBP)
		self.txtMultiline.table.sigBPOn.connect(self.handle_BPOn)
		
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
		
		self.gbpBPs = QGroupBox("Breakpoints")
		self.gbpBPs.setLayout(QHBoxLayout())
		self.gbpBPs.layout().addWidget(self.tblBPs)
		
		self.tabWidgetDbg.addTab(self.gbpBPs, "Break-/Watchpoints")
		
		self.treThreads = ThreadFrameTreeWidget()
		self.treThreads.setFont(ConfigClass.font)
		self.treThreads.setHeaderLabels(['Num / ID', 'Hex ID', 'Process / Threads / Frames', 'PC', 'Lang (guess)'])
		self.treThreads.header().resizeSection(0, 148)
		self.treThreads.header().resizeSection(1, 128)
		self.treThreads.header().resizeSection(2, 512)
		
		self.gbpThreads = QGroupBox("Threads / Frames")
		self.gbpThreads.setLayout(QHBoxLayout())
		self.gbpThreads.layout().addWidget(self.treThreads)
		
		self.tabWidgetDbg.addTab(self.gbpThreads, "Threads/Frames")
		
		self.tabWidgetMain = QTabWidget()
		self.tabWidgetMain.addTab(self.splitter, "Debugger")
		
		self.tblFileInfos = FileInfosTableWidget()
		self.tabWidgetFileInfos = QWidget()
		self.tabWidgetFileInfos.setLayout(QVBoxLayout())
		
		self.tabWidgetFileInfo = QTabWidget()
		
		self.gbFileInfo = QGroupBox("File Header")
		self.gbFileInfo.setLayout(QHBoxLayout())
		self.gbFileInfo.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
		self.gbFileInfo.layout().addWidget(self.tblFileInfos)
		
		self.splitterFileInfos = QSplitter()
		self.splitterFileInfos.setContentsMargins(0, 0, 0, 0)
		self.splitterFileInfos.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.splitterFileInfos.setOrientation(Qt.Orientation.Vertical)
		
#		self.splitterFileInfos.addWidget(self.gbFileInfo)
		self.tabWidgetFileInfo.addTab(self.gbFileInfo, "File Header")
		
		
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
		
#		self.splitterFileInfos.addWidget(self.gbFileStruct)
		self.tabWidgetFileInfo.addTab(self.gbFileStruct	, "File Structure")
		
		self.gbFileStats = QGroupBox("File Statistics")
		self.gbFileStats.setLayout(QHBoxLayout())
		self.gbFileStats.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
		
		self.splitterFileInfos.addWidget(self.gbFileStats)
		self.treStats = QStatisticsTreeWidget()
		self.tabWidgetStats = QWidget()
		self.tabWidgetStats.setLayout(QVBoxLayout())
		self.tabWidgetStats.layout().addWidget(self.treStats)
		
		self.gbFileStats.layout().addWidget(self.tabWidgetStats)
		
#		self.splitterFileInfos.addWidget(self.gbFileStats)
		self.tabWidgetFileInfo.addTab(self.gbFileStats, "File Statistics")
		
		self.tabWidgetFileInfos.layout().addWidget(self.tabWidgetFileInfo)
		
		self.tabWidgetMain.addTab(self.tabWidgetFileInfos, "File Info")
		
		self.wdgCmd = QWidget()
		self.wdgConsole = QWidget()
		self.layCmdParent = QVBoxLayout()
		self.layCmd = QHBoxLayout()
		self.wdgCmd.setLayout(self.layCmd)
		self.wdgConsole.setLayout(self.layCmdParent)
		
		self.lblCmd = QLabel("Command: ")
		self.lblCmd.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		
		self.txtCmd = HistoryLineEdit()
		self.txtCmd.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
		self.txtCmd.setText("re read")
		self.txtCmd.returnPressed.connect(self.click_execCommand)
		
		self.swtAutoscroll = QSwitch("Autoscroll")
		self.swtAutoscroll.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.swtAutoscroll.setChecked(True)
		
		self.cmdExecuteCmd = QPushButton("Execute")
		self.cmdExecuteCmd.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.cmdExecuteCmd.clicked.connect(self.click_execCommand)
		
		self.cmdClear = QPushButton()
		self.cmdClear.setIcon(ConfigClass.iconBin)
		self.cmdClear.setToolTip("Clear the console log")
		self.cmdClear.setIconSize(QSize(16, 16))
		self.cmdClear.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.cmdClear.clicked.connect(self.clear_clicked)
		
		self.layCmd.addWidget(self.lblCmd)
		self.layCmd.addWidget(self.txtCmd)
		self.layCmd.addWidget(self.cmdExecuteCmd)
		self.layCmd.addWidget(self.swtAutoscroll)
		self.layCmd.addWidget(self.cmdClear)
		self.wdgCmd.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
		
		
		self.txtConsole = QConsoleTextEdit()
		self.txtConsole.setReadOnly(True)
		self.txtConsole.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
		self.txtConsole.setFont(ConfigClass.font)
		self.layCmdParent.addWidget(self.txtConsole)
		self.layCmdParent.addWidget(self.wdgCmd)
		
		self.tabWidgetMain.addTab(self.wdgConsole, "Console")
		
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
				self.loadFileInfo(target.GetExecutable().GetFilename())
				self.loadFileStats(target)
				
				self.process = target.GetProcess()
				if self.process:
					
					
					idx = 0
					self.thread = self.process.GetThreadAtIndex(0)
					if self.thread:
						
#						def BroadcastBitStackChanged(args):
#							print(f"STACK Changed {args}")
#							
#						self.thread.eBroadcastBitStackChanged.connect(BroadcastBitStackChanged)
						
						
						for frame in self.thread:
							print(frame)
							
						self.treThreads.clear()
						self.processNode = QTreeWidgetItem(self.treThreads, ["#0 " + str(self.process.GetProcessID()), hex(self.process.GetProcessID()) + "", self.process.GetTarget().GetExecutable().GetFilename(), '', ''])
						
						self.threadNode = QTreeWidgetItem(self.processNode, ["#" + str(idx) + " " + str(self.thread.GetThreadID()), hex(self.thread.GetThreadID()) + "", self.thread.GetQueueName(), '', ''])
						
				#       print(thread.GetNumFrames())
						for idx2 in range(self.thread.GetNumFrames()):
							frame = self.thread.GetFrameAtIndex(idx2)
				#           print(dir(frame))
							frameNode = QTreeWidgetItem(self.threadNode, ["#" + str(frame.GetFrameID()), "", str(frame.GetPCAddress()), str(hex(frame.GetPC())), lldbHelper.GuessLanguage(frame)]) # + " " + str(thread.GetThreadID()) + " (0x" + hex(thread.GetThreadID()) + ")", thread.GetQueueName()])
						self.processNode.setExpanded(True)
						self.threadNode.setExpanded(True)
		#				pass
						frame = self.thread.GetFrameAtIndex(0)
						if frame:
							
							rip = self.convert_address(frame.register["rip"].value)
							
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
								
								
								self.disassemble_instructions(function.GetInstructions(target), target, rip)
							
							
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
#										print(dir(sym))
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
						
#						self.start_eventListenerWorker(self.debugger, self.interruptEventListenerWorker)
						self.start_loadSourceWorker(self.debugger, "/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/hello_world/hello_world_test.c", self.interruptLoadSourceWorker)
#						self.process.Continue()
				
				print("======== START BP INTER =========")
				for b in target.breakpoint_iter():
					print(b)
				print("========= END BP INTER ==========")
				
				idx = 0
				for i in range(target.GetNumBreakpoints()):
					idx += 1
					bp_cur = target.GetBreakpointAtIndex(i)
					print(bp_cur)
					for bl in bp_cur:
						# Make sure the name list has the remaining name:
						name_list = lldb.SBStringList()
						bp_cur.GetNames(name_list)
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
		
	def reloadBreakpoints(self):
		self.tblBPs.resetContent()
		target = self.driver.getTarget()
		print("======== START BP INTER =========")
		for b in target.breakpoint_iter():
			print(b)
		print("========= END BP INTER ==========")
	
		idx = 0
		for i in range(target.GetNumBreakpoints()):
			idx += 1
			bp_cur = target.GetBreakpointAtIndex(i)
			print(bp_cur)
			for bl in bp_cur:
				# Make sure the name list has the remaining name:
				name_list = lldb.SBStringList()
				bp_cur.GetNames(name_list)
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
				
				
#				self.txtMultiline.table.toggleBPAtAddress(hex(bl.GetLoadAddress()), False)
				
				
	#						self.tblBPs.resetContent()
				self.tblBPs.addRow(bp_cur.GetID(), idx, hex(bl.GetLoadAddress()), name, str(bp_cur.GetHitCount()), bp_cur.GetCondition())
		pass
		
	def convert_address(self, address):		
		# Convert the address to hex
		converted_address = int(address, 16)
		
		# Print the converted address
#       print("Converted address:", hex(converted_address))
		return hex(converted_address)
	
	def updateStatusBar(self, msg):
		self.statusBar.showMessage(msg)
		
	def clear_clicked(self):
		self.txtConsole.setText("")
		
	def click_execCommand(self):
#		print("EXEC COMMAND!!!!")
		newCommand = self.txtCmd.text()
		
		if len(self.txtCmd.lstCommands) > 0:
			if self.txtCmd.lstCommands[len(self.txtCmd.lstCommands) - 1] != newCommand:
				self.txtCmd.lstCommands.append(newCommand)
				self.txtCmd.currCmd = len(self.txtCmd.lstCommands) - 1
			else:
				self.txtCmd.lstCommands.append(newCommand)
				self.txtCmd.currCmd = len(self.txtCmd.lstCommands) - 1
					
		self.start_execCommandWorker(newCommand)
		pass
		
	def start_execCommandWorker(self, command):
		workerExecCommand = ExecCommandWorker(self.debugger, command)
		workerExecCommand.signals.finished.connect(self.handle_commandFinished)
		
		self.threadpool.start(workerExecCommand)
		
	def handle_commandFinished(self, res):
		if res.Succeeded():
			self.txtConsole.appendEscapedText(res.GetOutput())
		else:
			self.txtConsole.appendEscapedText(f"{res.GetError()}")
			
		if self.swtAutoscroll.isChecked():
			self.sb = self.txtConsole.verticalScrollBar()
			self.sb.setValue(self.sb.maximum())
		
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
	
	def disassemble_instructions(self, insts, target, rip):
		idx = 0
		for i in insts:
#			if idx == 0:
#				print(dir(i))
			print(i)
			idx += 1
			print(i.GetData(target))
			self.txtMultiline.appendAsmTextNG(hex(i.GetAddress().GetFileAddress()), i.GetMnemonic(target),  i.GetOperands(target), i.GetComment(target), str(i.GetData(target)).replace("                             ", "\t\t").replace("		            ", "\t\t\t").replace("		         ", "\t\t").replace("		      ", "\t\t").replace("			   ", "\t\t\t"), True, rip)
			
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
	
	def handle_enableBP(self, address, enable):
		self.tblBPs.doEnableBP(address, enable)
#		pass
	
	def handle_BPOn(self, address, on):
		self.tblBPs.doBPOn(address, on)
#		pass
		
	def handle_resumeThread(self):
		print("Trying to Continue ...")
		error = self.process.Continue()
		print("After Continue ...")
#		if error:
#			print(error)
			
	def handle_stopThread(self):
		print("Trying to SIGINT ...")
		error = self.process.Stop()
		print("After SIGINT ...")
		if error:
			print(error)
	
	def stepOver_clicked(self):
		print("Trying to step OVER ...")
		self.thread.StepInstruction(True)
		
		frame = self.thread.GetFrameAtIndex(0)
		
#		for i in range(len(frame.register)):
#			print(frame.register[i])
#		rip = self.convert_address(frame.register["rip"].value)
		
#		print(f'DEEEEEEBBBBBUUUUUGGGG: {lldbHelper.thread} / {lldbHelper.thread.GetNumFrames()} / {frame}')
#		print(f'NEXT STEP {frame.register["rip"].value}')
		
		# Get the current instruction
#       instruction = frame
		print(f'NEXT INSTRUCTION {hex(frame.GetPC())}')
		self.txtMultiline.setPC(frame.GetPC())
		self.reloadBreakpoints()
##       self.regTreeList.clear()
#		for reg in self.regTreeList:
#			reg.clear()
#			
#		self.workerLoadRegister = RegisterLoadWorker(self, lldbHelper.target)
#		self.workerLoadRegister.signals.loadRegister.connect(self.handle_loadRegister)
#		self.workerLoadRegister.signals.loadRegisterValue.connect(self.handle_loadRegisterValue)
#		
#		self.threadpool.start(self.workerLoadRegister)
			
	def stepInto_clicked(self):
		print("Trying to step INTO ...")
		self.thread.StepInto()
		
		frame = self.thread.GetFrameAtIndex(0)
		print(f'NEXT INSTRUCTION {hex(frame.GetPC())}')
		self.txtMultiline.setPC(frame.GetPC())
		self.reloadBreakpoints()
		
	def stepOut_clicked(self):
		print("Trying to step OUT ...")
		self.thread.StepOut()
		
		frame = self.thread.GetFrameAtIndex(0)
		print(f'NEXT INSTRUCTION {hex(frame.GetPC())}')
		self.txtMultiline.setPC(frame.GetPC())
		self.reloadBreakpoints()
		
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