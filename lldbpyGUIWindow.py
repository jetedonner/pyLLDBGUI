#!/usr/bin/env python3
import lldb
from lldb import *

import os

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from QConsoleTextEdit import *
from QSwitch import *
from QHEXTextEditSplitter import *

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
from ui.settingsDialog import *
from ui.widgets.QHexTableWidget import *
from ui.widgets.QMemoryViewer import *
from ui.searchTableWidget import *
#from ui.testTableWidget import *

from worker.eventListenerWorker import *
from worker.loadSourceWorker import *
from worker.execCommandWorker import *
from worker.loadRegisterWorker import *
from worker.loadBreakpointsWorker import *
from worker.debugWorker import *
from worker.loadDisassemblyWorker import *
from worker.findReferencesWorker import *

from helper import lldbHelper
#import helper.lldbHelper
import lldbutil
from lldbutil import *
from config import *
from helper.dbgHelper import *
from helper.dialogHelper import *
from lldbpyGUIConfig import *
from listener import *

try:
	import queue
except ImportError:
	import Queue as queue

global event_queueBP
event_queueBP = queue.Queue()
#from debuggerdriver import LLDBListenerThread
#from test.lldbutil import *

#APP_NAME = "LLDB-PyGUI"
#WINDOW_SIZE = 680

#APP_VERSION = "v0.0.1"
#global myProcess
#myProcess = None
#
#def worker2():
#	from lldbutil import print_stacktrace
#	stopped_due_to_breakpoint = False
#	global myProcess
#	for thread in myProcess:
#		if self.TraceOn():
#			print_stacktrace(thread)
#		ID = thread.GetThreadID()
#		if thread.GetStopReason() == lldb.eStopReasonBreakpoint:
#			stopped_due_to_breakpoint = True
#		for frame in thread:
#			self.assertTrue(frame.GetThread().GetThreadID() == ID)
#			if self.TraceOn():
#				print frame
#	pass

def worker():
	while True:
		global event_queueBP
		item = event_queueBP.get()
		print(f'Working on {item}')
#		print(f'Finished {item}')
		event_queueBP.task_done()
		
		# Turn-on the worker thread.
threading.Thread(target=worker, daemon=True).start()

global my_target
def myTest():
	print("MYTEST")
	
def my_callback(frame, bp_loc, dict): # self,
	
	global event_queueBP
	event_queueBP.put(bp_loc)
	QCoreApplication.processEvents()
	
	# Your code to execute when the breakpoint hits
	print(f"Breakpoint hit!!!!!!!! =========>>>>>>>>  YEESSSS 123 {bp_loc}!!!!!!")
	
#	LLDBPyGUIWindow.call_instance_method("hello")
	
#	global pymobiledevice3GUIWindow
	
	# Access the frame, breakpoint location, and any extra arguments passed to the callback
	print(f'bp_loc.GetBreakpoint() => {bp_loc.GetBreakpoint()} / frame => {frame}')
	
	if frame.GetThread().GetStopReason() == lldb.eStopReasonBreakpoint:
		print(f'frame.GetThread().GetStopReason() == lldb.eStopReasonBreakpoint')
	
	
#	global my_window
#	my_window.my_callbackWindow(frame, bp_loc, dict)

global my_window
my_window = None

class LLDBPyGUIWindow(QMainWindow):
	"""PyMobiledevice3GUI's main window (GUI or view)."""
	
#	regTreeList = []
	global my_target
	my_target = myTest
	driver = None
	debugger = None
	interruptEventListenerWorker = None
	interruptLoadSourceWorker = None
	process = None
	
	bpHelper = None
	
	def my_function(self, arg):
		print(f'HEEEEEEEELLLLLLLLOOOOOO ARG {arg}')
		
	def my_class_method(cls, instance, arg):
			instance.my_function(arg)  # Assuming access to the instance
		
	@classmethod
	def call_instance_method(cls, arg):
		global my_window
		# You can get the instance here (e.g., from a static variable)
		instance = my_window# get_instance()
		cls.my_class_method(cls, instance, arg)
			
	def bpcp(self, msg):
		print(f'IN CALLBACK: {msg}')
		self.load_resume.setIcon(ConfigClass.iconResume)
		self.updateStatusBar("Breakpoint hit!")
		
	def setResumeActionIcon(self, icon):
		self.load_resume.setIcon(icon)
		pass
		
	def onQApplicationStarted(self):
		print('onQApplicationStarted started')
		self.driver.createTarget("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/LLDBPyGUI/testtarget/hello_world_test")
		if self.driver.debugger.GetNumTargets() > 0:
			target = self.driver.getTarget()
			
			fname = "main"
			main_bp = target.BreakpointCreateByName(fname, target.GetExecutable().GetFilename())
			main_bp.AddName(fname)
#			print(main_bp)
			
			
						
			process = target.LaunchSimple(None, None, os.getcwd())
			
#			error = lldb.SBError()
#			main_wp = target.WatchAddress(int("0x304113084", 16), 0x1, False, True, error)
#			print(error)
#			print(main_wp)
#			
			self.loadTarget()
#			
#			loop_wp = target.WatchAddress(int("0x304113088", 16), 0x4, False, True, error)
#			print(error)
#			print(loop_wp)
			
	def my_callbackWindow(self, frame, bp_loc, dict): # self, 
		# Your code to execute when the breakpoint hits
		print(f"Breakpoint hit!!!!!!!! =========>>>>>>>>  WINDOW !!!!!! {bp_loc}!!!!!!")
		# Access the frame, breakpoint location, and any extra arguments passed to the callback
	
#	def worker(self):
#		while True:
#			global event_queueBP
#			item = event_queueBP.get()
#			print(f'Working on {item}')
#			print(f'Finished {item}')
#			event_queueBP.task_done()
#			
##	# Turn-on the worker thread.
#		threading.Thread(target=self.worker, daemon=True).start()
	
	def __init__(self, debugger, driver = None):
		super().__init__()
		global my_window
		my_window = self
		
#		global my_window
#		my_window = None
		
		# Turn-on the worker thread.
#		threading.Thread(target=self.worker, daemon=True).start()
		
		self.driver = driver
		self.driver.signals.event_queued.connect(self.handle_event_queued)
		self.driver.signals.event_output.connect(self.handle_output)
		
		self.bpHelper = BreakpointHelper(self, self.driver)
		self.setHelper = SettingsHelper()
		
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
		
		self.settings_action = QAction(ConfigClass.iconSettings, 'Settings', self)
		self.settings_action.setStatusTip('Settings')
		self.settings_action.setShortcut('Ctrl+O')
		self.settings_action.triggered.connect(self.settings_clicked)
#		self.toolbar.addAction(self.settings_action)
#		self.toolbar.addAction(self.settings_action)
		
		menu = self.menuBar()
		
		main_menu = menu.addMenu("Main")
		main_menu.addAction(self.settings_action)
		
		file_menu = menu.addMenu("&Load Action")
		file_menu.addAction(self.load_action)
#		file_menu.addAction(self.settings_action)
		
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
		self.load_resume.setShortcut('Ctrl+R')
		self.step_restart.triggered.connect(self.click_restartTarget)
		self.toolbar.addAction(self.step_restart)
		
		self.stop = QAction(ConfigClass.iconStop, '&Stop', self)
		self.stop.setStatusTip('Stop')
#		self.load_resume.setShortcut('Ctrl+L')
		self.stop.triggered.connect(self.handle_stopThread)
		self.toolbar.addAction(self.stop)
		
		self.toolbar.addAction(self.settings_action)
		
		file_menu.addAction(self.settings_action)
		
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
		
		self.txtMultiline = AssemblerTextEdit(self.driver)
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
#		self.tabWidgetDbg.setContentsMargins(0, 0, 0, 0)
		self.splitter.addWidget(self.tabWidgetDbg)
		
#		self.txtSource = QConsoleTextEdit()
#		self.txtSource.setFont(ConfigClass.font)
#		self.gbpSource = QGroupBox("Source")
#		self.gbpSource.setLayout(QHBoxLayout())
#		self.gbpSource.layout().addWidget(self.txtSource)
#		self.tabWidgetDbg.addTab(self.gbpSource, "Source")
		
		self.tabWidgetReg = QTabWidget()
		self.tabWidgetReg.setContentsMargins(0, 0, 0, 0)
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
		
		self.wdtBPsWPs = BPsWPsWidget(self.driver)
		
		self.tabWidgetDbg.addTab(self.wdtBPsWPs, "Break-/Watchpoints")
		
		self.treThreads = ThreadFrameTreeWidget()
		self.treThreads.setFont(ConfigClass.font)
		self.treThreads.setHeaderLabels(['Num / ID', 'Hex ID', 'Process / Threads / Frames', 'PC', 'Lang (guess)'])
		self.treThreads.header().resizeSection(0, 148)
		self.treThreads.header().resizeSection(1, 128)
		self.treThreads.header().resizeSection(2, 512)
		self.treThreads.header().resizeSection(3, 128)
		
		self.gbpThreads = QGroupBox("Threads / Frames")
		self.gbpThreads.setLayout(QHBoxLayout())
		self.gbpThreads.layout().addWidget(self.treThreads)
		
		self.tabWidgetDbg.addTab(self.gbpThreads, "Threads/Frames")
		
		self.tblHex = QMemoryViewer(self.driver)
		
		self.tabMemory = QWidget()
		self.tabMemory.setLayout(QVBoxLayout())
		self.tabMemory.layout().addWidget(self.tblHex)
		
		self.tabWidgetDbg.addTab(self.tabMemory, "Memory")
		
		self.wdtSearch = SearchWidget(self.driver)
		self.tabWidgetDbg.addTab(self.wdtSearch, "Search")
		
		self.txtOutput = QConsoleTextEdit()
		self.txtOutput.setFont(ConfigClass.font)
		self.txtOutput.setReadOnly(True)
#		self.gbpOutput = QGroupBox("Stacktrace")
#		self.gbpOutput.setLayout(QHBoxLayout())
#		self.gbpOutput.layout().addWidget(self.txtOutput)
		self.tabWidgetDbg.addTab(self.txtOutput, "Stacktrace")
		
		self.tabWidgetMain = QTabWidget()
		self.tabWidgetMain.addTab(self.splitter, "Debugger")
		
#		self.tblTest = TestTableWidgetNG()
#		self.tabWidgetMain.addTab(self.tblTest, "TEST")
#		self.tblTest.addRow(1, "0x10000", "HELLO", "ARGS", "COMMENT", "DATA", "0x10000")
		
		self.tblFileInfos = FileInfosTableWidget()
		self.tabWidgetFileInfos = QWidget()
		self.tabWidgetFileInfos.setLayout(QVBoxLayout())
		
		self.tabWidgetFileInfo = QTabWidget()
		
		self.gbFileInfo = QGroupBox("File Header / General Infos")
		self.gbFileInfo.setLayout(QHBoxLayout())
		self.gbFileInfo.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
		self.gbFileInfo.layout().addWidget(self.tblFileInfos)
		
		self.splitterFileInfos = QSplitter()
		self.splitterFileInfos.setContentsMargins(0, 0, 0, 0)
		self.splitterFileInfos.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.splitterFileInfos.setOrientation(Qt.Orientation.Vertical)
		
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
		
		self.tabWidgetFileInfo.addTab(self.gbFileStats, "File Statistics")
		
		self.tabWidgetFileInfos.layout().addWidget(self.tabWidgetFileInfo)
		
		self.tabWidgetMain.addTab(self.tabWidgetFileInfos, "File Info")
		self.wdgCmd = QWidget()
		self.wdgCommands = QWidget()
		self.layCmdParent = QVBoxLayout()
		self.layCmd = QHBoxLayout()
		self.wdgCmd.setLayout(self.layCmd)
		self.wdgCommands.setLayout(self.layCmdParent)
		
		self.lblCmd = QLabel("Command: ")
		self.lblCmd.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		
		self.txtCmd = HistoryLineEdit(self.setHelper.getValue(SettingsValues.CmdHistory))
		self.txtCmd.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
		self.txtCmd.setText(ConfigClass.initialCommand)
		self.txtCmd.returnPressed.connect(self.handle_execCommand)
		
		self.swtAutoscroll = QSwitch("Autoscroll")
		self.swtAutoscroll.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.swtAutoscroll.setChecked(True)
		
		self.cmdExecuteCmd = QPushButton("Execute")
		self.cmdExecuteCmd.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.cmdExecuteCmd.clicked.connect(self.handle_execCommand)
		
		self.cmdClear = QPushButton()
		self.cmdClear.setIcon(ConfigClass.iconTrash)
		self.cmdClear.setToolTip("Clear the Commands log")
		self.cmdClear.setIconSize(QSize(16, 16))
		self.cmdClear.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.cmdClear.clicked.connect(self.clear_clicked)
		
		self.layCmd.addWidget(self.lblCmd)
		self.layCmd.addWidget(self.txtCmd)
		self.layCmd.addWidget(self.cmdExecuteCmd)
		self.layCmd.addWidget(self.swtAutoscroll)
		self.layCmd.addWidget(self.cmdClear)
		self.wdgCmd.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)		
		
		self.txtCommands = QConsoleTextEdit()
		self.txtCommands.setReadOnly(True)
		self.txtCommands.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
		self.txtCommands.setFont(ConfigClass.font)
		self.layCmdParent.addWidget(self.txtCommands)
		self.layCmdParent.addWidget(self.wdgCmd)
		
		self.tabWidgetMain.addTab(self.wdgCommands, "Commands")
		
		self.layout.addWidget(self.tabWidgetMain)
		
		self.centralWidget = QWidget(self)
		self.centralWidget.setLayout(self.layout)        
		self.setCentralWidget(self.centralWidget)
		
		self.interruptEventListenerWorker = EventListenerReceiver()
		self.interruptLoadSourceWorker = LoadSourceCodeReceiver()
		
		self.threadpool = QThreadPool()
		
		self.tabWidgetDbg.setCurrentIndex(6)
	
	def my_callback(self, frame, bp_loc, dict):
		# Your code to execute when the breakpoint hits
		print("Breakpoint hit!!!!!!!! =========>>>>>>>>  YEESSSS!!!!!!")
		# Access the frame, breakpoint location, and any extra arguments passed to the callback
		
		
	def handle_stdoutEvent(self, data):
		print(f'EVENT: {data}')
		pass
		
	def handle_breakpointEvent(self, event):
		breakpoint = SBBreakpoint.GetBreakpointFromEvent(event)
		bpEventType = SBBreakpoint.GetBreakpointEventTypeFromEvent(event)
		
		print(f'GOT BREAKPOINT EVENT: {breakpoint} => TYPE: {bpEventType}')
		
		if bpEventType == lldb.eBreakpointEventTypeAdded:
			print(f"BP ID: {breakpoint.GetID()} has been ADDED !!!!!!!!!!!!!!")
			self.event_bpAdded(breakpoint)
			pass
		elif bpEventType == lldb.eBreakpointEventTypeRemoved:
			print(f"BP ID: {breakpoint.GetID()} has been DELETED !!!!!!!!!!!!!!")
#			self.bpHelper.handle_deleteBP(self.breakpoint.GetID())
			self.wdtBPsWPs.tblBPs.removeRowWithId(breakpoint.GetID())
			
			for i in range(breakpoint.GetNumLocations()):
				self.txtMultiline.table.removeBPAtAddress(hex(breakpoint.GetLocationAtIndex(i).GetLoadAddress()))
				pass
		
	def event_bpAdded(self, bp):
		print(f'bp.GetID() => {bp.GetID()}')
		for i in range(bp.GetNumLocations()):
			bl = bp.GetLocationAtIndex(i)
			self.txtMultiline.table.event_bpAdded(bl)
			self.wdtBPsWPs.tblBPs.event_bpAdded(bl)
		
	def loadTarget(self):
		if self.debugger.GetNumTargets() > 0:
			
#			print(f"TARGET-1: {self.debugger.GetTargetAtIndex(0)}")
			target = self.debugger.GetTargetAtIndex(0)
			
			if target:
				print(f'target.GetTriple() => {target.GetTriple()}')
#				self.start_loadDisassemblyWorker(True)
				
				self.loadFileInfo(target.GetExecutable().GetDirectory() + "/" + target.GetExecutable().GetFilename())
				self.loadFileStats(target)
				
				self.loadTestBPs(ConfigClass.testBPsFilename)
				
				self.process = target.GetProcess()
				if self.process:
					
					self.listener = LLDBListener(self.process)
					self.listener.breakpointEvent.connect(self.handle_breakpointEvent)
					self.listener.stdoutEvent.connect(self.handle_stdoutEvent)
					
					self.listener.start()
					
					idx = 0
					self.thread = self.process.GetThreadAtIndex(0)
					if self.thread:
						
#						self.loadStacktrace()
#						self.treThreads.clear()
#						self.processNode = QTreeWidgetItem(self.treThreads, ["#0 " + str(self.process.GetProcessID()), hex(self.process.GetProcessID()) + "", self.process.GetTarget().GetExecutable().GetFilename(), '', ''])
#						
#						self.threadNode = QTreeWidgetItem(self.processNode, ["#" + str(idx) + " " + str(self.thread.GetThreadID()), hex(self.thread.GetThreadID()) + "", self.thread.GetQueueName(), '', ''])
#						
#						for idx2 in range(self.thread.GetNumFrames()):
#							frame = self.thread.GetFrameAtIndex(idx2)
#							frameNode = QTreeWidgetItem(self.threadNode, ["#" + str(frame.GetFrameID()), "", str(frame.GetPCAddress()), str(hex(frame.GetPC())), lldbHelper.GuessLanguage(frame)])
#						
#						self.processNode.setExpanded(True)
#						self.threadNode.setExpanded(True)
						
#						print(f'self.thread.GetNumFrames() {self.thread.GetNumFrames()}')
						frame = self.thread.GetFrameAtIndex(0)
						if frame:
							print(frame)
							rip = lldbHelper.convert_address(frame.register["rip"].value)
							self.rip = rip
							self.start_loadDisassemblyWorker(True)
#							########################################################################
#							i = 0
#							addr = frame.GetPCAddress()
#							load_addr = addr.GetLoadAddress(target)
#							function = frame.GetFunction()
#							print(f'function => {function}')
#							mod_name = frame.GetModule().GetFileSpec().GetFilename()
#							#							print(f'load_addr: {load_addr}')
#							if not function:
#								# No debug info for 'function'.
#								symbol = frame.GetSymbol()
#								file_addr = addr.GetFileAddress()
#								start_addr = symbol.GetStartAddress().GetFileAddress()
#								symbol_name = symbol.GetName()
#								symbol_offset = file_addr - start_addr
#								#								print(f'symbol_name: {symbol_name}')
#								#								with open("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/my_output.txt", "w") as output:
#								#								print('  frame #{num}: {addr:#016x} {mod}`{symbol} + {offset}'.format(num=i, addr=load_addr, mod=mod_name, symbol=symbol_name, offset=symbol_offset))
#							else:
#								# Debug info is available for 'function'.
#								func_name = frame.GetFunctionName()
#								file_name = frame.GetLineEntry().GetFileSpec().GetFilename()
#								line_num = frame.GetLineEntry().GetLine()
#								#								print(f'function.GetStartAddress().GetFileAddress(): {function.GetStartAddress().	GetFileAddress()}')
#								#								print(f'func_name: {func_name}')
#								##								with open("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/my_output.txt", "w") as output:
#								#								print('  frame #{num}: {addr:#016x} {mod}`{func} at {file}:{line} {args}'.format(num=i, addr=load_addr, mod=mod_name, func='%s [inlined]' % func_name if frame.IsInlined() else func_name, file=file_name, line=line_num, args=get_args_as_string(frame, showFuncName=False))) #args=get_args_as_string(frame, showFuncName=False)), output)
#								
#								
#								self.disassemble_instructions(function.GetInstructions(target), target, rip)
#							
#							########################################################################
							
							module = frame.GetModule()
							for sec in module.section_iter():
								sectionNode = QTreeWidgetItem(self.treFile, [sec.GetName(), str(hex(sec.GetFileAddress())), str(hex(sec.GetFileAddress() + sec.GetByteSize())), hex(sec.GetFileByteSize()), hex(sec.GetByteSize()), lldbHelper.SectionTypeString(sec.GetSectionType()) + " (" + str(sec.GetSectionType()) + ")"])
								
								for idx3 in range(sec.GetNumSubSections()):
#									print(sec.GetSubSectionAtIndex(idx3).GetName())
									
									subSec = sec.GetSubSectionAtIndex(idx3)
									
									subSectionNode = QTreeWidgetItem(sectionNode, [subSec.GetName(), str(hex(subSec.GetFileAddress())), str(hex(subSec.GetFileAddress() + subSec.GetByteSize())), hex(subSec.GetFileByteSize()), hex(subSec.GetByteSize()), lldbHelper.SectionTypeString(subSec.GetSectionType()) + " (" + str(subSec.GetSectionType()) + ")"])
									
									for sym in module.symbol_in_section_iter(subSec):
										subSectionNode2 = QTreeWidgetItem(subSectionNode, [sym.GetName(), str(hex(sym.GetStartAddress().GetFileAddress())), str(hex(sym.GetEndAddress().GetFileAddress())), hex(sym.GetSize()), '', f'{lldbHelper.SymbolTypeString(sym.GetType())} ({sym.GetType()})'])
							
#							self.start_loadRegisterWorker()	
						
#						self.start_eventListenerWorker(self.debugger, self.interruptEventListenerWorker)
							context = frame.GetSymbolContext(lldb.eSymbolContextEverything)
							self.start_loadSourceWorker(self.debugger, "/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/LLDBPyGUI/testtarget/hello_world_test.c", self.interruptLoadSourceWorker, context.GetLineEntry().GetLine())
#						self.process.Continue()
				
#				self.reloadBreakpoints(True)
				
#				stdout_stream = self.process.GetSTDOUT()
#				stderr_stream = self.process.GetSTDERR()
#				while self.process.IsRunning():
#					data = stdout_stream.ReadBytes(1024)
#					if data:
#						print("STDOUT:", data.decode())
#					data = stderr_stream.ReadBytes(1024)
#					if data:
#						print("STDERR:", data.decode())
	
	
	def start_findReferencesWorker(self, address, initTable = True):
#		print(">>>> start_loadBreakpointsWorker")
#		self.symFuncName = ""
#		self.txtMultiline.table.resetContent()
		self.findReferencesWorker = FindReferencesWorker(self.driver, address, initTable)
		self.findReferencesWorker.signals.finished.connect(self.handle_findReferencesWorkerFinished)
		self.findReferencesWorker.signals.sendStatusBarUpdate.connect(self.handle_statusBarUpdate)
		self.findReferencesWorker.signals.sendProgressUpdate.connect(self.handle_progressUpdate)
		
		self.findReferencesWorker.signals.referenceFound.connect(self.handle_referenceFound)
##		self.loadBreakpointsWorker.signals.loadRegister.connect(self.handle_loadRegisterLoadRegister)
#		self.loadDisassemblyWorker.signals.loadBreakpointsValue.connect(self.handle_loadBreakpointsLoadBreakpointValue)
#		self.loadDisassemblyWorker.signals.updateBreakpointsValue.connect(self.handle_updateBreakpointsLoadBreakpointValue)
##		self.loadBreakpointsWorker.signals.updateRegisterValue.connect(self.handle_loadRegisterUpdateRegisterValue)
		
		self.threadpool.start(self.findReferencesWorker)
		
	def handle_referenceFound(self, address, instruction):
		print(f"REFERENCE TO ADDRESS '{address}' FOUND AT: {hex(int(str(instruction.GetAddress().GetFileAddress()), 10))}")
		pass
		
	def handle_findReferencesWorkerFinished(self):
		self.updateStatusBar("Search for references finished")
		pass
		
	def start_loadDisassemblyWorker(self, initTable = True):
#		print(">>>> start_loadBreakpointsWorker")
		self.symFuncName = ""
		self.txtMultiline.table.resetContent()
		self.loadDisassemblyWorker = LoadDisassemblyWorker(self.driver, initTable)
		self.loadDisassemblyWorker.signals.finished.connect(self.handle_loadDisassemblyWorkerFinished)
		self.loadDisassemblyWorker.signals.sendStatusBarUpdate.connect(self.handle_statusBarUpdate)
		self.loadDisassemblyWorker.signals.sendProgressUpdate.connect(self.handle_progressUpdate)
		
		self.loadDisassemblyWorker.signals.loadInstruction.connect(self.handle_loadInstruction)
##		self.loadBreakpointsWorker.signals.loadRegister.connect(self.handle_loadRegisterLoadRegister)
#		self.loadDisassemblyWorker.signals.loadBreakpointsValue.connect(self.handle_loadBreakpointsLoadBreakpointValue)
#		self.loadDisassemblyWorker.signals.updateBreakpointsValue.connect(self.handle_updateBreakpointsLoadBreakpointValue)
##		self.loadBreakpointsWorker.signals.updateRegisterValue.connect(self.handle_loadRegisterUpdateRegisterValue)
		
		self.threadpool.start(self.loadDisassemblyWorker)
		
	def handle_loadDisassemblyWorkerFinished(self):
		self.reloadBreakpoints(True)
#		print(f'self.rip => {self.rip}')
		QApplication.processEvents()
#		QCoreApplication.processEvents()
		self.txtMultiline.setInstsAndAddr(None, self.rip)
		self.txtMultiline.setPC(int(self.rip, 16))
		self.wdtBPsWPs.tblBPs.setPC(self.rip)
		self.loadStacktrace()
		self.start_loadRegisterWorker()	
#		self.loadTestBPs(ConfigClass.testBPsFilename)
		
	symFuncName = "" #== instruction.GetAddress().GetFunction().GetName()
	def handle_loadInstruction(self, instruction):
		target = self.driver.getTarget()
		
		if self.symFuncName != instruction.GetAddress().GetFunction().GetName():
			self.symFuncName = instruction.GetAddress().GetFunction().GetName()
			
			self.txtMultiline.appendAsmSymbol(str(instruction.GetAddress().GetFileAddress()), self.symFuncName)

#		print(f'instruction.GetComment(target) => {instruction.GetComment(target)}')
		self.txtMultiline.appendAsmText(hex(int(str(instruction.GetAddress().GetFileAddress()), 10)), instruction.GetMnemonic(target),  instruction.GetOperands(target), instruction.GetComment(target), str(instruction.GetData(target)).replace("                             ", "\t\t").replace("		            ", "\t\t\t").replace("		         ", "\t\t").replace("		      ", "\t\t").replace("			   ", "\t\t\t"), True, self.rip)
		pass
		
	def disassemble_instructions(self, insts, target, rip):
		idx = 0
		for i in insts:
			if idx == 0:
				self.txtMultiline.setInstsAndAddr(insts, hex(int(str(i.GetAddress().GetFileAddress()), 10)))
#				print(dir(i))
#			print(i)
			idx += 1
#			print(i.GetData(target))
			self.txtMultiline.appendAsmText(hex(int(str(i.GetAddress().GetFileAddress()), 10)), i.GetMnemonic(target),  i.GetOperands(target), i.GetComment(target), str(i.GetData(target)).replace("                             ", "\t\t").replace("		            ", "\t\t\t").replace("		         ", "\t\t").replace("		      ", "\t\t").replace("			   ", "\t\t\t"), True, rip)
			
			print(f'i.GetComment(target) => {i.GetComment(target)}')
			
	def handle_output(self, output):
		print(f">>>>>> OUTPUT: {output}")
		byte_array = bytearray.fromhex(output)
		string_value = byte_array.decode('utf-8')
		self.txtOutput.appendEscapedText(string_value, False)
		
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
					self.wdtBPsWPs.tblBPs.doBPOn(hex(bl.GetLoadAddress()), True)
					self.txtMultiline.table.setBPAtAddress(hex(bl.GetLoadAddress()), True, False)
				self.driver.handleCommand("br com a -F lldbpyGUI.breakpointHandlerNG")
				
		# eBroadcastBitSTDOUT
#		if event.GetType() == lldb.SBProcess.eBroadcastBitSTDOUT:
#			stdout = self.driver.getTarget().GetProcess().GetSTDOUT(256)
#			if stdout is not None and len(stdout) > 0:
#				message = {"status":"event", "type":"stdout", "output": "".join(["%02x" % ord(i) for i in stdout])}
#				print(message)
#				if event.GetDataFlavor() == "Process::ProcessEventData":
#					proc = SBProcess.GetProcessFromEvent(event)
#					if proc:
#						print(proc)
#					pass
#		if got_event and not event.IsValid():
##               self.winAddStr("Warning: Invalid or no event...")
#				continue
#		elif not event.GetBroadcaster().IsValid():
#				continue
		print("==============================================")
		pass
	
	def doReadMemory(self, address, size = 0x100):
		self.tabWidgetDbg.setCurrentWidget(self.tabMemory)
		self.tblHex.txtMemAddr.setText(hex(address))
		self.tblHex.txtMemSize.setText(hex(size))
		try:
#           global debugger
			print(f'INSIDE doReadMemory')
			self.handle_readMemory(self.driver.debugger, int(self.tblHex.txtMemAddr.text(), 16), int(self.tblHex.txtMemSize.text(), 16))
			print(f'AFTER doReadMemory')
		except Exception as e:
			print(f"Error while reading memory from process: {e}")
			
	def handle_readMemory(self, debugger, address, data_size = 0x100):
		print(f'INSIDE handle_readMemory')
		error_ref = lldb.SBError()
		process = debugger.GetSelectedTarget().GetProcess()
		memory = process.ReadMemory(address, data_size, error_ref)
		if error_ref.Success():
#           hex_string = binascii.hexlify(memory)
			# `memory` is a regular byte string
#           print(f'BYTES:\n{memory}\nHEX:\n{hex_string}')
			print(f'INSIDE tblHex.setTxtHex')
			self.tblHex.setTxtHex(memory, True, int(self.tblHex.txtMemAddr.text(), 16))
			print(f'AFTER tblHex.setTxtHex')
		else:
			print(str(error_ref))
			
	def click_restartTarget(self):
		target = self.driver.getTarget()
		launch_info = target.GetLaunchInfo()
#		target.Terminate()
		target.GetProcess().Kill()
		error = lldb.SBError()
		target.Launch(launch_info, error)

	def click_ReadMemory(self):
		try:
			self.handle_readMemory(self.driver.debugger, int(self.tblHex.txtMemAddr.text(), 16), int(self.tblHex.txtMemSize.text(), 16))
		except Exception as e:
			print(f"Error while reading memory from process: {e}")
			
#	0x3041130ad
		
	def click_saveBP(self):
		filename = showSaveFileDialog()
		if filename != None:
			print(f'Saving to: {filename} ...')
			self.bpHelper.handle_saveBreakpoints(self.driver.getTarget(), filename)
			self.updateStatusBar(f"Saving breakpoints to {filename} ...")
#			self.driver.handleCommand(f"breakpoint write -f {filename}")
			
	def loadTestBPs(self, filename):
		if filename != None:
			print(f'Loading Breakpoints from: {filename} ...')
			self.updateStatusBar(f"Loading Breakpoints from {filename} ...")
			self.driver.handleCommand(f"breakpoint read -f {filename}")
		pass
		
	def click_loadBP(self):
		filename = showOpenBPFileDialog()
		if filename != None:
			print(f'Loading Breakpoints from: {filename} ...')
			self.updateStatusBar(f"Loading Breakpoints from {filename} ...")
			self.driver.handleCommand(f"breakpoint read -f {filename}")
			
#		self.updateStatusBar("Loading breakpoints ...")
		pass
	
	def click_reloadBP(self):
		self.reloadBreakpoints(True)
		self.updateStatusBar("All Breakpoints reloaded!")
	
	def click_deleteAllBP(self):
		if showQuestionDialog(self, "Delete all Breakpoints?", "Do you really want to delete all Breakpoints?"):
			self.bpHelper.handle_deleteAllBPs()
			self.txtMultiline.table.handle_deleteAllBPs()
			self.wdtBPsWPs.tblBPs.resetContent()
			self.updateStatusBar("All Breakpoints deleted!")
		
	def click_exit_action(self):
		self.close()
		pass
		
	def reloadBreakpoints(self, initTable = True):
		self.updateStatusBar("Reloading breakpoints ...")
#		if initTable: # TODO: Implement Update instead of complete refresh
		if initTable:
			self.wdtBPsWPs.tblBPs.resetContent()
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
		self.progressbar.setValue(int(newValue))
		pass
		
	def updateStatusBar(self, msg):
		self.statusBar.showMessage(msg)
		
	def clear_clicked(self):
		self.txtCommands.setText("")
	
	def start_loadBreakpointsWorker(self, initTable = True):
#		print(">>>> start_loadBreakpointsWorker")
		self.loadBreakpointsWorker = LoadBreakpointsWorker(self.driver, initTable)
		self.loadBreakpointsWorker.signals.finished.connect(self.handle_loadBreakpointsFinished)
		self.loadBreakpointsWorker.signals.sendStatusBarUpdate.connect(self.handle_statusBarUpdate)
		self.loadBreakpointsWorker.signals.sendProgressUpdate.connect(self.handle_progressUpdate)
		
#		self.loadBreakpointsWorker.signals.loadRegister.connect(self.handle_loadRegisterLoadRegister)
		self.loadBreakpointsWorker.signals.loadBreakpointsValue.connect(self.handle_loadBreakpointsLoadBreakpointValue)
		self.loadBreakpointsWorker.signals.updateBreakpointsValue.connect(self.handle_updateBreakpointsLoadBreakpointValue)
		self.loadBreakpointsWorker.signals.loadWatchpointsValue.connect(self.handle_loadWatchpointsLoadBreakpointValue)
		self.loadBreakpointsWorker.signals.updateWatchpointsValue.connect(self.handle_updateWatchpointsLoadBreakpointValue)
#		self.loadBreakpointsWorker.signals.updateRegisterValue.connect(self.handle_loadRegisterUpdateRegisterValue)
		
		self.threadpool.start(self.loadBreakpointsWorker)
		
	
	wpsEnabled = {}
	
	def handle_loadWatchpointsLoadBreakpointValue(self, wp):
#		if initTable:
#			self.txtMultiline.table.setBPAtAddress(loadAddr, True, False)
		self.wpsEnabled[wp.GetID()] = wp.IsEnabled()
		self.wdtBPsWPs.tblWPs.addRow(wp.IsEnabled(), wp.GetID(), hex(wp.GetWatchAddress()), hex(wp.GetWatchSize()), wp.GetWatchSpec(), ("r" if wp.IsWatchingReads() else "") + ("" if wp.IsWatchingReads() and wp.IsWatchingWrites() else "") + ("w" if wp.IsWatchingWrites() else ""), wp.GetHitCount(), wp.GetIgnoreCount(), wp.GetCondition())
	
	def handle_updateWatchpointsLoadBreakpointValue(self, wp):
		print(f'wp.GetWatchValueKind() =====================>>>>>>>>>>>>>> {wp.GetWatchValueKind()} / {lldb.eWatchPointValueKindExpression}')
		
		newEnabled = wp.IsEnabled()
		if wp.GetID() in self.wpsEnabled.keys():
			if self.wpsEnabled[wp.GetID()] != newEnabled:
				newEnabled = not newEnabled
				wp.SetEnabled(newEnabled)
		else:
			self.wpsEnabled[wp.GetID()] = newEnabled
			wp.SetEnabled(newEnabled)
			
		self.wdtBPsWPs.tblWPs.updateRow(newEnabled, wp.GetID(), hex(wp.GetWatchAddress()), hex(wp.GetWatchSize()), wp.GetWatchSpec(), ("r" if wp.IsWatchingReads() else "") + ("" if wp.IsWatchingReads() and wp.IsWatchingWrites() else "") + ("w" if wp.IsWatchingWrites() else ""), wp.GetHitCount(), wp.GetIgnoreCount(), wp.GetCondition())
		
	def handle_loadBreakpointsLoadBreakpointValue(self, bpId, idx, loadAddr, name, hitCount, condition, initTable, enabled, bp):
		if initTable:
			self.txtMultiline.table.setBPAtAddress(loadAddr, True, False)
		self.wdtBPsWPs.tblBPs.addRow(enabled, idx, loadAddr, name, str(hitCount), condition)
#		bp.SetScriptCallbackBody("print('HELLLLLLLLLLLLLLOOOOOOOOO SSSSCCCCRRRRIIIIIPPPTTTTT CALLBACK!!!!!')")
		extra_args = lldb.SBStructuredData()
		# Add any extra data you want to pass to the callback (e.g., variables, settings)
		self.driver.handleCommand("command script import --allow-reload ./lldbpyGUIWindow.py")
		bp.SetScriptCallbackFunction("lldbpyGUIWindow.my_callback", extra_args)
		
#		self.driver.handleCommand("command script import --allow-reload ./lldbpyGUI.py")
#		bp.SetScriptCallbackFunction("lldbpyGUI.my_callback", extra_args)
		
#		print("Reloading BPs ...")
	
	def handle_updateBreakpointsLoadBreakpointValue(self, bpId, idx, loadAddr, name, hitCount, condition, initTable, enabled, bp):
#		if initTable:
#			self.txtMultiline.table.setBPAtAddress(loadAddr, True, False)
		self.wdtBPsWPs.tblBPs.updateRow(enabled, idx, loadAddr, name, str(hitCount), condition)
		extra_args = lldb.SBStructuredData()
		self.driver.handleCommand("command script import --allow-reload ./lldbpyGUIWindow.py")
		bp.SetScriptCallbackFunction("lldbpyGUIWindow.my_callback", extra_args)
#		self.driver.handleCommand("command script import --allow-reload ./lldbpyGUI.py")
#		bp.SetScriptCallbackFunction("lldbpyGUI.my_callback", extra_args)
#		print("Reloading BPs ...")
		
	def handle_loadBreakpointsFinished(self):
#		print("handle_loadBreakpointsFinished")
#		self.tblBPs.setCurrentBPHit(str(self.rip))
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
		self.updateStatusBar("handle_loadRegisterFinished")
		
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
			
	def handle_loadRegisterLoadVariableValue(self, name, value, data, valType, address):
		self.tblVariables.addRow(name, value, valType, address, data)
		
	def handle_loadRegisterUpdateVariableValue(self, name, value, data, valType, address):
		self.tblVariables.updateRow(name, value, valType, address, data)
		
	def click_help(self):
		self.updateStatusBar("Help for LLDBPyGUI opening ...")
		helpWindow = HelpDialog()
		helpWindow.exec()
		pass
		
	def handle_execCommand(self):
		self.do_execCommand(True)
		
#	def click_execCommand(self):
#		self.do_execCommand(True)
		
	def do_execCommand(self, addCmd2Hist = False):
		if self.setHelper.getValue(SettingsValues.CmdHistory):
			self.txtCmd.addCommandToHistory()
			
		self.txtCommands.append(f"({PROMPT_TEXT}) {self.txtCmd.text().strip()}")
		if self.txtCmd.text().strip().lower() in ["clear", "clr"]:
			self.clear_clicked()
		else:
			self.start_execCommandWorker(self.txtCmd.text())
		
	def start_execCommandWorker(self, command):
		workerExecCommand = ExecCommandWorker(self.debugger, command)
		workerExecCommand.signals.finished.connect(self.handle_commandFinished)
		
		self.threadpool.start(workerExecCommand)
		
	def handle_commandFinished(self, res):
		if res.Succeeded():
			self.txtCommands.appendEscapedText(res.GetOutput())
		else:
			self.txtCommands.appendEscapedText(f"{res.GetError()}")
			
		if self.swtAutoscroll.isChecked():
			self.sb = self.txtCommands.verticalScrollBar()
			self.sb.setValue(self.sb.maximum())
	
	def settings_clicked(self, s):
		print("Opening Settings ...")
		self.updateStatusBar("Opening Settings ...")
		
#		project_root = dirname(realpath(__file__))
#		helpDialogPath = os.path.join(project_root, 'resources', 'designer', 'helpDialog.ui')
#		
#		window = uic.loadUi(helpDialogPath)
		settingsWindow = SettingsDialog(self.setHelper)
		if settingsWindow.exec():
			print(f'Settings saved')
			self.txtCmd.doAddCmdToHist = self.setHelper.getValue(SettingsValues.CmdHistory)
		
#		dialog = QFileDialog(None, "Select executable or library", "", "All Files (*.*)")
#		dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
#		dialog.setNameFilter("Executables (*.exe *.com *.bat *);;Libraries (*.dll *.so *.dylib)")
#		
#		if dialog.exec():
#			filename = dialog.selectedFiles()[0]
#			print(filename)
##			self.start_workerLoadTarget(filename)
#		else:
#			return None
		
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
		
		self.tblFileInfos.addRow("----", str("-----"), '-----')
		self.tblFileInfos.addRow("Triple", str(self.driver.getTarget().GetTriple()), '-')
		
#		print(f'target.GetTriple() => {target.GetTriple()}')
			
	def loadFileStats(self, target):
		statistics = target.GetStatistics()
		stream = lldb.SBStream()
		success = statistics.GetAsJSON(stream)
		if success:
#			self.signals.loadStats.emit(str(stream.GetData()))
			self.treStats.loadJSON(str(stream.GetData()))
		
	def start_eventListenerWorker(self, debugger, event_listener):
		workerEventListener = EventListenerWorker(debugger, event_listener)
#		workerEventListe	ner.signals.finished.connect(self.handle_commandFinished)
		
		self.threadpool.start(workerEventListener)
		
	def start_loadSourceWorker(self, debugger, sourceFile, event_listener, lineNum = 1):
		self.workerLoadSource = LoadSourceCodeWorker(debugger, sourceFile, event_listener, lineNum)
		self.workerLoadSource.signals.finished.connect(self.handle_loadSourceFinished)
		
		self.threadpool.start(self.workerLoadSource)
	
	def handle_enableBPTblBPs(self, address, enabled):
		self.txtMultiline.table.doEnableBP(address, enabled)
		if self.bpHelper.handle_checkBPExists(address) != None:
			self.bpHelper.handle_enableBP(address, enabled)
			if enabled:
				self.driver.handleCommand("br com a -F lldbpyGUI.breakpointHandlerNG")
	
	def handle_enableBP(self, address, enabled):
		self.wdtBPsWPs.tblBPs.doEnableBP(address, enabled)
		if self.bpHelper.handle_checkBPExists(address) != None:
			self.bpHelper.handle_enableBP(address, enabled)
			if enabled:
				self.driver.handleCommand("br com a -F lldbpyGUI.breakpointHandlerNG")
	
	def handle_BPOn(self, address, on):
		self.wdtBPsWPs.tblBPs.doBPOn(address, on)
#		print(f"breakpoint set -a {address} -C bpcbdriver")
		res = lldb.SBCommandReturnObject()
		ci = self.driver.debugger.GetCommandInterpreter()
		if on:
			#			self.driver.handleCommand(f"breakpoint set -a {address} -C bpcb")
			
			ci.HandleCommand(f"breakpoint set -a {address} -C bpcb", res)
		else:
			ci.HandleCommand(f"breakpoint set -a {address} -C bpcb", res)
		self.bpHelper.handle_enableBP(address, on)
		pass
		
	def handle_resumeThread(self):
#		print("Trying to Continue ...")
#		error = self.process.Continue()
		self.start_debugWorker(self.driver, StepKind.Continue)
		self.load_resume.setIcon(ConfigClass.iconPause)
#		print("After Continue ...")
#		if error:
#			print(error)
			
	def handle_stopThread(self):
		print("Trying to SIGINT ...")
		error = self.process.Stop()
		print("After SIGINT ...")
		if error:
			print(error)
	
	workerDebug = None
	def start_debugWorker(self, driver, kind):
		if self.workerDebug == None or not self.workerDebug.isRunning:
			self.setResumeActionIcon(ConfigClass.iconPause)
			self.workerDebug = DebugWorker(driver, kind)
			self.workerDebug.signals.debugStepCompleted.connect(self.handle_debugStepCompleted)
			self.workerDebug.signals.setPC.connect(self.handle_debugSetPC)
			
			self.threadpool.start(self.workerDebug)
		
	def handle_debugSetPC(self, newPC):
		self.wdtBPsWPs.tblBPs.setPC(newPC)
		pass
		
	def handle_debugStepCompleted(self, kind, success, rip, frm):
		if success:
#			print(f"Debug STEP ({kind}) completed SUCCESSFULLY")
			self.txtMultiline.setPC(int(str(rip), 16))
			
#			print(f'NEXT INSTRUCTION {rip}')
#			self.txtMultiline.setPC(frame.GetPC())
			self.reloadRegister(False)
			self.reloadBreakpoints(False)
			self.wdtBPsWPs.tblBPs.setPC(rip)
#			print(f'GOT if thread.GetStopReason() == lldb.eStopReasonBreakpoint:')
			self.loadStacktrace()
#			frame = thread.GetFrameAtIndex(0)
			
#			QCoreApplication.processEvents()
			
#			self.driver.getTarget()
			context = frm.GetSymbolContext(lldb.eSymbolContextEverything)
#			print(f'.GetLineEntry() => {context.GetLineEntry()} => {context.GetLineEntry().GetLine()}')
			self.start_loadSourceWorker(self.debugger, "/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/LLDBPyGUI/testtarget/hello_world_test.c", self.interruptLoadSourceWorker, context.GetLineEntry().GetLine())
			self.setResumeActionIcon(ConfigClass.iconResume)
		else:
			print(f"Debug STEP ({kind}) FAILED!!!")
		pass
		
	def loadStacktrace(self):
		self.process = self.driver.getTarget().GetProcess()
		self.thread = self.process.GetThreadAtIndex(0)
#		from lldbutil import print_stacktrace
#		st = get_stacktrace(self.thread)
##			print(f'{st}')
#		self.txtOutput.setText(st)
		
		idx = 0
		if self.thread:
			
			self.treThreads.clear()
			self.processNode = QTreeWidgetItem(self.treThreads, ["#0 " + str(self.process.GetProcessID()), hex(self.process.GetProcessID()) + "", self.process.GetTarget().GetExecutable().GetFilename(), '', ''])
			
			self.threadNode = QTreeWidgetItem(self.processNode, ["#" + str(idx) + " " + str(self.thread.GetThreadID()), hex(self.thread.GetThreadID()) + "", self.thread.GetQueueName(), '', ''])
			
			numFrames = self.thread.GetNumFrames()
			
			for idx2 in range(numFrames):
				self.setProgressValue(idx2 / numFrames)
				frame = self.thread.GetFrameAtIndex(idx2)
				frameNode = QTreeWidgetItem(self.threadNode, ["#" + str(frame.GetFrameID()), "", str(frame.GetPCAddress()), str(hex(frame.GetPC())), lldbHelper.GuessLanguage(frame)])
				idx += 1
				
			self.processNode.setExpanded(True)
			self.threadNode.setExpanded(True)
	
	def stepOver_clicked(self):
#		print("Trying to step OVER ...")
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
##		print("Trying to step INTO ...")
##		self.driver.debugger.SetAsync(False)
#		self.thread.StepInto()
##		self.driver.debugger.SetAsync(True)
#		
#		frame = self.thread.GetFrameAtIndex(0)
#		print(f'NEXT INSTRUCTION {hex(frame.GetPC())}')
#		self.txtMultiline.setPC(frame.GetPC())
#		self.reloadRegister(False)
#		self.reloadBreakpoints(False)
		self.start_debugWorker(self.driver, StepKind.StepInto)
		
	def stepOut_clicked(self):
##		print("Trying to step OUT ...")
##		self.driver.debugger.SetAsync(False)
#		self.thread.StepOut()
##		self.driver.debugger.SetAsync(True)
#		
#		frame = self.thread.GetFrameAtIndex(0)
#		print(f'NEXT INSTRUCTION {hex(frame.GetPC())}')
#		self.txtMultiline.setPC(frame.GetPC())
#		self.reloadRegister(False)
#		self.reloadBreakpoints(False)
		self.start_debugWorker(self.driver, StepKind.StepOut)
		
	def handle_loadSourceFinished(self, sourceCode, autoScroll = True):
		if sourceCode != "":
			horizontal_value = self.txtSource.horizontalScrollBar().value()
			
			if not autoScroll:
				vertical_value = self.txtSource.verticalScrollBar().value()
			
			self.txtSource.setEscapedText(sourceCode)
			
#			self.tabWidgetDbg
			currTabIdx = self.tabWidgetDbg.currentIndex()
			self.tabWidgetDbg.setCurrentIndex(2)
			self.txtSource.horizontalScrollBar().setValue(horizontal_value)
			if not autoScroll:
				self.txtSource.verticalScrollBar().setValue(vertical_value)
			else:
				line_text = "=>"
				self.scroll_to_line(self.txtSource, line_text)
				self.tabWidgetDbg.setCurrentIndex(currTabIdx)
		else:
			self.txtSource.setText("<Source code NOT available>")
		
	def getNextNBSpace(self, text, start_pos):
		decoded_text = text.encode('utf-8').decode('utf-8')  # Encode and decode to handle the byte sequence
		position = decoded_text.find('\xa0', start_pos)  # Search for the nearby text
		return position
		
	def scroll_to_line(self, text_edit, line_text):
		search_string = "=&gt;"
		
		text = text_edit.document().findBlockByNumber(0).text()
		position = text.find(line_text)
#		print(f'position => {position}')
		start_pos = position + 3
		
		end_pos = self.getNextNBSpace(text, start_pos)
		if text[start_pos:end_pos] == '':
			return
		
		linePos = int(text[start_pos:end_pos])

		scroll_value = linePos * self.txtSource.fontMetrics().height()
#		print(f'scroll_value => {scroll_value}')
		scroll_value -= self.txtSource.viewport().height() / 2  # Center vertically
#		print(f'self.txtSource.viewport().height() / 2 => {self.txtSource.viewport().height() / 2}')
		self.txtSource.verticalScrollBar().setValue(int(scroll_value))
#		print(f'scroll_value => {scroll_value}')
	
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