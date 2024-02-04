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
from ui.statisticsTreeWidget import *

from worker.eventListenerWorker import *

import lldbHelper
from config import *

APP_NAME = "LLDB-PyGUI"
WINDOW_SIZE = 680

APP_VERSION = "v0.0.1"

class LLDBPyGUIWindow(QMainWindow):
	"""PyMobiledevice3GUI's main window (GUI or view)."""
	
#	regTreeList = []
	
	debugger = None
	
	def __init__(self, debugger):
		super().__init__()
		self.debugger = debugger
		
		self.setWindowTitle(APP_NAME + " " + APP_VERSION)
		self.setBaseSize(WINDOW_SIZE * 2, WINDOW_SIZE)
		self.setMinimumSize(WINDOW_SIZE * 2, WINDOW_SIZE + 72)
		
		self.toolbar = QToolBar('Main ToolBar')
		self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)
		self.toolbar.setIconSize(QSize(ConfigClass.toolbarIconSize, ConfigClass.toolbarIconSize))
		
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
		
		self.txtMultiline = AssemblerTextEdit()
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
		self.tabWidgetDbg.addTab(QConsoleTextEdit(), "Source")
		self.tabWidgetDbg.addTab(QTextEdit(), "Break-/Watchpoints")
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
		
		self.gbFileStats = QGroupBox("File Statistics")
		self.gbFileStats.setLayout(QHBoxLayout())
		self.gbFileStats.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
		
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
		
		self.threadpool = QThreadPool()
		
		print(f"NUM-TARGETS: {self.debugger.GetNumTargets()}")
		if self.debugger.GetNumTargets() > 0:
			
			print(f"TARGET-1: {self.debugger.GetTargetAtIndex(0)}")
			target = self.debugger.GetTargetAtIndex(0)
			
			if target:
				self.loadFileInfo(target.GetExecutable().GetFilename())
				self.loadFileStats(target)
				
				process = target.GetProcess()
				if process:
					thread = process.GetThreadAtIndex(0)
					if thread:
		#				pass
						frame = thread.GetFrameAtIndex(0)
						if frame:
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
										data = self.read_memory(process, target.ResolveLoadAddress(int(child.GetValue(), 16)), size)
										
										hex_string = ''.join("%02x" % byte for byte in data)
										
										formatted_hex_string = ' '.join(re.findall(r'.{2}', hex_string))
										memoryValue = formatted_hex_string
		
									except Exception as e:
#                              				print(f"Error getting memory for addr: {e}")
										pass
										
#									self.signals.loadRegisterValue.emit(currReg, child.GetName(), child.GetValue(), memoryValue)
#									QCoreApplication.processEvents()
									registerDetailNode = QTreeWidgetItem(treDet, [child.GetName(), child.GetValue(), memoryValue])
						
						self.start_eventListenerWorker(self.debugger)
#						process.Continue()	
	
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
		
	def loadFileStats(self, target):
		statistics = target.GetStatistics()
		stream = lldb.SBStream()
		success = statistics.GetAsJSON(stream)
		if success:
#			self.signals.loadStats.emit(str(stream.GetData()))
			
			self.treStats.loadJSON(str(stream.GetData()))
		
	def start_eventListenerWorker(self, debugger):
		workerEventListener = EventListenerWorker(debugger)
#		workerEventListener.signals.finished.connect(self.handle_commandFinished)
		
		self.threadpool.start(workerEventListener)
		
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
							