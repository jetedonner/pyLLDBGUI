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
		
from ui.assemblerTextEdit import *
from helper.breakpointHelper import *

def breakpointHandlerAuto(dummy, frame, bpno, err):
		print("breakpointHandlerAuto ...")
		print("YESSSSSSS GETTTTTTTIIIIINNNNNNNGGGGG THERE!!!!!!")
		
class BreakpointsTableWidget(QTableWidget):
	
	ommitCellChanged = False
	
#	window() = None
	
#	def resetContentNG(self):
#		#		self.clear()
#		self.clearContents()
#		self.setRowCount(0)
#		#		self.initTable()
#		pass
	
	driver = None
	
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
			item.toggleBPEnabled()
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
			
	def doEnableBP(self, address, enable):
		for i in range(self.rowCount()):
			if self.item(i, 2).text() == address:
				itemCell = self.item(i, 0)
				itemCell.toggleBPEnabled()
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
	
	def __init__(self, driver):
		super().__init__()
#		self.window() = window()
		self.driver = driver
		
#		self.driver.handleCommand("command script add -h '(lldbinit) The breakpoint callback function (auto).' --function breakpointTableWidget.breakpointHandlerAuto bpcbauto")
		
		self.initTable()
		self.context_menu = QMenu(self)
		actionDeleteBP = self.context_menu.addAction("Delete Breakpoint")
		actionDeleteBP.triggered.connect(self.handle_deleteBP)
		actionToggleBP = self.context_menu.addAction("Toggle Breakpoint")
		actionToggleBP.triggered.connect(self.handle_toggleBP)
		actionDisableBP = self.context_menu.addAction("Enable / Disable Breakpoint")
		actionDisableBP.triggered.connect(self.handle_enableBP)
		actionEditCondition = self.context_menu.addAction("Edit condition")
		actionEditCondition.triggered.connect(self.handle_editCondition)
		
		self.context_menu.addSeparator()
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
		self.setColumnWidth(2, 96)
		self.setColumnWidth(3, 108)
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
		pass
			
	def contextMenuEvent(self, event):
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
	
	def updateRow(self, state, num, address, name, hitcount, condition):
		self.ommitCellChanged = True

		for i in range(self.rowCount()):
			if self.item(i, 1).text() == "#" + str(num):
				self.item(i, 0).setBPOn(state)
				self.item(i, 2).setText(address)
				self.item(i, 3).setText(name)
				self.item(i, 4).setText(hitcount)
				self.item(i, 5).setText(condition)
				break
		self.ommitCellChanged = False
		
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

		item.setBPOn(state)
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
			if col == 3:
				target = self.driver.getTarget()
#				idx = 0
				for i in range(target.GetNumBreakpoints()):
#					idx += 1
					bp_cur = target.GetBreakpointAtIndex(i)
					for bl in bp_cur:
						name_list = lldb.SBStringList()
						bp_cur.GetNames(name_list)
						num_names = name_list.GetSize()
#						oldName = "main"
						for j in range(num_names):
							name = name_list.GetStringAtIndex(j)
							print(name + " / " + self.oldBPName)
							if name == self.oldBPName:
								bp_cur.RemoveName(self.oldBPName)
								bp_cur.AddName(self.item(row, 3).text())
								break
			pass