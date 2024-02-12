#!/usr/bin/env python3
import lldb
from lldb import *

import os

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from PyQt6.QConsoleTextEdit import *
from PyQt6.QSwitch import *
from PyQt6.QHEXTextEditSplitter import *

from ui.assemblerTextEdit import *
#from ui.registerTreeView import *
from ui.registerTableWidget import *
from ui.fileInfoTableWidget import *
from ui.fileStructureTreeView import *
from ui.statisticsTreeWidget import *
from ui.breakpointTableWidget import *
from ui.historyLineEdit import *
from ui.threadFrameTreeView import *
from ui.variablesTableWidget import *
from ui.clickLabel import *
from ui.helpDialog import *

from worker.eventListenerWorker import *
from worker.loadSourceWorker import *
from worker.execCommandWorker import *
from worker.loadRegisterWorker import *
from worker.loadBreakpointsWorker import *
from worker.debugWorker import *

from helper import lldbHelper
#import helper.lldbHelper
import lldbutil
from lldbutil import *
from config import *
from helper.dbgHelper import *
from helper.dialogHelper import *
#from test.lldbutil import *

APP_NAME = "LLDB-PyGUI"
WINDOW_SIZE = 680

APP_VERSION = "v0.0.1"

#class UI(QDialog):
#	def __init__(self):
#		super().__init__()
#		
#		# loading the ui file with uic module
#		project_root = dirname(realpath(__file__))
#		helpDialogPath = os.path.join(project_root, 'resources', 'designer', 'helpDialog.ui')
#		
#		uic.loadUi(helpDialogPath, self)
#		print("AFTER INIT helpDialog.ui")
#		self.initTable()
#		
#	def initTable(self):
#		self.setColumnCount(3)
#		self.setColumnWidth(0, 48)
#		self.setColumnWidth(1, 48)
#		self.setColumnWidth(2, 512)
##		self.setColumnWidth(3, 108)
##		self.setColumnWidth(4, 32)
##		self.setColumnWidth(5, 256)
##		self.setColumnWidth(5, 324)
##		self.setColumnWidth(6, 304)
#		self.verticalHeader().hide()
#		self.horizontalHeader().show()
#		self.horizontalHeader().setHighlightSections(False)
#		self.setHorizontalHeaderLabels(['Key', 'Value', 'Description'])#, 'Instruction', 'Hex', 'Comment'])
#		self.horizontalHeaderItem(0).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
#		self.horizontalHeaderItem(1).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
#		self.horizontalHeaderItem(2).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
##		self.horizontalHeaderItem(3).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
##		self.horizontalHeaderItem(4).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
##		self.horizontalHeaderItem(5).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
##		self.horizontalHeaderItem(5).setTextAlignment(Qt.AlignmentFlag.AlignLeft)
##		self.horizontalHeaderItem(6).setTextAlignment(Qt.AlignmentFlag.AlignLeft)
##		self.setFont(ConfigClass.font)
##		
#		self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
#		self.setShowGrid(False)
##		self.cellDoubleClicked.connect(self.on_double_click)
#		pass
		
class LLDBPyGUIWindow(QMainWindow):
	"""PyMobiledevice3GUI's main window (GUI or view)."""
	
#	regTreeList = []
	
	driver = None
	debugger = None
	interruptEventListenerWorker = None
	interruptLoadSourceWorker = None
	process = None
	
	def bpcp(self, msg):
		print(f'IN CALLBACK: {msg}')
		self.load_resume.setIcon(ConfigClass.iconResume)
		
		
	def __init__(self, debugger, driver = None):
		super().__init__()
		self.driver = driver
		self.driver.signals.event_queued.connect(self.handle_event_queued)
		
		self.debugger = debugger
		
		self.setWindowTitle(APP_NAME + " " + APP_VERSION)
		self.setBaseSize(WINDOW_SIZE * 2, WINDOW_SIZE)
		self.setMinimumSize(WINDOW_SIZE * 2, WINDOW_SIZE + 72)
		self.move(1200, 200)
		
		# Create the menu
#		self.menubar = QtWidgets.QMenuBar()
#		self.setMenuBar(self.menubar)
#		
##		self.setMenuWidget(self.menubar)
#		# Create the file menu
#		self.file_menu = QtWidgets.QMenu('KIMTEST', self.menubar)
#		self.menubar.addMenu(self.file_menu)
#		self.menubar.addSeparator()
#		self.menubar.addAction(QAction('TEST', self))
#		
#		# Create the exit action
#		self.exit_action = QAction('Exit', self)
#		self.exit_action.setShortcut('Ctrl+K')
#		self.exit_action.triggered.connect(self.click_exit_action)
#		self.menubar.addAction(self.exit_action)
#		# Add the exit action to the file menu
#		self.file_menu.addAction(self.exit_action)
		
		self.toolbar = QToolBar('Main ToolBar')
		self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)
		self.toolbar.setIconSize(QSize(ConfigClass.toolbarIconSize, ConfigClass.toolbarIconSize))
		
		# new menu item
		self.load_action = QAction(ConfigClass.iconBug, '&Load Target', self)
		self.load_action.setStatusTip('Load Target')
		self.load_action.setShortcut('Ctrl+L')
		self.load_action.triggered.connect(self.load_clicked)
		self.toolbar.addAction(self.load_action)
		
		menu = self.menuBar()
		
		file_menu = menu.addMenu("&Load Action")
		file_menu.addAction(self.load_action)
		
		self.help_action = QAction(ConfigClass.iconInfo, '&Show Help', self)
		self.help_action.setStatusTip('Show Help')
		self.help_action.setShortcut('Ctrl+H')
		self.help_action.triggered.connect(self.click_help)
		
		about_menu = menu.addMenu("&About")
		
#		help_menu = about_menu.addMenu("&Show Help")
		about_menu.addAction(self.help_action)
		
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
		
		self.wgtStatusbarRight = QWidget()
		self.wgtStatusbarRight.setLayout(QHBoxLayout())
		self.wgtStatusbarRight.layout().addWidget(self.progressbar)
		self.wgtStatusbarRight.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.wgtStatusbarRight.setContentsMargins(0, 0, 0, 0)
#		self.wgtStatusbarRight.setMaximumHeight(28)
		self.cmdHelp = ClickLabel()
		self.cmdHelp.setPixmap(ConfigClass.pixInfo)
		self.cmdHelp.clicked.connect(self.click_help)
#		self.cmdHelp.setIconSize(QSize(24, 24))
#		self.cmdHelp.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
#		self.cmdHelp.setContentsMargins(0, 0, 0, 0)
#		self.cmdHelp.setMaximumHeight(38)
		self.wgtStatusbarRight.layout().addWidget(self.cmdHelp)
#		self.wgtStatusbarRight.layout().addWidget(ConfigClass.iconInfo)
		# Add the progress bar to the status bar
		self.statusBar.addPermanentWidget(self.wgtStatusbarRight)
		
		self.layout = QVBoxLayout()
		
		self.txtMultiline = AssemblerTextEditNG(self.driver)
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
		
		self.tblVariables = VariablesTableWidget()
		self.gbpVariables = QGroupBox("Variables")
		self.gbpVariables.setLayout(QHBoxLayout())
		self.gbpVariables.layout().addWidget(self.tblVariables)
		
		self.tabWidgetDbg.addTab(self.gbpVariables, "Variables")
		
		self.txtSource = QConsoleTextEdit()
		self.txtSource.setFont(ConfigClass.font)
		self.gbpSource = QGroupBox("Source")
		self.gbpSource.setLayout(QHBoxLayout())
		self.gbpSource.layout().addWidget(self.txtSource)
		self.tabWidgetDbg.addTab(self.gbpSource, "Source")
		
		self.tblBPs = BreakpointsTableWidget(self.driver)
		
		self.cmdSaveBP = ClickLabel()
		self.cmdSaveBP.setPixmap(ConfigClass.pixSave)
		self.cmdSaveBP.setToolTip("Save Breakpoints")
		self.cmdSaveBP.clicked.connect(self.click_saveBP)
		self.cmdSaveBP.setContentsMargins(0, 0, 0, 0)
		
		self.cmdLoadBP = ClickLabel()
		self.cmdLoadBP.setPixmap(ConfigClass.pixLoad)
		self.cmdLoadBP.setToolTip("Load Breakpoints")
		self.cmdLoadBP.clicked.connect(self.click_loadBP)
		self.cmdLoadBP.setContentsMargins(0, 0, 0, 0)
		
		self.cmdDeleteAllBP = ClickLabel()
		self.cmdDeleteAllBP.setPixmap(ConfigClass.pixTrash)
		self.cmdDeleteAllBP.setToolTip("Delete ALL Breakpoints")
		self.cmdDeleteAllBP.clicked.connect(self.click_deleteAllBP)
		self.cmdDeleteAllBP.setContentsMargins(0, 0, 0, 0)
		
		self.wgtBPCtrls = QWidget()
		self.wgtBPCtrls.setContentsMargins(0, 10, 0, 0)
		self.wgtBPCtrls.setLayout(QHBoxLayout())
		self.wgtBPCtrls.layout().addWidget(self.cmdSaveBP)
		self.wgtBPCtrls.layout().addWidget(self.cmdLoadBP)
		self.wgtBPCtrls.layout().addWidget(self.cmdDeleteAllBP)
#		self.wgtBPCtrls.layout().setContentsMargins(0, 0, 0, 0)
		self.wgtBPCtrls.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
#		self.wgtBPCtrls.layout().addSpacing(200)
		self.gbpBPs = QGroupBox("Breakpoints")
		self.gbpBPs.setLayout(QVBoxLayout())
		self.gbpBPs.layout().addWidget(self.wgtBPCtrls)
		self.gbpBPs.layout().addWidget(self.tblBPs)
		self.gbpBPs.setContentsMargins(0, 0, 0, 0)
#		self.gbpBPs.layout().add
		
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
#		self.tabWidgetMain.setTabEnabled(2)
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
		self.txtCmd.setText(ConfigClass.initialCommand)
		self.txtCmd.returnPressed.connect(self.handle_execCommand)
		
		self.swtAutoscroll = QSwitch("Autoscroll")
		self.swtAutoscroll.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.swtAutoscroll.setChecked(True)
		
		self.cmdExecuteCmd = QPushButton("Execute")
		self.cmdExecuteCmd.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.cmdExecuteCmd.clicked.connect(self.click_execCommand)
		
		self.cmdClear = QPushButton()
		self.cmdClear.setIcon(ConfigClass.iconTrash)
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
		
#		print(f"NUM-TARGETS: {self.debugger.GetNumTargets()}")
	
	def loadTarget(self):
		if self.debugger.GetNumTargets() > 0:
			
#			print(f"TARGET-1: {self.debugger.GetTargetAtIndex(0)}")
			target = self.debugger.GetTargetAtIndex(0)
			
			if target:
				self.loadFileInfo(target.GetExecutable().GetDirectory() + "/" + target.GetExecutable().GetFilename())
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
						
						
#						for frame in self.thread:
#							print(frame)
							
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
						print(f'self.thread.GetNumFrames() {self.thread.GetNumFrames()}')
						frame = self.thread.GetFrameAtIndex(0)
						if frame:
							print(frame)
							rip = lldbHelper.convert_address(frame.register["rip"].value)
							
							########################################################################
							i = 0
							addr = frame.GetPCAddress()
							load_addr = addr.GetLoadAddress(target)
							function = frame.GetFunction()
							mod_name = frame.GetModule().GetFileSpec().GetFilename()
#							print(f'load_addr: {load_addr}')
							if not function:
								# No debug info for 'function'.
								symbol = frame.GetSymbol()
								file_addr = addr.GetFileAddress()
								start_addr = symbol.GetStartAddress().GetFileAddress()
								symbol_name = symbol.GetName()
								symbol_offset = file_addr - start_addr
#								print(f'symbol_name: {symbol_name}')
#								with open("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/my_output.txt", "w") as output:
#								print('  frame #{num}: {addr:#016x} {mod}`{symbol} + {offset}'.format(num=i, addr=load_addr, mod=mod_name, symbol=symbol_name, offset=symbol_offset))
							else:
								# Debug info is available for 'function'.
								func_name = frame.GetFunctionName()
								file_name = frame.GetLineEntry().GetFileSpec().GetFilename()
								line_num = frame.GetLineEntry().GetLine()
#								print(f'function.GetStartAddress().GetFileAddress(): {function.GetStartAddress().	GetFileAddress()}')
#								print(f'func_name: {func_name}')
##								with open("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/my_output.txt", "w") as output:
#								print('  frame #{num}: {addr:#016x} {mod}`{func} at {file}:{line} {args}'.format(num=i, addr=load_addr, mod=mod_name, func='%s [inlined]' % func_name if frame.IsInlined() else func_name, file=file_name, line=line_num, args=get_args_as_string(frame, showFuncName=False))) #args=get_args_as_string(frame, showFuncName=False)), output)
								
								
								self.disassemble_instructions(function.GetInstructions(target), target, rip)
							
							
#							for symbol in frame.GetModule():
#								name = symbol.GetName()
#								saddr = symbol.GetStartAddress()
#								eaddr = symbol.GetEndAddress()
#								type = symbol.GetType()
#								
#								print(f'- SYM: {name} => {saddr} - {eaddr} ({type})')
							
							
							module = frame.GetModule()
#								self.signals.loadSections.emit(frame.GetModule())
#								QCoreApplication.self.processEvents()
							
#							print('Number of sections: %d' % module.GetNumSections())
							for sec in module.section_iter():
#								print(sec)
#								print(sec.GetName())
#								print(f'GetFileByteSize() == {hex(sec.GetFileByteSize())}')
#								print(f'GetByteSize() == {hex(sec.GetByteSize())}')
#								
#								print(f'GetSectionType: {sec.GetSectionType()} / {lldbHelper.SectionTypeString(sec.GetSectionType())}')
								
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
								
								for idx3 in range(sec.GetNumSubSections()):
#									print(sec.GetSubSectionAtIndex(idx3).GetName())
									
									subSec = sec.GetSubSectionAtIndex(idx3)
									
									subSectionNode = QTreeWidgetItem(sectionNode, [subSec.GetName(), str(hex(subSec.GetFileAddress())), str(hex(subSec.GetFileAddress() + subSec.GetByteSize())), hex(subSec.GetFileByteSize()), hex(subSec.GetByteSize()), lldbHelper.SectionTypeString(subSec.GetSectionType()) + " (" + str(subSec.GetSectionType()) + ")"])
									
									for sym in module.symbol_in_section_iter(subSec):
										subSectionNode2 = QTreeWidgetItem(subSectionNode, [sym.GetName(), str(hex(sym.GetStartAddress().GetFileAddress())), str(hex(sym.GetEndAddress().GetFileAddress())), hex(sym.GetSize()), '', f'{lldbHelper.SymbolTypeString(sym.GetType())} ({sym.GetType()})'])
#										print(dir(sym))
#										print(sym.GetName())
#										print(INDENT2 + repr(sym))
#										print(INDENT2 + 'symbol type: %s' % str(sym.GetType())) # symbol_type_to_str
#							pass
							
							self.start_loadRegisterWorker()	
						
#						self.start_eventListenerWorker(self.debugger, self.interruptEventListenerWorker)
							context = frame.GetSymbolContext(lldb.eSymbolContextEverything)
							print(f'.GetLineEntry() => {context.GetLineEntry()} => {context.GetLineEntry().GetLine()}')
							
							self.start_loadSourceWorker(self.debugger, "/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/LLDBPyGUI/testtarget/hello_world_test.c", self.interruptLoadSourceWorker, context.GetLineEntry().GetLine())
#						self.process.Continue()
				
				self.reloadBreakpoints(True)
		
	def handle_event_queued(self, event):
		print("==============================================")
		print(event)
		print(f'GOT-EVENT: {event} / {event.GetType()}')
#		for i in dir(event):
#			print(i)
			
		desc = get_description(event)#, lldb.eDescriptionLevelVerbose)
		print('Event description:', desc)
		print('Event data flavor:', event.GetDataFlavor())
		if event.GetDataFlavor() == "Breakpoint::BreakpointEventData":
			print("GOT BREAKPOINT CHANGE!!!")
			if event.GetType() == lldb.SBTarget.eBroadcastBitBreakpointChanged:
				print("lldb.SBTarget.eBroadcastBitBreakpointChanged")
				bpevent = SBBreakpoint.GetBreakpointFromEvent(event)
				print(bpevent)
				for bl in bpevent:
					print('breakpoint location load addr: %s' % hex(bl.GetLoadAddress()))
					self.tblBPs.doBPOn(hex(bl.GetLoadAddress()), True)
					self.txtMultiline.table.setBPAtAddress(hex(bl.GetLoadAddress()), True, False)
#					print('breakpoint location condition: %s' % hex(bl.GetCondition()))
#			print(f'GetBreakpoint() => {event.GetBreakpoint()}')
				self.driver.handleCommand("br com a -F lldbpyGUI.breakpointHandlerNG")
		print("==============================================")
		pass
		
	def click_saveBP(self):
		filename = showSaveFileDialog()
		if filename != None:
			print(f'Saving to: {filename} ...')
			self.updateStatusBar(f"Saving breakpoints to {filename} ...")
			self.driver.handleCommand(f"breakpoint write -f {filename}")
		pass
		
		
	def click_loadBP(self):
		filename = showOpenBPFileDialog()
		if filename != None:
			print(f'Loading Breakpoints from: {filename} ...')
			self.updateStatusBar(f"Loading Breakpoints from {filename} ...")
			self.driver.handleCommand(f"breakpoint read -f {filename}")
			
#		self.updateStatusBar("Loading breakpoints ...")
		pass
	
	def click_deleteAllBP(self):
#		dlg = ConfirmDialog("Delete all Breakpoints?", "Do you really want to delete all Breakpoints?")
#		if dlg.exec():
		if showQuestionDialog(self, "Delete all Breakpoints?", "Do you really want to delete all Breakpoints?"):
			self.tblBPs.resetContent()
			self.updateStatusBar("Deleted all Breakpoints!")			
		pass
		
	def click_exit_action(self):
		self.close()
		pass
		
	def reloadBreakpoints(self, initTable = True):
		self.updateStatusBar("Reloading breakpoints ...")
#		if initTable: # TODO: Implement Update instead of complete refresh
		self.tblBPs.resetContent()
		self.start_loadBreakpointsWorker(initTable)
		
	def reloadRegister(self, initTabs = True):
		self.updateStatusBar("Reloading registers ...")
		if initTabs:
			self.tabWidgetReg.clear()
		self.start_loadRegisterWorker(initTabs)
		
#	def convert_address(self, address):		
#		# Convert the address to hex
#		converted_address = int(address, 16)
#		
#		# Print the converted address
#		return hex(converted_address)
	
	def setProgressValue(self, newValue):
		self.progressbar.setValue(newValue)
		pass
		
	def updateStatusBar(self, msg):
		self.statusBar.showMessage(msg)
		
	def clear_clicked(self):
		self.txtConsole.setText("")
	
	def start_loadBreakpointsWorker(self, initTable = True):
		self.loadBreakpointsWorker = LoadBreakpointsWorker(self.driver, initTable)
		self.loadBreakpointsWorker.signals.finished.connect(self.handle_loadBreakpointsFinished)
		self.loadBreakpointsWorker.signals.sendStatusBarUpdate.connect(self.handle_statusBarUpdate)
		self.loadBreakpointsWorker.signals.sendProgressUpdate.connect(self.handle_progressUpdate)
		
#		self.loadBreakpointsWorker.signals.loadRegister.connect(self.handle_loadRegisterLoadRegister)
		self.loadBreakpointsWorker.signals.loadBreakpointsValue.connect(self.handle_loadBreakpointsLoadBreakpointValue)
#		self.loadBreakpointsWorker.signals.updateRegisterValue.connect(self.handle_loadRegisterUpdateRegisterValue)
		
		self.threadpool.start(self.loadBreakpointsWorker)
		
	def handle_loadBreakpointsLoadBreakpointValue(self, bpId, idx, loadAddr, name, hitCount, condition, initTable):
		if initTable:
			self.txtMultiline.table.setBPAtAddress(loadAddr, True, False)
		self.tblBPs.addRow(bpId, idx, loadAddr, name, str(hitCount), condition)
		print("Reloading BPs ...")
		
	def handle_loadBreakpointsFinished(self):
		pass
		
	def start_loadRegisterWorker(self, initTabs = True):
		self.loadRegisterWorker = LoadRegisterWorker(self.driver, initTabs)
		self.loadRegisterWorker.signals.finished.connect(self.handle_loadRegisterFinished)
		self.loadRegisterWorker.signals.sendStatusBarUpdate.connect(self.handle_statusBarUpdate)
		self.loadRegisterWorker.signals.sendProgressUpdate.connect(self.handle_progressUpdate)
		
		self.loadRegisterWorker.signals.loadRegister.connect(self.handle_loadRegisterLoadRegister)
		self.loadRegisterWorker.signals.loadRegisterValue.connect(self.handle_loadRegisterLoadRegisterValue)
		self.loadRegisterWorker.signals.updateRegisterValue.connect(self.handle_loadRegisterUpdateRegisterValue)
		
		self.loadRegisterWorker.signals.loadVariableValue.connect(self.handle_loadRegisterLoadVariableValue)
		self.loadRegisterWorker.signals.updateVariableValue.connect(self.handle_loadRegisterUpdateVariableValue)
		
		
		
		self.threadpool.start(self.loadRegisterWorker)
		
	def handle_loadRegisterFinished(self):
		self.setProgressValue(100)
		self.updateStatusBar("Loading register finished")
		
	def handle_statusBarUpdate(self, txt):
		self.updateStatusBar(txt)
	
	def handle_progressUpdate(self, value, statusTxt):
		self.setProgressValue(value)
		self.updateStatusBar(statusTxt)
		
	currTreDet = None
	def handle_loadRegisterLoadRegister(self, type):
		tabDet = QWidget()
		tblReg = RegisterTableWidget()
		tabDet.tblWdgt = tblReg
#		self.regTreeList.append(treDet)
		tabDet.setLayout(QVBoxLayout())
		tabDet.layout().addWidget(tblReg)
		self.tabWidgetReg.addTab(tabDet, type)
		self.currTblDet = tblReg
		
	def handle_loadRegisterLoadRegisterValue(self, idx, type, register, value):
		target = self.driver.getTarget()
		process = target.GetProcess()
#		print(f'idx: {idx}, type: {type}, register: {register}, value: {value}')
		self.currTblDet.addRow(type, register, value)
		
	def handle_loadRegisterUpdateRegisterValue(self, idx, type, register, value):
		tblWdgt = self.tabWidgetReg.widget(idx).tblWdgt
		for i in range(tblWdgt.rowCount()):
			if tblWdgt.item(i, 0).text() == type:
				tblWdgt.item(i, 1).setText(register)
				tblWdgt.item(i, 2).setText(value)
				break
			
	def handle_loadRegisterLoadVariableValue(self, name, value, valType):
		self.tblVariables.addRow(name, value, valType)
		
	def handle_loadRegisterUpdateVariableValue(self, name, value, valType):
		tblWdgt = self.tblVariables
		for i in range(tblWdgt.rowCount()):
			if tblWdgt.item(i, 0).text() == name:
				tblWdgt.item(i, 1).setText(value)
				tblWdgt.item(i, 2).setText(valType)
				break
	
	def handle_execCommand(self):
		self.do_execCommand()
		
	def click_help(self):
		self.updateStatusBar("Help for LLDBPyGUI opening ...")
		
#		project_root = dirname(realpath(__file__))
#		helpDialogPath = os.path.join(project_root, 'resources', 'designer', 'helpDialog.ui')
#		
#		window = uic.loadUi(helpDialogPath)
		helpWindow = HelpDialog()
		helpWindow.exec()
		pass
		
	def click_execCommand(self):
		self.do_execCommand(True)
#		print("EXEC COMMAND!!!!")
#		newCommand = self.txtCmd.text()
#		
#		if len(self.txtCmd.lstCommands) > 0:
#			if self.txtCmd.lstCommands[len(self.txtCmd.lstCommands) - 1] != newCommand:
#				self.txtCmd.lstCommands.append(newCommand)
#				self.txtCmd.currCmd = len(self.txtCmd.lstCommands) - 1
#			else:
#				self.txtCmd.lstCommands.append(newCommand)
#				self.txtCmd.currCmd = len(self.txtCmd.lstCommands) - 1
		pass
		
	def do_execCommand(self, addCmd2Hist = False):
		if addCmd2Hist:
			self.txtCmd.addCommandToHistory()
		self.start_execCommandWorker(self.txtCmd.text())
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
		
		mach_header = helper.lldbHelper.GetFileHeader(target)
		
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
#			print(i)
			idx += 1
#			print(i.GetData(target))
			self.txtMultiline.appendAsmTextNG(hex(int(str(i.GetAddress().GetFileAddress()), 10)), i.GetMnemonic(target),  i.GetOperands(target), i.GetComment(target), str(i.GetData(target)).replace("                             ", "\t\t").replace("		            ", "\t\t\t").replace("		         ", "\t\t").replace("		      ", "\t\t").replace("			   ", "\t\t\t"), True, rip)
			
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
		
	def start_loadSourceWorker(self, debugger, sourceFile, event_listener, lineNum = 1):
		self.workerLoadSource = LoadSourceCodeWorker(debugger, sourceFile, event_listener, lineNum)
		self.workerLoadSource.signals.finished.connect(self.handle_loadSourceFinished)
		
		self.threadpool.start(self.workerLoadSource)
	
	def handle_enableBP(self, address, enable):
		self.tblBPs.doEnableBP(address, enable)
#		pass
	
	def handle_BPOn(self, address, on):
		self.tblBPs.doBPOn(address, on)
#		print(f"breakpoint set -a {address} -C bpcbdriver")
		if on:
#			self.driver.handleCommand(f"breakpoint set -a {address} -C bpcb")
			res = lldb.SBCommandReturnObject()
			ci = self.driver.debugger.GetCommandInterpreter()
			ci.HandleCommand(f"breakpoint set -a {address} -C bpcb", res)
#		pass
		
	def handle_resumeThread(self):
		print("Trying to Continue ...")
#		error = self.process.Continue()
		self.start_debugWorker(self.driver, StepKind.Continue)
		self.load_resume.setIcon(ConfigClass.iconPause)
		print("After Continue ...")
#		if error:
#			print(error)
			
	def handle_stopThread(self):
		print("Trying to SIGINT ...")
		error = self.process.Stop()
		print("After SIGINT ...")
		if error:
			print(error)
	
	
	def start_debugWorker(self, driver, kind):
		self.workerDebug = DebugWorker(driver, kind)
		self.workerDebug.signals.debugStepCompleted.connect(self.handle_debugStepCompleted)
		
		self.threadpool.start(self.workerDebug)
		
	def handle_debugStepCompleted(self, kind, success, rip, frm):
		if success:
#			print(f"Debug STEP ({kind}) completed SUCCESSFULLY")
			self.txtMultiline.setPC(int(str(rip), 16))
#			print(f'NEXT INSTRUCTION {rip}')
#			self.txtMultiline.setPC(frame.GetPC())
			self.reloadRegister(False)
			self.reloadBreakpoints(False)
#			self.driver.getTarget()
			context = frm.GetSymbolContext(lldb.eSymbolContextEverything)
			print(f'.GetLineEntry() => {context.GetLineEntry()} => {context.GetLineEntry().GetLine()}')
			self.start_loadSourceWorker(self.debugger, "/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/LLDBPyGUI/testtarget/hello_world_test.c", self.interruptLoadSourceWorker, context.GetLineEntry().GetLine())
		else:
			print(f"Debug STEP ({kind}) FAILED!!!")
		pass
	
	def stepOver_clicked(self):
		print("Trying to step OVER ...")
#		self.driver.debugger.SetAsync(True)
#		self.thread.StepInstruction(True)
		
		self.start_debugWorker(self.driver, StepKind.StepOver)
		
#		print(self.driver.getTarget().GetProcess().GetThreadAtIndex(0))
##		print(self.driver.getTarget().GetProcess().GetThreadAtIndex(0))
#		for frame in self.driver.getTarget().GetProcess().GetThreadAtIndex(0):
##		self.assertTrue(frame.GetThread().GetThreadID() == ID)
##		if self.TraceOn():
#			print(frame)
##		self.thread.StepOver()
#		frame = self.thread.GetFrameAtIndex(0)
#		print(frame)
##		self.driver.debugger.SetAsync(True)
#		
#		
#		
##		for i in range(len(frame.register)):
##			print(frame.register[i])
##		rip = self.convert_address(frame.register["rip"].value)
#		
##		print(f'DEEEEEEBBBBBUUUUUGGGG: {lldbHelper.thread} / {lldbHelper.thread.GetNumFrames()} / {frame}')
##		print(f'NEXT STEP {frame.register["rip"].value}')
#		
#		# Get the current instruction
##       instruction = frame
#		print(f'NEXT INSTRUCTION {hex(frame.GetPC())}')
#		self.txtMultiline.setPC(frame.GetPC())
#		self.reloadRegister(False)
#		self.reloadBreakpoints(False)
		
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
#		self.driver.debugger.SetAsync(False)
		self.thread.StepInto()
#		self.driver.debugger.SetAsync(True)
		
		frame = self.thread.GetFrameAtIndex(0)
		print(f'NEXT INSTRUCTION {hex(frame.GetPC())}')
		self.txtMultiline.setPC(frame.GetPC())
		self.reloadRegister(False)
		self.reloadBreakpoints(False)
		
	def stepOut_clicked(self):
		print("Trying to step OUT ...")
#		self.driver.debugger.SetAsync(False)
		self.thread.StepOut()
#		self.driver.debugger.SetAsync(True)
		
		frame = self.thread.GetFrameAtIndex(0)
		print(f'NEXT INSTRUCTION {hex(frame.GetPC())}')
		self.txtMultiline.setPC(frame.GetPC())
		self.reloadRegister(False)
		self.reloadBreakpoints(False)
		
	def handle_loadSourceFinished(self, sourceCode):
		if sourceCode != "":
#			log(sourceCode)
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