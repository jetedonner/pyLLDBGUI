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

from worker.breakpointWorker import *

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

#def worker():
#	while True:
#		global event_queueBP
#		item = event_queueBP.get()
#		print(f'Working on {item}')
##		print(f'Finished {item}')
#		event_queueBP.task_done()
#		
#		# Turn-on the worker thread.
#threading.Thread(target=worker, daemon=True).start()
#
#global my_target
#def myTest():
#	print("MYTEST")
	
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
		
#		self.event_queueBP.put(event)
	
#	global my_window
#	my_window.my_callbackWindow(frame, bp_loc, dict)

global my_window
my_window = None

class LLDBPyGUIWindow(QMainWindow):
	"""PyMobiledevice3GUI's main window (GUI or view)."""
	
#	regTreeList = []
#	global my_target
#	my_target = myTest
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
		self.driver.createTarget(ConfigClass.testTarget)
		if self.driver.debugger.GetNumTargets() > 0:
			target = self.driver.getTarget()
			
			fname = "main"
			main_bp = target.BreakpointCreateByName(fname, target.GetExecutable().GetFilename())
			main_bp.AddName(fname)
			#			print(main_bp)
			
#			start_bp = target.BreakpointCreateByAddress(0x100003f0a) # 0x100003f85) # 0x100003c90) 
#			start_bp.SetEnabled(True)
#			start_bp.AddName("start_bp")
			
			##     start_bp.SetScriptCallbackFunction("lldbpyGUI.breakpointHandler")
			##     start_bp.SetCondition("$eax == 0x00000000")
			##     start_bp.SetScriptCallbackFunction("disasm_ui.breakpointHandler")
			
			
			self.click_restartTarget()
#			return
#			process = target.LaunchSimple(None, None, os.getcwd())
			
#			error = lldb.SBError()
#			main_wp = target.WatchAddress(int("0x304113084", 16), 0x1, False, True, error)
#			print(error)
#			print(main_wp)
#			
			self.loadTarget()
#			start_bp = target.BreakpointCreateByAddress(0x100003f0a) # 0x100003f85) # 0x100003c90) 
#			start_bp.SetEnabled(True)
#			start_bp.AddName("start_bp")
#			print(start_bp)
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
		
#		self.setWindowTitle(APP_NAME + " " + APP_VERSION)
		self.setWinTitleWithState("GUI Started")
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
		
		self.attach_action = QAction(ConfigClass.iconGears, '&Attach Process', self)
		self.attach_action.setStatusTip('Attach Process')
		self.attach_action.setShortcut('Ctrl+A')
		self.attach_action.triggered.connect(self.attach_clicked)
		self.toolbar.addAction(self.attach_action)
		
		
		
		self.settings_action = QAction(ConfigClass.iconSettings, 'Settings', self)
		self.settings_action.setStatusTip('Settings')
		self.settings_action.setShortcut('Ctrl+O')
		self.settings_action.triggered.connect(self.settings_clicked)
#		self.toolbar.addAction(self.settings_action)
#		self.toolbar.addAction(self.settings_action)
		
		self.help_action = QAction(ConfigClass.iconInfo, '&Show Help', self)
		self.help_action.setStatusTip('Show Help')
		self.help_action.setShortcut('Ctrl+H')
		self.help_action.triggered.connect(self.click_help)
		
		menu = self.menuBar()
		
		main_menu = menu.addMenu("Main")
		main_menu.addAction(self.settings_action)
		
		file_menu = menu.addMenu("&Load Action")
		file_menu.addAction(self.load_action)
#		file_menu.addAction(self.settings_action)
		
#		self.help_action = QAction(ConfigClass.iconInfo, '&Show Help', self)
#		self.help_action.setStatusTip('Show Help')
#		self.help_action.setShortcut('Ctrl+H')
#		self.help_action.triggered.connect(self.click_help)
		
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
		
		self.back = QAction(ConfigClass.iconLeft, '&Back', self)
		self.back.setStatusTip('Back')
#		self.load_resume.setShortcut('Ctrl+L')
		self.back.triggered.connect(self.handle_back)
		self.toolbar.addAction(self.back)
		
		self.forward = QAction(ConfigClass.iconRight, '&Forward', self)
		self.forward.setStatusTip('Back')
#		self.load_resume.setShortcut('Ctrl+L')
		self.forward.triggered.connect(self.handle_forward)
		self.forward.setEnabled(False)
		self.toolbar.addAction(self.forward)
		
		
		self.toolbar.addAction(self.settings_action)
		self.toolbar.addAction(self.help_action)
		
		self.reset = QAction(ConfigClass.iconRight, '&Reset', self)
		self.reset.setStatusTip('Reset')
#		self.load_resume.setShortcut('Ctrl+L')
		self.reset.triggered.connect(self.handle_reset)
#		self.reset.setEnabled(False)
		self.toolbar.addAction(self.reset)
		
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
		self.wgtStatusbarRight.layout().addWidget(self.cmdHelp)
		self.statusBar.addPermanentWidget(self.wgtStatusbarRight)
		
		self.layout = QVBoxLayout()
		
		self.txtMultiline = AssemblerTextEdit(self.driver)
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
		self.splitter.setStretchFactor(0, 90)
		self.splitter.setStretchFactor(1, 10)
		
		self.tabWidgetReg = QTabWidget()
		self.tabWidgetReg.setContentsMargins(0, 0, 0, 0)
		self.tabWidgetDbg.addTab(self.tabWidgetReg, "Register")
		
		self.tblVariables = VariablesTableWidget()
		self.gbpVariables = QGroupBox("Variables")
		self.gbpVariables.setLayout(QHBoxLayout())
		self.gbpVariables.layout().addWidget(self.tblVariables)
		
		self.tabWidgetDbg.addTab(self.gbpVariables, "Variables")
		
		self.txtSource = QConsoleTextEdit()
		self.txtSource.setReadOnly(True)
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
		self.treThreads.doubleClicked.connect(self.treThreads_doubleClicked)
		
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
		
#		self.txtOutput = QConsoleTextEdit()
#		self.txtOutput.setFont(ConfigClass.font)
#		self.txtOutput.setReadOnly(True)
#		self.tabWidgetDbg.addTab(self.txtOutput, "Stacktrace")
		
		self.tabWidgetMain = QTabWidget()
		self.tabWidgetMain.addTab(self.splitter, "Debugger")
		
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
		self.txtCommands.setText("Here you can run LLDB commands. Type 'help' for a list of available commands.\n")
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
		
		self.tabWidgetDbg.setCurrentIndex(ConfigClass.currentDebuggerSubTab)
	
	def attach_clicked(self):
		print(f"Attaching to process ...")
		pd = ProcessesDialog("Select process", "Select a process to attach to.")
		if pd.exec():
			print(f"Process Idx: '{pd.cmbPID.currentIndex()}' / PID: '{pd.getSelectedProcess().pid}' / Name: '{pd.getSelectedProcess().name()}' selected")
			pass
			
#		import psutil
#		
#		# Get list of all processes
#		processes = list(psutil.process_iter())
#		
#		# Extract PID and name for each process
#		process_info = []
#		for process in processes:
#			try:
#				process_info.append((process.pid, process.name()))
#			except (psutil.NoSuchProcess, psutil.AccessDenied):
#				# Handle potential errors (process might disappear or insufficient permissions)
#				pass
#				
#		print(process_info)
#		pass
		
	def handle_back(self):
		print(f"GOING BACK ... {self.txtMultiline.locationStack.currentLocation}")
#		self.forward.setEnabled(True)
		newLoc = self.txtMultiline.locationStack.backLocation()
		if newLoc:
			print(f"GOING BACK to {newLoc} ... {self.txtMultiline.locationStack.currentLocation}")
			self.txtMultiline.viewAddress(newLoc, False)
		self.forward.setEnabled(not self.txtMultiline.locationStack.currentIsLast())
		self.back.setEnabled(not self.txtMultiline.locationStack.currentIsFirst())
		
	def handle_forward(self):
		print(f"GOING FORWARD ... {self.txtMultiline.locationStack.currentLocation}")
		newLoc = self.txtMultiline.locationStack.forwardLocation()
		if newLoc:
			print(f"GOING FORWARD to {newLoc} ... {self.txtMultiline.locationStack.currentLocation}")
			self.txtMultiline.viewAddress(newLoc, False)
#			self.back.setEnabled(True)
		self.forward.setEnabled(not self.txtMultiline.locationStack.currentIsLast())
		self.back.setEnabled(not self.txtMultiline.locationStack.currentIsFirst())
		
	def treThreads_doubleClicked(self, event):
		print(f"treThreads_doubleClicked")
		print(dir(event))
		self.txtMultiline.viewAddress(self.treThreads.currentItem().text(3))
		
	def my_callback(self, frame, bp_loc, dict):
		# Your code to execute when the breakpoint hits
		print("Breakpoint hit!!!!!!!! =========>>>>>>>>  YEESSSS!!!!!!")
		# Access the frame, breakpoint location, and any extra arguments passed to the callback
		
		
	def handle_reset(self):
		print(f"Resetting GUI")
		self.updateStatusBar(f"Resetting GUI ...")
		self.txtMultiline.resetContent()
		self.tblFileInfos.resetContent()
		self.treFile.clear()
		self.treStats.clear()
#		self.tblReg.resetContent()
		for tbl in self.tblRegs:
			tbl.resetContent()
		self.tblRegs.clear()
		self.tabWidgetReg.clear()
		self.tblVariables.resetContent()
		self.wdtBPsWPs.treBPs.clear()
		self.wdtBPsWPs.tblWPs.resetContent()
		self.txtSource.setText("")
		self.treThreads.clear()
		self.wdtSearch.resetContent()
		self.tblHex.resetContent()
#		self.wdtBPsWPs.treWPs.clear()
		
	def handle_processEvent(self, event):
#		if SBProcess.EventIsProcessEvent(event):
#			process = SBProcess.GetProcessFromEvent(event)
#		else:
#			process = event
#		print(f'Process-EVENT: {event} => {process}')
#		state = 'stopped'
#		if process.state == eStateStepping or process.state == eStateRunning:
#			state = 'running'
#		elif process.state == eStateExited:
#			state = 'exited'
#			self.should_quit = True
#		thread = process.selected_thread
#		print('Process event: %s, reason: %d' % (state, thread.GetStopReason()))
#		if thread.GetStopReason() == lldb.eStopReasonBreakpoint:
#			print(f'REASON BP RFEACHED (listener) Event: {process} => Continuing...')
#			print(f"thread.GetFrameAtIndex(0).GetPC() => {thread.GetFrameAtIndex(0).GetPC()}")
#			self.txtMultiline.locationStack.pushLocation(hex(thread.GetFrameAtIndex(0).GetPC()))
		pass
		
	def handle_stdoutEvent(self, data):
		print(f'EVENT: {data}')
		pass
		
	def handle_breakpointEvent(self, event):
		breakpoint = SBBreakpoint.GetBreakpointFromEvent(event)
		bpEventType = SBBreakpoint.GetBreakpointEventTypeFromEvent(event)
		
		print(f'GOT BREAKPOINT EVENT NG: {breakpoint} => TYPE: {bpEventType}')
		
		if bpEventType == lldb.eBreakpointEventTypeAdded:
			print(f"BP ID: {breakpoint.GetID()} has been ADDED !!!!!!!!!!!!!!")
			self.event_bpAdded(breakpoint)
			pass
		elif bpEventType == lldb.eBreakpointEventTypeRemoved:
			print(f"BP ID: {breakpoint.GetID()} has been DELETED !!!!!!!!!!!!!!")
			
			for i in range(breakpoint.GetNumLocations()):
				self.txtMultiline.table.removeBPAtAddress(hex(breakpoint.GetLocationAtIndex(i).GetLoadAddress()))
				pass
			pass
		elif bpEventType == lldb.eBreakpointEventTypeDisabled:
			pass
		elif bpEventType == lldb.eBreakpointEventTypeEnabled:
			pass
		elif bpEventType == lldb.eBreakpointEventTypeConditionChanged:
			print(f"bpEventType == lldb.eBreakpointEventTypeConditionChanged: {breakpoint}")
			pass
		
	def event_bpAdded(self, bp):
		print(f'bp.GetID() => {bp.GetID()}')
		self.handle_loadBreakpointsLoadBreakpointValue(bp, False)
		for i in range(bp.GetNumLocations()):
			bl = bp.GetLocationAtIndex(i)
			self.txtMultiline.table.event_bpAdded(bl)
#			self.wdtBPsWPs.tblBPs.event_bpAdded(bl)
			self.wdtBPsWPs.treBPs.setPC(hex(bl.GetLoadAddress()), False)
			
		
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
					self.listener.processEvent.connect(self.handle_processEvent)
					self.listener.stdoutEvent.connect(self.handle_stdoutEvent)
					self.listener.addListenerCalls()
					self.listener.start()
					
					idx = 0
					self.thread = self.process.GetThreadAtIndex(0)
					if self.thread:
						
						frame = self.thread.GetFrameAtIndex(0)
						if frame:
							print(frame)
							rip = lldbHelper.convert_address(frame.register["rip"].value)
							self.rip = rip
							self.start_loadDisassemblyWorker(True)
							
							module = frame.GetModule()
							for sec in module.section_iter():
								sectionNode = QTreeWidgetItem(self.treFile, [sec.GetName(), str(hex(sec.GetFileAddress())), str(hex(sec.GetFileAddress() + sec.GetByteSize())), hex(sec.GetFileByteSize()), hex(sec.GetByteSize()), lldbHelper.SectionTypeString(sec.GetSectionType()) + " (" + str(sec.GetSectionType()) + ")"])
								
								for idx3 in range(sec.GetNumSubSections()):
#									print(sec.GetSubSectionAtIndex(idx3).GetName())
									
									subSec = sec.GetSubSectionAtIndex(idx3)
									print(subSec)
									for idx4 in range(subSec.GetNumSubSections()):
										subSubSec = sec.GetSubSectionAtIndex(idx4)
										print(subSubSec)
										
									subSectionNode = QTreeWidgetItem(sectionNode, [subSec.GetName(), str(hex(subSec.GetFileAddress())), str(hex(subSec.GetFileAddress() + subSec.GetByteSize())), hex(subSec.GetFileByteSize()), hex(subSec.GetByteSize()), lldbHelper.SectionTypeString(subSec.GetSectionType()) + " (" + str(subSec.GetSectionType()) + ")"])
									
									for sym in module.symbol_in_section_iter(subSec):
										subSectionNode2 = QTreeWidgetItem(subSectionNode, [sym.GetName(), str(hex(sym.GetStartAddress().GetFileAddress())), str(hex(sym.GetEndAddress().GetFileAddress())), hex(sym.GetSize()), '', f'{lldbHelper.SymbolTypeString(sym.GetType())} ({sym.GetType()})'])
							
							context = frame.GetSymbolContext(lldb.eSymbolContextEverything)
							self.start_loadSourceWorker(self.debugger, ConfigClass.testTargetSource, self.interruptLoadSourceWorker, context.GetLineEntry().GetLine())
						
						self.start_breakpointWorker()
	
	
	
	
	
	def start_breakpointWorker(self):
		print(">>>> start_breakpointWorker")
#		self.symFuncName = ""
#		self.txtMultiline.table.resetContent()
		global event_queueBP
		self.breakpointWorker = BreakpointWorker(self.driver, event_queueBP)
#		self.findReferencesWorker.signals.finished.connect(self.handle_breakpointWorkerFinished)
		self.breakpointWorker.signals.sendStatusBarUpdate.connect(self.handle_statusBarUpdate)
		self.breakpointWorker.signals.sendProgressUpdate.connect(self.handle_progressUpdate)
		
		self.breakpointWorker.signals.gotEvent.connect(self.handle_gotEvent)
		
		self.threadpool.start(self.breakpointWorker)
		
	def handle_gotEvent(self, event):
		print(f"handle_gotEvent => {event}")
		pass
		
	def start_findReferencesWorker(self, address, initTable = True):
#		print(">>>> start_loadBreakpointsWorker")
#		self.symFuncName = ""
#		self.txtMultiline.table.resetContent()
		self.findReferencesWorker = FindReferencesWorker(self.driver, address, initTable)
		self.findReferencesWorker.signals.finished.connect(self.handle_findReferencesWorkerFinished)
		self.findReferencesWorker.signals.sendStatusBarUpdate.connect(self.handle_statusBarUpdate)
		self.findReferencesWorker.signals.sendProgressUpdate.connect(self.handle_progressUpdate)
		
		self.findReferencesWorker.signals.referenceFound.connect(self.handle_referenceFound)
		
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
		
		self.threadpool.start(self.loadDisassemblyWorker)
		
	def handle_loadDisassemblyWorkerFinished(self):
		self.reloadBreakpoints(True)
#		print(f'self.rip => {self.rip}')
		QApplication.processEvents()
#		QCoreApplication.processEvents()
		self.txtMultiline.setInstsAndAddr(None, self.rip)
		self.txtMultiline.setPC(int(self.rip, 16))
		self.wdtBPsWPs.tblBPs.setPC(self.rip)
		self.wdtBPsWPs.treBPs.setPC(self.rip)
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
		
#	def disassemble_instructions(self, insts, target, rip):
#		idx = 0
#		for i in insts:
#			if idx == 0:
#				self.txtMultiline.setInstsAndAddr(insts, hex(int(str(i.GetAddress().GetFileAddress()), 10)))
##				print(dir(i))
##			print(i)
#			idx += 1
##			print(i.GetData(target))
#			self.txtMultiline.appendAsmText(hex(int(str(i.GetAddress().GetFileAddress()), 10)), i.GetMnemonic(target),  i.GetOperands(target), i.GetComment(target), str(i.GetData(target)).replace("                             ", "\t\t").replace("		            ", "\t\t\t").replace("		         ", "\t\t").replace("		      ", "\t\t").replace("			   ", "\t\t\t"), True, rip)
#			
#			print(f'i.GetComment(target) => {i.GetComment(target)}')
			
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
					self.wdtBPsWPs.tblBPs.doBPOn(bpevent.GetID(), hex(bl.GetLoadAddress()), True)
					self.txtMultiline.table.setBPAtAddress(hex(bl.GetLoadAddress()), True, False)
				self.driver.handleCommand("br com a -F lldbpyGUI.breakpointHandlerNG")
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
			print(f'INSIDE tblHex.setTxtHex')
			self.tblHex.setTxtHex(memory, True, int(self.tblHex.txtMemAddr.text(), 16))
			print(f'AFTER tblHex.setTxtHex')
		else:
			print(str(error_ref))
			
	def click_restartTarget(self):
		target = self.driver.getTarget()
		launch_info = target.GetLaunchInfo()
#		target.Terminate()
#		target.GetProcess().Kill()
		error = lldb.SBError()
		target.Launch(launch_info, error)

#	def click_ReadMemory(self):
#		try:
#			self.handle_readMemory(self.driver.debugger, int(self.tblHex.txtMemAddr.text(), 16), int(self.tblHex.txtMemSize.text(), 16))
#		except Exception as e:
#			print(f"Error while reading memory from process: {e}")
			
#	def click_saveBP(self):
#		filename = showSaveFileDialog()
#		if filename != None:
#			print(f'Saving to: {filename} ...')
#			self.bpHelper.handle_saveBreakpoints(self.driver.getTarget(), filename)
#			self.updateStatusBar(f"Saving breakpoints to {filename} ...")
##			self.driver.handleCommand(f"breakpoint write -f {filename}")
			
	def loadTestBPs(self, filename):
		if filename != None:
			print(f'Loading Breakpoints from: {filename} ...')
			self.updateStatusBar(f"Loading Breakpoints from {filename} ...")
			self.driver.handleCommand(f"breakpoint read -f {filename}")
		pass
		
#	def click_loadBP(self):
#		filename = showOpenBPFileDialog()
#		if filename != None:
#			print(f'Loading Breakpoints from: {filename} ...')
#			self.updateStatusBar(f"Loading Breakpoints from {filename} ...")
#			self.driver.handleCommand(f"breakpoint read -f {filename}")
#			
##		self.updateStatusBar("Loading breakpoints ...")
#		pass
	
#	def click_reloadBP(self):
#		self.reloadBreakpoints(True)
#		self.updateStatusBar("All Breakpoints reloaded!")
	
#	def click_deleteAllBP(self):
#		if showQuestionDialog(self, "Delete all Breakpoints?", "Do you really want to delete all Breakpoints?"):
#			self.bpHelper.handle_deleteAllBPs()
#			self.txtMultiline.table.handle_deleteAllBPs()
#			self.updateStatusBar("All Breakpoints deleted!")
		
	def click_exit_action(self):
		self.close()
		pass
		
	def reloadBreakpoints(self, initTable = True):
		self.updateStatusBar("Reloading breakpoints ...")
#		if initTable: # TODO: Implement Update instead of complete refresh
#		if initTable:
#			self.wdtBPsWPs.tblBPs.resetContent()
		self.start_loadBreakpointsWorker(initTable)
		
	def reloadRegister(self, initTabs = True):
		self.updateStatusBar("Reloading registers ...")
		if initTabs:
			self.tabWidgetReg.clear()
		self.start_loadRegisterWorker(initTabs)
	
	def setProgressValue(self, newValue):
		self.progressbar.setValue(int(newValue))
		pass
		
	def updateStatusBar(self, msg):
		self.statusBar.showMessage(msg)
		
	def clear_clicked(self):
		self.txtCommands.setText("")
	
	def start_loadBreakpointsWorker(self, initTable = True):
		self.loadBreakpointsWorker = LoadBreakpointsWorker(self.driver, initTable)
		self.loadBreakpointsWorker.signals.finished.connect(self.handle_loadBreakpointsFinished)
		self.loadBreakpointsWorker.signals.sendStatusBarUpdate.connect(self.handle_statusBarUpdate)
		self.loadBreakpointsWorker.signals.sendProgressUpdate.connect(self.handle_progressUpdate)
		self.loadBreakpointsWorker.signals.loadBreakpointsValue.connect(self.handle_loadBreakpointsLoadBreakpointValue)
		self.loadBreakpointsWorker.signals.updateBreakpointsValue.connect(self.handle_updateBreakpointsLoadBreakpointValue)
		self.loadBreakpointsWorker.signals.loadWatchpointsValue.connect(self.handle_loadWatchpointsLoadBreakpointValue)
		self.loadBreakpointsWorker.signals.updateWatchpointsValue.connect(self.handle_updateWatchpointsLoadBreakpointValue)
		self.threadpool.start(self.loadBreakpointsWorker)
		
	
	wpsEnabled = {}
	
	def handle_loadWatchpointsLoadBreakpointValue(self, wp):
#		if initTable:
#			self.txtMultiline.table.setBPAtAddress(loadAddr, True, False)
		self.wpsEnabled[wp.GetID()] = wp.IsEnabled()
		self.wdtBPsWPs.tblWPs.addRow(wp.IsEnabled(), wp.GetID(), hex(wp.GetWatchAddress()), hex(wp.GetWatchSize()), wp.GetWatchSpec(), ("r" if wp.IsWatchingReads() else "") + ("" if wp.IsWatchingReads() and wp.IsWatchingWrites() else "") + ("w" if wp.IsWatchingWrites() else ""), wp.GetHitCount(), wp.GetIgnoreCount(), wp.GetCondition())
		
	
	def handle_updateWatchpointsLoadBreakpointValue(self, wp):
#		print(f'wp.GetWatchValueKind() =====================>>>>>>>>>>>>>> {wp.GetWatchValueKind()} / {lldb.eWatchPointValueKindExpression}')
		
		newEnabled = wp.IsEnabled()
		if wp.GetID() in self.wpsEnabled.keys():
			if self.wpsEnabled[wp.GetID()] != newEnabled:
				newEnabled = not newEnabled
				wp.SetEnabled(newEnabled)
		else:
			self.wpsEnabled[wp.GetID()] = newEnabled
			wp.SetEnabled(newEnabled)
			
		self.wdtBPsWPs.tblWPs.updateRow(newEnabled, wp.GetID(), hex(wp.GetWatchAddress()), hex(wp.GetWatchSize()), wp.GetWatchSpec(), ("r" if wp.IsWatchingReads() else "") + ("" if wp.IsWatchingReads() and wp.IsWatchingWrites() else "") + ("w" if wp.IsWatchingWrites() else ""), wp.GetHitCount(), wp.GetIgnoreCount(), wp.GetCondition())
		
	def handle_loadBreakpointsLoadBreakpointValue(self, bp, initTable):			
		names = lldb.SBStringList()
		bp.GetNames(names)
		num_names = names.GetSize()
		name = names.GetStringAtIndex(0)
		cmds = lldb.SBStringList()
		bp.GetCommandLineCommands(cmds)
		num_cmds = cmds.GetSize()
		cmd = cmds.GetStringAtIndex(0)
		bpNode = EditableTreeItem(self.wdtBPsWPs.treBPs, [str(bp.GetID()), '', '', name, str(bp.GetHitCount()), bp.GetCondition(), cmd])
		bpNode.enableBP(bp.IsEnabled())
		idx = 1
		for bl in bp:
			if initTable:
				self.txtMultiline.table.setBPAtAddress(hex(bl.GetLoadAddress()), True, False)
				
			print(f"SETTING UP BP CALLBACK")
			print(f"command script import --allow-reload ./lldbpyGUIWindow.py")
			extra_args = lldb.SBStructuredData()
			self.driver.handleCommand("command script import --allow-reload lldbpyGUIWindow.py")
			bp.SetScriptCallbackFunction("lldbpyGUIWindow.my_callback", extra_args)
			
			txtID = str(bp.GetID()) + "." + str(idx)
			sectionNode = EditableTreeItem(bpNode, [txtID, '', hex(bl.GetLoadAddress()), name, str(bl.GetHitCount()), bl.GetCondition(), ''])
			sectionNode.enableBP(bl.IsEnabled())
			sectionNode.setToolTip(1, f"Enabled: {bl.IsEnabled()}")
			sectionNode.setTextAlignment(0, Qt.AlignmentFlag.AlignLeft)
			idx += 1
		bpNode.setExpanded(True)
	
	def handle_updateBreakpointsLoadBreakpointValue(self, bp):
		rootItem = self.wdtBPsWPs.treBPs.invisibleRootItem()
		for childPar in range(rootItem.childCount()):
			parentItem = rootItem.child(childPar)
			if parentItem.text(0) == str(bp.GetID()):
				if parentItem.text(4) != str(bp.GetHitCount()):
					parentItem.setText(4, str(bp.GetHitCount()))
				if bp.GetCondition() != None and str(bp.GetCondition()) != "":
					if parentItem.text(5) != str(bp.GetCondition()):
						parentItem.setText(5, str(bp.GetCondition()))
				else:
					if parentItem.text(5) != "":
						parentItem.setText(5, "")
					
				idx = 0
				for bl in bp:
					for childChild in range(parentItem.childCount()):
						childItem = parentItem.child(childChild)
						if childItem != None:
							if childItem.text(0) == str(bp.GetID()) + "." + str(bl.GetID()):
								if childItem.text(4) != str(bl.GetHitCount()):
									childItem.setText(4, str(bl.GetHitCount()))
								if bl.GetCondition() != None and str(bl.GetCondition()) != "":
									if childItem.text(5) != str(bl.GetCondition()):
										childItem.setText(5, str(bl.GetCondition()))
								else:
									if childItem.text(5) != "":
										childItem.setText(5, "")
								break
					idx += 1
				break
		
	def handle_loadBreakpointsFinished(self):
		self.wdtBPsWPs.treBPs.setPC(self.rip)
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
	tblRegs = []
	def handle_loadRegisterLoadRegister(self, type):
		tabDet = QWidget()
		tblReg = RegisterTableWidget()
		tabDet.tblWdgt = tblReg
		self.tblRegs.append(tblReg)
		tabDet.setLayout(QVBoxLayout())
		tabDet.layout().addWidget(tblReg)
		self.tabWidgetReg.addTab(tabDet, type)
		self.currTblDet = tblReg
		
	def handle_loadRegisterLoadRegisterValue(self, idx, type, register, value):
		target = self.driver.getTarget()
		process = target.GetProcess()
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
		
	def do_execCommand(self, addCmd2Hist = False):
		if self.setHelper.getValue(SettingsValues.CmdHistory):
			self.txtCmd.addCommandToHistory()
			
		self.txtCommands.append(f"({PROMPT_TEXT}) {self.txtCmd.text().strip()}")
		if self.txtCmd.text().strip().lower() in ["clear", "clr"]:
			self.clear_clicked()
		else:
			self.start_execCommandWorker(self.txtCmd.text())
		
	def start_execCommandWorker(self, command):
		workerExecCommand = ExecCommandWorker(self.driver, command)
		
		workerExecCommand.signals.commandCompleted.connect(self.handle_commandFinished)
#		workerExecCommand.signals.finished.connect(self.handle_commandFinished)
		self.threadpool.start(workerExecCommand)
		
	def handle_commandFinished(self, res):
		if res.Succeeded():
#			print(dir(res))
#			print(res.GetOutput())
			self.txtCommands.appendEscapedText(res.GetOutput())
		else:
			self.txtCommands.appendEscapedText(f"{res.GetError()}")
			
		if self.swtAutoscroll.isChecked():
			self.sb = self.txtCommands.verticalScrollBar()
			self.sb.setValue(self.sb.maximum())
	
	def settings_clicked(self, s):
		print("Opening Settings ...")
		self.updateStatusBar("Opening Settings ...")
		
		settingsWindow = SettingsDialog(self.setHelper)
		if settingsWindow.exec():
			print(f'Settings saved')
			self.txtCmd.doAddCmdToHist = self.setHelper.getValue(SettingsValues.CmdHistory)
		
	def load_clicked(self, s):
		
#		global pymobiledevice3GUIApp
		
		useNativeDlg = SettingsHelper.GetValue(SettingsValues.UseNativeDialogs)
		if not useNativeDlg:
			self.app.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeDialogs, True)
		
		dlg = QMessageBox()
		dlg.setWindowTitle("Active target running")
		dlg.setText("Do you want to quit the current target and start a new one?")
		dlg.setIcon(QMessageBox.Icon.Warning)
		dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
		dlg.setDefaultButton(QMessageBox.StandardButton.Yes)
		button = dlg.exec()
		
		doLoadNew = False
		if button == QMessageBox.StandardButton.Yes:
			print(f"RELOADING TARGET!!!!")
			doLoadNew = True
		
#		if not useNativeDlg:
#			self.app.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeDialogs, False)
		
		if doLoadNew:
			self.openLoadTargetFileBrowser()
			
		if not useNativeDlg:
			self.app.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeDialogs, False)
		return
	
	def openLoadTargetFileBrowser(self):
		dialog = QFileDialog(None, "Select executable or library", "", "All Files (*.*)")
		dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
		dialog.setNameFilter("Executables (*.exe *.com *.bat *);;Libraries (*.dll *.so *.dylib)")
		
		if dialog.exec():
			filename = dialog.selectedFiles()[0]
			print(f"Loading new target: {filename}")
#			print("close_application()")
			# # Stop all running tasks in the thread pool
			if self.driver.getTarget().GetProcess(): #pymobiledevice3GUIWindow.process:
				print("KILLING PROCESS")
				
				self.driver.aborted = True
				print("Aborted sent")
				#					os._exit(1)
				#       sys.exit(0)
				#       pymobiledevice3GUIWindow.process.Kill()
				#       global driver
				#       driver.terminate()
				#       pymobiledevice3GUIWindow.driver.getTarget().GetProcess().Stop()
				#       print("Process stopped")        
				self.driver.getTarget().GetProcess().Kill()
				print("Process killed")
				self.handle_reset()
				
				global event_queue
				event_queue = queue.Queue()
#				
#				#				global driver
				self.driver = debuggerdriver.createDriver(self.debugger, event_queue)
				self.driver.aborted = False
				self.driver.createTarget(filename)
				if self.driver.debugger.GetNumTargets() > 0:
					target = self.driver.getTarget()
					
					fname = "main"
					main_bp = target.BreakpointCreateByName(fname, target.GetExecutable().GetFilename())
					main_bp.AddName(fname)
					
					self.click_restartTarget()
					self.loadTarget()
					self.updateStatusBar(f"New target '{filename}' loaded successfully!")
			else:
				print("NO PROCESS TO KILL!!!")
#			else:
		return None
	
	targetBasename = "<not set>"
	def loadFileInfo(self, target):
		self.targetBasename = os.path.basename(target)
#		self.setWindowTitle(APP_NAME + " " + APP_VERSION + " - " + self.targetBasename)
		self.setWinTitleWithState("Initialized")
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
			
	def loadFileStats(self, target):
		statistics = target.GetStatistics()
		stream = lldb.SBStream()
		success = statistics.GetAsJSON(stream)
		if success:
			self.treStats.loadJSON(str(stream.GetData()))
		
	def start_eventListenerWorker(self, debugger, event_listener):
		workerEventListener = EventListenerWorker(debugger, event_listener)
		self.threadpool.start(workerEventListener)
		
	def start_loadSourceWorker(self, debugger, sourceFile, event_listener, lineNum = 1):
		self.workerLoadSource = LoadSourceCodeWorker(debugger, sourceFile, event_listener, lineNum)
		self.workerLoadSource.signals.finished.connect(self.handle_loadSourceFinished)
		
		self.threadpool.start(self.workerLoadSource)
	
	def handle_enableBPTblBPs(self, address, enabled):
		self.txtMultiline.table.enableBP(address, enabled)
		if self.bpHelper.handle_checkBPExists(address) != None:
			self.bpHelper.handle_enableBP(address, enabled)
			if enabled:
				self.driver.handleCommand("br com a -F lldbpyGUI.breakpointHandlerNG")
	
	def handle_enableBP(self, address, enabled):
		if self.bpHelper.handle_checkBPExists(address) != None:
			self.bpHelper.handle_enableBP(address, enabled)
			if enabled:
				self.driver.handleCommand("br com a -F lldbpyGUI.breakpointHandlerNG")
	
	def handle_BPOn(self, address, on):
		res = lldb.SBCommandReturnObject()
		ci = self.driver.debugger.GetCommandInterpreter()
		if on:
			#			self.driver.handleCommand(f"breakpoint set -a {address} -C bpcb")
			
			ci.HandleCommand(f"breakpoint set -a {address} -C bpcb", res)
		else:
			ci.HandleCommand(f"breakpoint set -a {address} -C bpcb", res)
		self.bpHelper.handle_enableBP(address, on)
		
	def setWinTitleWithState(self, state):
		self.setWindowTitle(APP_NAME + " " + APP_VERSION + " - " + self.targetBasename + " - " + state)
		
	def handle_resumeThread(self):
#		print("Trying to Continue ...")
#		error = self.process.Continue()
#		self.isRunning = False
		if self.workerDebug is None or (self.workerDebug != None and not self.workerDebug.isRunning):
			self.start_debugWorker(self.driver, StepKind.Continue)
			self.load_resume.setIcon(ConfigClass.iconPause)
			self.setWinTitleWithState("Running")
		else:
			target = self.driver.getTarget()
			process = target.GetProcess()
			if process:
				thread = process.GetThreadAtIndex(0)
				self.workerDebug.isRunning = False
				error = lldb.SBError()
				if thread.Suspend(error):
					print(f"Suspend-Error: {error}")
					self.load_resume.setIcon(ConfigClass.iconPlay)
					self.setWinTitleWithState("Paused")
#		print("After Continue ...")
#		if error:
#			print(error)
			
	def handle_stopThread(self):
		print("Trying to SIGINT ...")
		error = self.process.Stop()
		self.setWinTitleWithState("Stopped")
		print("After SIGINT ...")
		if error:
			print(error)
	
	workerDebug = None
	def start_debugWorker(self, driver, kind):
		if self.workerDebug == None or not self.workerDebug.isRunning:
			self.setResumeActionIcon(ConfigClass.iconPause)
			self.workerDebug = DebugWorker(driver, kind)
			self.workerDebug.signals.debugStepCompleted.connect(self.handle_debugStepCompleted)
#			self.workerDebug.signals.setPC.connect(self.handle_debugSetPC)
			
			self.threadpool.start(self.workerDebug)
		
#	def handle_debugSetPC(self, newPC):
#		self.wdtBPsWPs.treBPs.setPC(hex(newPC))
		
	rip = ""
	
	def handle_debugStepCompleted(self, kind, success, rip, frm):
		if success:
			self.rip = rip
			self.txtMultiline.setPC(int(str(self.rip), 16))
			self.wdtBPsWPs.treBPs.setPC(self.rip)
			self.reloadRegister(False)
			self.reloadBreakpoints(False)
			self.loadStacktrace()
			context = frm.GetSymbolContext(lldb.eSymbolContextEverything)
			self.start_loadSourceWorker(self.debugger, ConfigClass.testTargetSource, self.interruptLoadSourceWorker, context.GetLineEntry().GetLine())
			self.setResumeActionIcon(ConfigClass.iconResume)
			self.setWinTitleWithState("Interrupted")
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
#			self.treThreads.doubleClicked.connect()
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
		self.start_debugWorker(self.driver, StepKind.StepOver)
			
	def stepInto_clicked(self):
		self.start_debugWorker(self.driver, StepKind.StepInto)
		
	def stepOut_clicked(self):
		self.start_debugWorker(self.driver, StepKind.StepOut)
		
	def handle_loadSourceFinished(self, sourceCode, autoScroll = True):
		if sourceCode != "":
			horizontal_value = self.txtSource.horizontalScrollBar().value()
			
			if not autoScroll:
				vertical_value = self.txtSource.verticalScrollBar().value()
			
			self.txtSource.setEscapedText(sourceCode)
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
		start_pos = position + 3
		
		end_pos = self.getNextNBSpace(text, start_pos)
		if text[start_pos:end_pos] == '':
			return
		
		linePos = int(text[start_pos:end_pos])

		scroll_value = linePos * self.txtSource.fontMetrics().height()
		scroll_value -= self.txtSource.viewport().height() / 2
		self.txtSource.verticalScrollBar().setValue(int(scroll_value))
	
#	def read_memory(self, process, address, size):
#		error = lldb.SBError()
#		target = process.GetTarget()
#		
#		# Read memory using ReadMemory function
#		data = target.ReadMemory(address, size, error)
#		
#		if error.Success():
#			return data
#		else:
#			print("Error reading memory:", error)
#			return None			