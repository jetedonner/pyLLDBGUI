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
		
class DisassemblyImageTableWidgetItem(QTableWidgetItem):
	
	iconStd = None
	iconBPEnabled = None
	iconBPDisabled = None
	
	isBPOn = False
	isBPEnabled = False
	
	def __init__(self):
		self.iconStd = QIcon()
		super().__init__(self.iconStd, "", QTableWidgetItem.ItemType.Type)
		self.iconBPEnabled = ConfigClass.iconBPEnabled
		self.iconBPDisabled = ConfigClass.iconBPDisabled
		self.setFlags(self.flags() & ~Qt.ItemFlag.ItemIsEditable)
		pass
		
	def toggleBPOn(self):
		self.isBPOn = not self.isBPOn
		if self.isBPOn:
			self.isBPEnabled = True
			self.setIcon(self.iconBPEnabled)
		else:
			self.isBPEnabled = False
			self.setIcon(self.iconStd)
		pass
	
	def toggleBPEnabled(self):
		if not self.isBPOn:
			self.isBPOn = True
			
		self.isBPEnabled = not self.isBPEnabled
		if self.isBPEnabled:
			self.setIcon(self.iconBPEnabled)
		else:
			self.setIcon(self.iconBPDisabled)
		pass
		
class DisassemblyTableWidget(QTableWidget):
	
	sigEnableBP = pyqtSignal(str, bool)
	sigBPOn = pyqtSignal(str, bool)
	
	actionShowMemory = None
	
	def handle_copyHexValue(self):
		item = self.item(self.selectedItems()[0].row(), 5)
		pyperclip.copy(item.text())
		
	def handle_copyInstruction(self):
		item = self.item(self.selectedItems()[0].row(), 4)
		pyperclip.copy(item.text())
		
	def handle_copyAddress(self):
		item = self.item(self.selectedItems()[0].row(), 3)
		pyperclip.copy(item.text())
#		clipboard_contents = pyperclip.paste()
#		print(clipboard_contents)
#		pass
		
	def handle_toggleBP(self):
		item = self.item(self.selectedItems()[0].row(), 1)
		item.toggleBPOn()
		self.sigBPOn.emit(self.item(self.selectedItems()[0].row(), 3).text(), item.isBPOn)
		pass
		
	def handle_disableBP(self):
		item = self.item(self.selectedItems()[0].row(), 1)
		item.toggleBPEnabled()
		self.sigEnableBP.emit(self.item(self.selectedItems()[0].row(), 3).text(), not item.isBPEnabled)
		pass
		
	def __init__(self):
		super().__init__()
		self.context_menu = QMenu(self)
		actionToggleBP = self.context_menu.addAction("Toggle Breakpoint")
		actionToggleBP.triggered.connect(self.handle_toggleBP)
		actionDisableBP = self.context_menu.addAction("Enable / Disable Breakpoint")
		actionDisableBP.triggered.connect(self.handle_disableBP)
		
		self.context_menu.addSeparator()
		actionCopyAddress = self.context_menu.addAction("Copy address")
		actionCopyAddress.triggered.connect(self.handle_copyAddress)
		actionCopyInstruction = self.context_menu.addAction("Copy instruction")
		actionCopyInstruction.triggered.connect(self.handle_copyInstruction)
		actionCopyHex = self.context_menu.addAction("Copy hex value")
		actionCopyHex.triggered.connect(self.handle_copyHexValue)
		self.context_menu.addSeparator()
		actionFindReferences = self.context_menu.addAction("Find references")
		self.actionShowMemory = self.context_menu.addAction("Show memory")
		
		self.setColumnCount(7)
		self.setColumnWidth(0, 24)
		self.setColumnWidth(1, 32)
		self.setColumnWidth(2, 72)
		self.setColumnWidth(3, 108)
		self.setColumnWidth(4, 256)
		self.setColumnWidth(5, 324)
		self.setColumnWidth(6, 304)
		self.verticalHeader().hide()
		self.horizontalHeader().show()
		self.setHorizontalHeaderLabels(['PC', 'BP', '#', 'Address', 'Instruction', 'Hex', 'Comment'])
		self.horizontalHeaderItem(2).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
#		self.horizontalHeaderItem(2).setFont(ConfigClass.font)
		self.horizontalHeaderItem(3).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
#		self.horizontalHeaderItem(3).setFont(ConfigClass.font)
		self.horizontalHeaderItem(4).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
#		self.horizontalHeaderItem(4).setFont(ConfigClass.font)
		self.horizontalHeaderItem(5).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
#		self.horizontalHeaderItem(5).setFont(ConfigClass.font)
		self.horizontalHeaderItem(6).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
#		self.horizontalHeaderItem(6).setFont(ConfigClass.font)
		self.setFont(ConfigClass.font)
		
		self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
		self.setShowGrid(False)
		self.cellDoubleClicked.connect(self.on_double_click)
		
	def on_double_click(self, row, col):
		if col in range(3):
			self.toggleBPOn(row)
#			self.sigBPOn.emit(self.item(self.selectedItems()[0].row(), 3).text(), self.item(self.selectedItems()[0].row(), 1).isBPOn)
		
	def contextMenuEvent(self, event):
		for i in dir(event):
			print(i)
		print(event.pos())
		print(self.itemAt(event.pos().x(), event.pos().y()))
		print(self.selectedItems())
		self.context_menu.exec(event.globalPos())
	
	def toggleBPOn(self, row):
#		print(f'TOGGLE BP: {self.item(row, 3).text()}')
		item = self.item(row, 1)
		item.toggleBPOn()
		self.sigBPOn.emit(self.item(row, 3).text(), item.isBPOn)
		pass
		
	def toggleBPAtAddress(self, address):
#		self.txtMultiline
#		print(f'CHECKING BREAKPOINT ROW-COUNT: {self.rowCount()}')
		for row in range(self.rowCount()):
#			print(f'CHECKING BREAKPOINT AT ADDRESS: {self.item(row, 3).text()}')
			if self.item(row, 3).text() == address:
				self.toggleBPOn(row)
				break
		pass
	
	def resetContent(self):
		for row in range(self.rowCount(), 0):
			self.removeRow(row)
			
	def addRow(self, lineNum, address, instr, comment, data, rip = ""):
		currRowCount = self.rowCount()
		self.setRowCount(currRowCount + 1)

		item = DisassemblyImageTableWidgetItem()
		
		self.addItem(currRowCount, 0, ('>' if rip == address else ''))
		self.setItem(currRowCount, 1, item)
		self.addItem(currRowCount, 2, str(lineNum) + ":")
		self.addItem(currRowCount, 3, address)
		self.addItem(currRowCount, 4, instr)
		self.addItem(currRowCount, 5, data)
		self.addItem(currRowCount, 6, comment)
		
		self.setRowHeight(currRowCount, 18)
		
		
	def addItem(self, row, col, txt):
		item = QTableWidgetItem(txt, QTableWidgetItem.ItemType.Type)
		item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) #Qt.ItemFlag.ItemIsSelectable)
		
		# Insert the items into the row
		self.setItem(row, col, item)
		
class AssemblerTextEdit(QWidget):
	
	lineCountNG = 0
	table = None
	
	def clear(self):
		self.lineCountNG = 0
		self.table.resetContent()
		pass
	
	def appendAsmTextNG(self, addr, instr, comment, data, addLineNum = True, rip = ""):
		if addLineNum:
			self.lineCountNG += 1
			self.table.addRow(self.lineCountNG, addr, instr, comment, data, rip)
		else:
			self.table.addRow(0, addr, instr, comment, data, rip)
	
	def setTextColor(self, color = "black", lineNum = False):
		pass
		
	def setPC(self, pc):
		for row in range(self.table.rowCount()):
			if self.table.item(row, 3).text() == hex(pc):
				print("FOUND ROW")
				self.table.item(row, 0).setText('>')
			else:
				self.table.item(row, 0).setText('')
		pass
		
	def __init__(self):
		super().__init__()
		
		self.setLayout(QHBoxLayout())

		self.frame = QFrame()

		self.vlayout = QHBoxLayout()
		self.frame.setLayout(self.vlayout)
		
		self.table = DisassemblyTableWidget()
		
		self.vlayout.addWidget(self.table)
						
		self.vlayout.setSpacing(0)
		self.vlayout.setContentsMargins(0, 0, 0, 0)
		
		self.frame.setFrameShape(QFrame.Shape.NoFrame)
		self.frame.setFrameStyle(QFrame.Shape.NoFrame)
		self.frame.setContentsMargins(0, 0, 0, 0)
		
		self.widget = QWidget()
		self.layFrame = QHBoxLayout()
		self.layFrame.addWidget(self.frame)
		self.widget.setLayout(self.layFrame)
		
		self.layout().addWidget(self.widget)
		
		
class BreakpointsTableWidget(QTableWidget):
	
#	actionShowMemory = None
	
#	def resetContentNG(self):
#		#		self.clear()
#		self.clearContents()
#		self.setRowCount(0)
#		#		self.initTable()
#		pass
		
	def handle_toggleBP(self):
#		item = self.item(self.selectedItems()[0].row(), 1)
#		item.toggleBPOn()
		pass
		
	def handle_disableBP(self):
		item = self.item(self.selectedItems()[0].row(), 0)
		item.toggleBPEnabled()
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
		
	def __init__(self):
		super().__init__()
		self.initTable()
#		self.context_menu = QMenu(self)
#		actionToggleBP = self.context_menu.addAction("Toggle Breakpoint")
#		actionToggleBP.triggered.connect(self.handle_toggleBP)
#		actionDisableBP = self.context_menu.addAction("Enable / Disable Breakpoint")
#		actionDisableBP.triggered.connect(self.handle_disableBP)
#		
#		self.context_menu.addSeparator()
#		actionCopyAddress = self.context_menu.addAction("Copy address")
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
		self.setColumnWidth(5, 108)
#		self.setColumnWidth(5, 324)
#		self.setColumnWidth(6, 304)
		self.verticalHeader().hide()
		self.horizontalHeader().show()
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
#		self.cellDoubleClicked.connect(self.on_double_click)
		pass
		
	def on_double_click(self, row, col):
#		if col in range(3):
#			self.toggleBPOn(row)
		pass
			
	def contextMenuEvent(self, event):
#		for i in dir(event):
#			print(i)
#		print(event.pos())
#		print(self.itemAt(event.pos().x(), event.pos().y()))
#		print(self.selectedItems())
#		self.context_menu.exec(event.globalPos())
		pass
		
	def toggleBPOn(self, row):
#		item = self.item(row, 1)
#		item.toggleBPOn()
		pass
		
	def resetContent(self):
		for row in range(self.rowCount(), 0):
			self.removeRow(row)
		self.setRowCount(0)
		pass
			
	def addRow(self, state, num, address, nme, hitcount, condition):
		currRowCount = self.rowCount()
		self.setRowCount(currRowCount + 1)
#		
		item = DisassemblyImageTableWidgetItem()
#		
#		self.addItem(currRowCount, 0, ('>' if rip == address else ''))
		item.toggleBPOn()
		self.setItem(currRowCount, 0, item)
		self.addItem(currRowCount, 1, "#" + str(num))
		self.addItem(currRowCount, 2, address)
		self.addItem(currRowCount, 3, nme)
		self.addItem(currRowCount, 4, hitcount)
		self.addItem(currRowCount, 5, condition)
#		self.addItem(currRowCount, 6, comment)
#		
		self.setRowHeight(currRowCount, 18)
		pass
		
	def addItem(self, row, col, txt):
		item = QTableWidgetItem(txt, QTableWidgetItem.ItemType.Type)
		item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) #Qt.ItemFlag.ItemIsSelectable)
		
		# Insert the items into the row
		self.setItem(row, col, item)
		pass