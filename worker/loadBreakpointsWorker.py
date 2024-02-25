#!/usr/bin/env python3
from worker.baseWorker import *
from helper.dbgHelper import *
#from  lldbpyGUIWindow import myTest

#class LoadBreakpointsWorkerReceiver(BaseWorkerReceiver):
#	interruptWorker = pyqtSignal()
	
class LoadBreakpointsWorkerSignals(BaseWorkerSignals):
	loadBreakpoints = pyqtSignal(str)
#	loadBreakpointsValue = pyqtSignal(int, int, str, str, int, str, bool, bool, object)
#	updateBreakpointsValue = pyqtSignal(int, int, str, str, int, str, bool, bool, object)
	loadBreakpointsValue = pyqtSignal(object, bool)
	updateBreakpointsValue = pyqtSignal(object)
	loadWatchpointsValue = pyqtSignal(object)
	updateWatchpointsValue = pyqtSignal(object)
#	updateRegisterValue = pyqtSignal(int, str, str, str)

class LoadBreakpointsWorker(BaseWorker):
	
	initTable = True
		
	def __init__(self, driver, initTable = True):
		super(LoadBreakpointsWorker, self).__init__(driver)
		self.initTable = initTable
		
		self.signals = LoadBreakpointsWorkerSignals()
		
	def workerFunc(self):
		super(LoadBreakpointsWorker, self).workerFunc()
		
		self.sendStatusBarUpdate("Reloading breakpoints ...")
		target = self.driver.getTarget()
#		process = target.GetProcess()
#		if process:
		
#		print("======== START BP INTER =========")
#		for b in target.breakpoint_iter():
#			print(b)
#		print("========= END BP INTER ==========")

		idx = 0
		for i in range(target.GetNumBreakpoints()):
			idx += 1
			bp_cur = target.GetBreakpointAtIndex(i)
#			print(bp_cur)
#			print(bp_cur.GetCondition())
#			for bl in bp_cur:
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
#				
#				
##						self.tblBPs.resetContent()
#				self.tblBPs.addRow(bp_cur.GetID(), idx, hex(bl.GetLoadAddress()), name, str(bp_cur.GetHitCount()), bp_cur.GetCondition())
#				def myTest(self):
#					print("MYTEST")
#					
#				print(f'bp_cur.GetID() ==> {bp_cur.GetID()}')
#				bl.SetScriptCallbackBody("print(f'HELLLLLLLLLLLLLLOOOOOOOOO SSSSCCCCRRRRIIIIIPPPTTTTT CALLBACK BLLLLLL!!!!! {bp_loc}');")
			if self.initTable:
				print(f'RELOADING BREAKPOINT NUM => {bp_cur.GetID()}')
				self.signals.loadBreakpointsValue.emit(bp_cur, self.initTable)
#					self.signals.loadBreakpointsValue.emit(bp_cur.GetID(), bp_cur.GetID(), hex(bl.GetLoadAddress()), name, bp_cur.GetHitCount(), bp_cur.GetCondition(), self.initTable, bp_cur.IsEnabled(), bp_cur)
			else:
				print(f'RELOADING BREAKPOINT NUM => {bp_cur.GetID()}')
				self.signals.updateBreakpointsValue.emit(bp_cur)
#					self.signals.updateBreakpointsValue.emit(bp_cur.GetID(), bp_cur.GetID(), hex(bl.GetLoadAddress()), name, bp_cur.GetHitCount(), bp_cur.GetCondition(), self.initTable, bp_cur.IsEnabled(), bp_cur)
#					
#					self.signals.updateBreakpointsValue.emit(bp_cur.GetID(), bp_cur.GetID(), hex(bl.GetLoadAddress()), name, bp_cur.GetHitCount(), bp_cur.GetCondition(), self.initTable, bp_cur.IsEnabled(), bp_cur)
		
		for wp_loc in target.watchpoint_iter():
#			print(wp_loc)
			if self.initTable:
				self.signals.loadWatchpointsValue.emit(wp_loc)
			else:
				self.signals.updateWatchpointsValue.emit(wp_loc)
#		self.signals.finished.emit()
		pass
		

		