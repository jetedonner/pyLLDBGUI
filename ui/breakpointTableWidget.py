#!/usr/bin/env python3

import lldb
import os
import sys
import re
import pyperclip

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets
from config import *
		
from ui.clickLabel import *
from ui.assemblerTextEdit import *
from helper.dialogHelper import *
from helper.breakpointHelper import *
from ui.addBreakpointDialog import *

def breakpointHandlerAuto(dummy, frame, bpno, err):
		print("breakpointHandlerAuto ...")
		print("YESSSSSSS GETTTTTTTIIIIINNNNNNNGGGGG THERE!!!!!!")

class WatchpointsTableWidget(QTableWidget):
	
	ommitCellChanged = False
	
	def __init__(self, driver):
		super().__init__()
		self.driver = driver
		
#		self.driver.handleCommand("command script add -h '(lldbinit) The breakpoint callback function (auto).' --function breakpointTableWidget.breakpointHandlerAuto bpcbauto")
		
		self.initTable()
		self.context_menu = QMenu(self)
		self.actionEnableWP = self.context_menu.addAction("Enable / Disable Watchpoint")
#		self.actionEnableWP.triggered.connect(self.handle_enableWP)
		self.context_menu.addSeparator()
#		actionDeleteBP = self.context_menu.addAction("Delete Breakpoint")
#		actionDeleteBP.triggered.connect(self.handle_deleteBP)
##		actionToggleBP = self.context_menu.addAction("Toggle Breakpoint")
##		actionToggleBP.triggered.connect(self.handle_toggleBP)
#		
#		actionEditCondition = self.context_menu.addAction("Edit condition")
#		actionEditCondition.triggered.connect(self.handle_editCondition)
#		
#		self.context_menu.addSeparator()
#		actionGotoAddress = self.context_menu.addAction("Goto address")
#		actionGotoAddress.triggered.connect(self.handle_gotoAddress)
#		actionCopyAddress = self.context_menu.addAction("Copy address")
#		actionCopyAddress.triggered.connect(self.handle_copyAddress)
#		
		self.cellDoubleClicked.connect(self.on_double_click)
		self.cellChanged.connect(self.item_changed_handler)
		
#		actionCopyInstruction = self.context_menu.addAction("Copy instruction")
#		actionCopyHex = self.context_menu.addAction("Copy hex value")
#		self.context_menu.addSeparator()
#		actionFindReferences = self.context_menu.addAction("Find references")
#		self.actionShowMemory = self.context_menu.addAction("Show memory")
#		
		
	def initTable(self):
		self.setColumnCount(9)
		self.setColumnWidth(0, 48)
		self.setColumnWidth(1, 32)
		self.setColumnWidth(2, 128)
		self.setColumnWidth(3, 128)
		self.setColumnWidth(4, 128)
		self.setColumnWidth(5, 128)
		self.setColumnWidth(6, 32)
		self.setColumnWidth(7, 48)
		self.setColumnWidth(8, 256)
#		self.setColumnWidth(5, 324)
#		self.setColumnWidth(6, 304)
		self.verticalHeader().hide()
		self.horizontalHeader().show()
		self.horizontalHeader().setHighlightSections(False)
		self.setHorizontalHeaderLabels(['State', '#', 'Address', 'Size', 'Spec', 'Type', 'Hit', 'Ignore', 'Condition'])#, 'Instruction', 'Hex', 'Comment'])
		self.horizontalHeaderItem(0).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(1).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(2).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(3).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(4).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(5).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(6).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(7).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(8).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
#		self.horizontalHeaderItem(5).setTextAlignment(Qt.AlignmentFlag.AlignLeft)
#		self.horizontalHeaderItem(6).setTextAlignment(Qt.AlignmentFlag.AlignLeft)
		self.setFont(ConfigClass.font)
#		
		self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
		self.setShowGrid(False)
#		self.cellDoubleClicked.connect(self.on_double_click)
#		self.addRow(True, 1, "0x10000", "noname", 0, "nocond")
		pass
		
	oldBPName = ""
	
	def on_double_click(self, row, col):
		if col == 3:
			self.oldBPName = self.item(row, 3).text()
		elif col == 2:
#			self.oldBPName = self.item(row, 3).text()
			self.window().txtMultiline.viewAddress(self.item(row, 2).text())
			pass
		pass
		
	def contextMenuEvent(self, event):
		if self.item(self.selectedItems()[0].row(), 0).isBPEnabled:
			self.actionEnableWP.setText("Disable Watchpoint")
		else:
			self.actionEnableWP.setText("Enable Watchpoint")
			
#		for i in dir(event):
#			print(i)
#			print(event.pos())
#			print(self.itemAt(event.pos().x(), event.pos().y()))
#			print(self.selectedItems())
		self.context_menu.exec(event.globalPos())
		
	def item_changed_handler(self, row, col):
		if not self.ommitCellChanged:
			if col == 7: # Name changed
				target = self.driver.getTarget()
				wpFound = False
				for i in range(target.GetNumWatchpoints()):
					wp_cur = target.GetWatchpointAtIndex(i)
					if "#" + str(wp_cur.GetID()) == self.item(self.selectedItems()[0].row(), 1).text():
						wp_cur.SetIgnoreCount(int(self.item(self.selectedItems()[0].row(), 7).text()))
						break
#					for bl in bp_cur:
#						name_list = lldb.SBStringList()
#						bp_cur.GetNames(name_list)
#						num_names = name_list.GetSize()
#						name_list.AppendString("")
#						num_names = 1
#						for j in range(num_names):
#							name = name_list.GetStringAtIndex(j)
#							if name == self.oldBPName:
#								bp_cur.RemoveName(self.oldBPName)
#								bp_cur.AddName(self.item(row, 3).text())
#						wpFound = True
##								break
#						if wpFound:
#							break
			elif col == 8: # Name changed
				target = self.driver.getTarget()
				wpFound = False
				for i in range(target.GetNumWatchpoints()):
					wp_cur = target.GetWatchpointAtIndex(i)
					if "#" + str(wp_cur.GetID()) == self.item(self.selectedItems()[0].row(), 1).text():
						wp_cur.SetCondition(self.item(self.selectedItems()[0].row(), 8).text())
						break
			pass
			
	def updateRow(self, state, num, address, size, spec, name, hitcount, ignore, condition):
		self.ommitCellChanged = True
		
		for i in range(self.rowCount()):
			if self.item(i, 1).text() == "#" + str(num):
				if not state:
					self.item(i, 0).setIcon(ConfigClass.iconEyeGrey)
				else:
					self.item(i, 0).setIcon(ConfigClass.iconEyeRed)
#				self.item(i, 0).enableBP(state)
				self.item(i, 2).setText(str(address))
				self.item(i, 3).setText(str(size))
				self.item(i, 4).setText(str(spec))
				self.item(i, 5).setText(str(name))
				self.item(i, 6).setText(str(hitcount))
				self.item(i, 7).setText(str(ignore))
				self.item(i, 8).setText("" if condition == None else str(condition))
				break
		self.ommitCellChanged = False
		
	def addRow(self, state, num, address, size, spec, name, hitcount, ignore, condition):
		self.ommitCellChanged = True
		currRowCount = self.rowCount()
		self.setRowCount(currRowCount + 1)
		item = DisassemblyImageTableWidgetItem()
		
#		item.enableBP(state)
#		item.setIcon(ConfigClass.iconEyeRed)
		if not state:
			item.setIcon(ConfigClass.iconEyeGrey)
		else:
			item.setIcon(ConfigClass.iconEyeRed)
		self.setItem(currRowCount, 0, item)
		self.addItem(currRowCount, 1, "#" + str(num))
		self.addItem(currRowCount, 2, str(address))
		self.addItem(currRowCount, 3, str(size))
		self.addItem(currRowCount, 4, str(spec))
		self.addItem(currRowCount, 5, str(name))
		self.addItem(currRowCount, 6, str(hitcount))
		self.addItem(currRowCount, 7, str(ignore))
		self.addItem(currRowCount, 8, "" if condition == None else str(condition))
		self.setRowHeight(currRowCount, 18)
		self.ommitCellChanged = False
		
	def addItem(self, row, col, txt):
		item = QTableWidgetItem(txt, QTableWidgetItem.ItemType.Type)
		if col != 5 and col != 7 and col != 8:
			item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) #Qt.ItemFlag.ItemIsSelectable)
			
		# Insert the items into the row
		self.setItem(row, col, item)
		
class BreakpointsTableWidget(QTableWidget):
	
	sigEnableBP = pyqtSignal(str, bool)
	
	ommitCellChanged = False
	
#	window() = None
	
#	def resetContentNG(self):
#		#		self.clear()
#		self.clearContents()
#		self.setRowCount(0)
#		#		self.initTable()
#		pass
	
	driver = None
	
	def setPC(self, pc):
		print(f'def setPC(self, pc): {pc}')
		self.clearSelection()
		for row in range(self.rowCount()):
			if self.item(row, 2) != None:
				if int(self.item(row, 2).text(), 16) == int(pc, 16):
					print(f'SETTING PC: {self.item(row, 2).text()}')
					for i in range(self.colorCount()):
						if self.item(row, i) != None:
							self.item(row, i).setBackground(ConfigClass.colorGreen)
#					break
				else:
					print(f'UNSET PC: {self.item(row, 2).text()}')
					for i in range(self.colorCount()):
						if self.item(row, i) != None:
							self.item(row, i).setBackground(ConfigClass.colorTransparent)
#					self.table.item(row, 0).setText('>')
#					self.table.scrollToRow(row)
#					print(f'scrollToRow: {row}')
#				else:
#					self.table.item(row, 0).setText('')
		
		pass
	
	def handle_deleteBP(self):
		if len(self.selectedItems()) > 0:
#			print(f'SELECTED ITEMS: {reversed(range(len(self.selectedItems())))}')
#			for i in reversed(range(len(self.selectedItems()))):
#				print(f'I== {i}')
#			item = self.item(self.selectedItems()[0].row(), 0)
			itemNum = self.item(self.selectedItems()[0].row(), 1).text()
#			addr = self.item(self.selectedItems()[0].row(), 2).text()
#			item.toggleBPOn()
#			self.driver.handleCommand(f"breakpoint set -a {addr} -C bpcbauto")
			self.removeRow(self.selectedItems()[0].row())
			self.window().updateStatusBar(f"Deleted breakpoint #{itemNum}")
				
		pass
		
	def handle_toggleBP(self):
		if len(self.selectedItems()) > 0:
			item = self.item(self.selectedItems()[0].row(), 0)
			itemNum = self.item(self.selectedItems()[0].row(), 1)
			addr = self.item(self.selectedItems()[0].row(), 2).text()
			item.toggleBPOn()
#			self.driver.handleCommand(f"breakpoint set -a {addr} -C bpcbauto")
			self.window().updateStatusBar(f"Set breakpoint {itemNum.text()} status to {item.isBPEnabled}")
		pass
		
	def handle_enableBP(self):
		if len(self.selectedItems()) > 0:
			item = self.item(self.selectedItems()[0].row(), 0)
			itemNum = self.item(self.selectedItems()[0].row(), 1)
#			item.toggleBPEnabled()
			item.enableBP(not item.isBPEnabled)
			self.sigEnableBP.emit(self.item(self.selectedItems()[0].row(), 2).text(), item.isBPEnabled)
			self.window().updateStatusBar(f"Set breakpoint {itemNum.text()} enabled to {item.isBPEnabled}")
		pass
		
		
	def handle_editCondition(self):
		
		BreakpointHelper().handle_editCondition(self, 1, 5)
#		itemNum = self.item(self.selectedItems()[0].row(), 1)
#		itemCond = self.item(self.selectedItems()[0].row(), 5)
#		title = f'Condition of breakpoint {itemNum.text()}'
#		label = f'Edit the condition of breakpoint {itemNum.text()}'
#		
#		dialog = QInputDialog()
#		dialog.setwindow()Title(title)
#		dialog.setLabelText(label)
#		oldCond = itemCond.text()
#		dialog.setTextValue(oldCond)
#		dialog.textValueChanged.connect(self.handle_editConditionChanged)
#		dialog.resize(512, 128)
#		# Show the dialog and get the selected process name
#		if dialog.exec():
#			# OK pressed
#			pass
#		else:
#			itemCond.setText(oldCond)
#		pass
#	
#	def handle_editConditionChanged(self, text):
#		itemCond = self.item(self.selectedItems()[0].row(), 5)
#		itemCond.setText(text)
#		pass
		
	def handle_gotoAddress(self):
		if len(self.selectedItems()) > 0:
			item = self.item(self.selectedItems()[0].row(), 2)
			self.window().txtMultiline.viewAddress(item.text())
		pass
		
	def handle_copyAddress(self):
		if len(self.selectedItems()) > 0:
			item = self.item(self.selectedItems()[0].row(), 2)
			pyperclip.copy(item.text())
			self.window().updateStatusBar(f"Copied address {item.text()} of breakpoint to clipboard")
	#		clipboard_contents = pyperclip.paste()
	#		print(clipboard_contents)
		pass
	
	def doToggleBP(self, address, on):
		for i in range(self.rowCount()):
			if self.item(i, 2).text() == address:
				itemCell = self.item(i, 0)
				itemCell.toggleBPOn()
				break
			
	def doEnableBP(self, address, enabled):
		for i in range(self.rowCount()):
			if self.item(i, 2).text() == address:
				item = self.item(i, 0)
#				item.toggleBPEnabled()
				item.enableBP(enabled)
				break
	
	def selectBPRow(self, address):
		bBPFound = False
		for i in range(self.rowCount()):
			if self.item(i, 2).text() == address:
#				bBPFound = True
				itemCell = self.item(i, 0)
				self.selectRow(i)
#				itemCell.row().se
#				itemCell.toggleBPOn()
				break
			
	def doBPOn(self, address, on):
		bBPFound = False
		for i in range(self.rowCount()):
			if self.item(i, 2).text() == address:
				bBPFound = True
				itemCell = self.item(i, 0)
				itemCell.toggleBPOn()
				break
		if on and not bBPFound:
			self.addRow(on, self.rowCount() + 1, address, '', '0', '')
	
	def event_bpAdded(self, bp):
		bBPFound = False
		for i in range(self.rowCount()):
			if self.item(i, 2).text() == hex(bp.GetLoadAddress()):
				bBPFound = True
				itemCell = self.item(i, 0)
				itemCell.toggleBPOn()
				break
		if True and not bBPFound:
			print(f'str(bp.GetBreakpoint().GetID()) => {str(bp.GetBreakpoint().GetID())}')
			self.addRow(True, str(bp.GetBreakpoint().GetID()), hex(bp.GetLoadAddress()), '', str(bp.GetHitCount()), bp.GetCondition())
	
	def __init__(self, driver):
		super().__init__()
#		self.window() = window()
		self.driver = driver
		
#		self.driver.handleCommand("command script add -h '(lldbinit) The breakpoint callback function (auto).' --function breakpointTableWidget.breakpointHandlerAuto bpcbauto")
		
		self.initTable()
		self.context_menu = QMenu(self)
		self.actionEnableBP = self.context_menu.addAction("Enable / Disable Breakpoint")
		self.actionEnableBP.triggered.connect(self.handle_enableBP)
		self.context_menu.addSeparator()
		actionDeleteBP = self.context_menu.addAction("Delete Breakpoint")
		actionDeleteBP.triggered.connect(self.handle_deleteBP)
#		actionToggleBP = self.context_menu.addAction("Toggle Breakpoint")
#		actionToggleBP.triggered.connect(self.handle_toggleBP)
		
		actionEditCondition = self.context_menu.addAction("Edit condition")
		actionEditCondition.triggered.connect(self.handle_editCondition)
		
		self.context_menu.addSeparator()
		actionGotoAddress = self.context_menu.addAction("Goto address")
		actionGotoAddress.triggered.connect(self.handle_gotoAddress)
		actionCopyAddress = self.context_menu.addAction("Copy address")
		actionCopyAddress.triggered.connect(self.handle_copyAddress)
		
		self.cellChanged.connect(self.item_changed_handler)
		
#		actionCopyInstruction = self.context_menu.addAction("Copy instruction")
#		actionCopyHex = self.context_menu.addAction("Copy hex value")
#		self.context_menu.addSeparator()
#		actionFindReferences = self.context_menu.addAction("Find references")
#		self.actionShowMemory = self.context_menu.addAction("Show memory")
#		
		
	def initTable(self):
		self.setColumnCount(6)
		self.setColumnWidth(0, 48)
		self.setColumnWidth(1, 32)
		self.setColumnWidth(2, 128)
		self.setColumnWidth(3, 128)
		self.setColumnWidth(4, 32)
		self.setColumnWidth(5, 256)
#		self.setColumnWidth(5, 324)
#		self.setColumnWidth(6, 304)
		self.verticalHeader().hide()
		self.horizontalHeader().show()
		self.horizontalHeader().setHighlightSections(False)
		self.setHorizontalHeaderLabels(['State', '#', 'Address', 'Name', 'Hit', 'Condition'])#, 'Instruction', 'Hex', 'Comment'])
		self.horizontalHeaderItem(0).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(1).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(2).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(3).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(4).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(5).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
#		self.horizontalHeaderItem(5).setTextAlignment(Qt.AlignmentFlag.AlignLeft)
#		self.horizontalHeaderItem(6).setTextAlignment(Qt.AlignmentFlag.AlignLeft)
		self.setFont(ConfigClass.font)
#		
		self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
		self.setShowGrid(False)
		self.cellDoubleClicked.connect(self.on_double_click)
		pass
		
	oldBPName = ""
	
	def on_double_click(self, row, col):
		if col == 3:
			self.oldBPName = self.item(row, 3).text()
		elif col == 1 or col == 2:
#			self.oldBPName = self.item(row, 3).text()
			self.window().txtMultiline.viewAddress(self.item(row, 2).text())
		pass
			
	def contextMenuEvent(self, event):
		if self.item(self.selectedItems()[0].row(), 0).isBPEnabled:
			self.actionEnableBP.setText("Disable Breakpoint")
		else:
			self.actionEnableBP.setText("Enable Breakpoint")
		
#		for i in dir(event):
#			print(i)
#			print(event.pos())
#			print(self.itemAt(event.pos().x(), event.pos().y()))
#			print(self.selectedItems())
		self.context_menu.exec(event.globalPos())
		
	def toggleBPOn(self, row):
#		item = self.item(row, 1)
#		item.toggleBPOn()
		pass
		
	def resetContent(self):
		for row in range(self.rowCount(), 0):
			self.removeRow(row)
		self.setRowCount(0)
	
	def removeRowWithId(self, num):
#		self.ommitCellChanged = True
		
		for i in range(self.rowCount()):
			if self.item(i, 1).text() == "#" + str(num):
				print("FOUND ROW")
				self.removeRow(i)
#				self.item(i, 0).setBPOn(state)
#				self.item(i, 2).setText(address)
#				self.item(i, 3).setText(name)
#				self.item(i, 4).setText(hitcount)
#				self.item(i, 5).setText(condition)
				break
#		self.ommitCellChanged = False
		
	def updateRow(self, state, num, address, name, hitcount, condition):
		self.ommitCellChanged = True

		for i in range(self.rowCount()):
			if self.item(i, 1).text() == "#" + str(num):
				self.item(i, 0).enableBP(state)
				self.item(i, 2).setText(address)
				self.item(i, 3).setText(name)
				self.item(i, 4).setText(hitcount)
				self.item(i, 5).setText(condition)
				break
		self.ommitCellChanged = False
		
	def setCurrentBPHit(self, address):
		for i in range(self.rowCount()):
			if self.item(i, 2).text() == address:
				self.item(i, 0).setBackground(QColor(0, 255, 0, 128))
			else:
				self.item(i, 0).setBackground(QColor(0, 255, 0, 0))
		
#		currRowCount = self.rowCount()
#		self.setRowCount(currRowCount + 1)
#		item = DisassemblyImageTableWidgetItem()
		
#		item.setBPOn(state)
#		self.setItem(currRowCount, 0, item)
#		self.addItem(currRowCount, 1, "#" + str(num))
#		self.addItem(currRowCount, 2, address)
#		self.addItem(currRowCount, 3, name)
#		self.addItem(currRowCount, 4, hitcount)
#		self.addItem(currRowCount, 5, condition)
#		self.setRowHeight(currRowCount, 18)
#		self.ommitCellChanged = False
		
	def addRow(self, state, num, address, name, hitcount, condition):
		self.ommitCellChanged = True
		currRowCount = self.rowCount()
		self.setRowCount(currRowCount + 1)
		item = DisassemblyImageTableWidgetItem()

		item.enableBP(state)
		self.setItem(currRowCount, 0, item)
		self.addItem(currRowCount, 1, "#" + str(num))
		self.addItem(currRowCount, 2, address)
		self.addItem(currRowCount, 3, name)
		self.addItem(currRowCount, 4, hitcount)
		self.addItem(currRowCount, 5, condition)
		self.setRowHeight(currRowCount, 18)
		self.ommitCellChanged = False
		
	def addItem(self, row, col, txt):
		item = QTableWidgetItem(txt, QTableWidgetItem.ItemType.Type)
		if col != 3 and col != 5:
			item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) #Qt.ItemFlag.ItemIsSelectable)
		
		# Insert the items into the row
		self.setItem(row, col, item)
	
	def item_changed_handler(self, row, col):
		if not self.ommitCellChanged:
			
			if col == 3: # Name changed
				target = self.driver.getTarget()
				bpFound = False
#				for i in range(target.GetNumBreakpoints()):
				bp_cur = target.GetBreakpointAtIndex(row)
				for bl in bp_cur:
					name_list = lldb.SBStringList()
					bp_cur.GetNames(name_list)
					num_names = name_list.GetSize()
					name_list.AppendString("")
					num_names = 1
					for j in range(num_names):
						name = name_list.GetStringAtIndex(j)
						if name == self.oldBPName:
							bp_cur.RemoveName(self.oldBPName)
							bp_cur.AddName(self.item(row, 3).text())
							bpFound = True
							break
					if bpFound:
						break
#					if bpFound:
#						break
					
			elif col == 5: # Condition changed
				target = self.driver.getTarget()
				bp_cur = target.GetBreakpointAtIndex(row)
				bp_cur.SetCondition(self.item(row, 5).text())
				pass
				
				
				
class BPsWPsWidget(QWidget):
	
	driver = None
#	caseSensitive = True
	
	def __init__(self, driver):
		super().__init__()
		self.driver = driver
#		self.wdtSearchMain = QWidget()
		self.layBPWPMain = QVBoxLayout()
		
		self.tabWidgetBPsWPs = QTabWidget()
		
		self.tblBPs = BreakpointsTableWidget(self.driver)
		self.tblBPs.sigEnableBP.connect(self.handle_enableBPTblBPs)
		
		self.cmdAddBP = ClickLabel()
		self.cmdAddBP.setPixmap(ConfigClass.pixAdd)
		self.cmdAddBP.setToolTip("Add Breakpoints")
		self.cmdAddBP.clicked.connect(self.click_addBP)
		self.cmdAddBP.setContentsMargins(0, 0, 0, 0)
		
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
		
		self.cmdReloadBPs = ClickLabel()
		self.cmdReloadBPs.setPixmap(ConfigClass.pixReload)
		self.cmdReloadBPs.setToolTip("Reload Breakpoints")
		self.cmdReloadBPs.clicked.connect(self.click_reloadBP)
		self.cmdReloadBPs.setContentsMargins(0, 0, 0, 0)
		
		self.cmdDeleteAllBP = ClickLabel()
		self.cmdDeleteAllBP.setPixmap(ConfigClass.pixTrash)
		self.cmdDeleteAllBP.setToolTip("Delete ALL Breakpoints")
		self.cmdDeleteAllBP.clicked.connect(self.click_deleteAllBP)
		self.cmdDeleteAllBP.setContentsMargins(0, 0, 0, 0)
		
		self.wgtBPCtrls = QWidget()
		self.wgtBPCtrls.setContentsMargins(0, 10, 0, 0)
		self.wgtBPCtrls.setLayout(QHBoxLayout())
		self.wgtBPCtrls.layout().addWidget(self.cmdAddBP)
		self.wgtBPCtrls.layout().addWidget(self.cmdSaveBP)
		self.wgtBPCtrls.layout().addWidget(self.cmdLoadBP)
		self.wgtBPCtrls.layout().addWidget(self.cmdReloadBPs)
		self.wgtBPCtrls.layout().addWidget(self.cmdDeleteAllBP)
#		self.wgtBPCtrls.layout().setContentsMargins(0, 0, 0, 0)
		self.wgtBPCtrls.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
#		self.gbpBPs = QGroupBox("Breakpoints")
#		self.gbpBPs.setLayout(QVBoxLayout())
		self.wdtBPs = QWidget()
		self.wdtBPs.setLayout(QVBoxLayout())
		self.wdtBPs.layout().addWidget(self.wgtBPCtrls)
		self.wdtBPs.layout().addWidget(self.tblBPs)
		self.wdtBPs.setContentsMargins(0, 0, 0, 0)
		
		self.tabWidgetBPsWPs.addTab(self.wdtBPs, "Breakpoints")
		
		self.tblWPs = WatchpointsTableWidget(self.driver)
		self.tabWidgetBPsWPs.addTab(self.tblWPs, "Watchpoints")
		
		self.layBPWPMain.addWidget(self.tabWidgetBPsWPs)
		self.setLayout(self.layBPWPMain)
		
	def handle_enableBPTblBPs(self, address, enabled):
#		self.txtMultiline.table.doEnableBP(address, enabled)
#		if self.bpHelper.handle_checkBPExists(address) != None:
#			self.bpHelper.handle_enableBP(address, enabled)
#			if enabled:
#				self.driver.handleCommand("br com a -F lldbpyGUI.breakpointHandlerNG")
		pass
				
	def handle_enableBP(self, address, enabled):
#		self.tblBPs.doEnableBP(address, enabled)
#		if self.bpHelper.handle_checkBPExists(address) != None:
#			self.bpHelper.handle_enableBP(address, enabled)
#			if enabled:
#				self.driver.handleCommand("br com a -F lldbpyGUI.breakpointHandlerNG")
		pass
				
	def handle_BPOn(self, address, on):
#		self.tblBPs.doBPOn(address, on)
##		print(f"breakpoint set -a {address} -C bpcbdriver")
#		res = lldb.SBCommandReturnObject()
#		ci = self.driver.debugger.GetCommandInterpreter()
#		if on:
#			#			self.driver.handleCommand(f"breakpoint set -a {address} -C bpcb")
#			
#			ci.HandleCommand(f"breakpoint set -a {address} -C bpcb", res)
#		else:
#			ci.HandleCommand(f"breakpoint set -a {address} -C bpcb", res)
#		self.bpHelper.handle_enableBP(address, on)
		pass
		
	def click_addBP(self):
		
		print("Opening AddBreakpointDialog ...")
		self.window().updateStatusBar("Opening AddBreakpointDialog ...")
		
#		project_root = dirname(realpath(__file__))
#		helpDialogPath = os.path.join(project_root, 'resources', 'designer', 'helpDialog.ui')
#		
#		window = uic.loadUi(helpDialogPath)
		addBreakpointDialog = AddBreakpointDialog()
		if addBreakpointDialog.exec():
			print(f'AddBreakpointDialog closed')
		pass
		
	def click_saveBP(self):
		filename = showSaveFileDialog()
		if filename != None:
			print(f'Saving to: {filename} ...')
			self.window().bpHelper.handle_saveBreakpoints(self.driver.getTarget(), filename)
			self.window().updateStatusBar(f"Saving breakpoints to {filename} ...")
			#			self.driver.handleCommand(f"breakpoint write -f {filename}")
		pass
			
	def loadTestBPs(self, filename):
#		if filename != None:
#			print(f'Loading Breakpoints from: {filename} ...')
#			self.updateStatusBar(f"Loading Breakpoints from {filename} ...")
#			self.driver.handleCommand(f"breakpoint read -f {filename}")
		pass
		
	def click_loadBP(self):
#		filename = showOpenBPFileDialog()
#		if filename != None:
#			print(f'Loading Breakpoints from: {filename} ...')
#			self.updateStatusBar(f"Loading Breakpoints from {filename} ...")
#			self.driver.handleCommand(f"breakpoint read -f {filename}")
#			
##		self.updateStatusBar("Loading breakpoints ...")
		pass
		
	def click_reloadBP(self):
#		self.reloadBreakpoints(True)
#		self.updateStatusBar("All Breakpoints reloaded!")
		pass
		
	def click_deleteAllBP(self):
#		if showQuestionDialog(self, "Delete all Breakpoints?", "Do you really want to delete all Breakpoints?"):
#			self.bpHelper.handle_deleteAllBPs()
#			self.txtMultiline.table.handle_deleteAllBPs()
#			self.tblBPs.resetContent()
#			self.updateStatusBar("All Breakpoints deleted!")
		pass