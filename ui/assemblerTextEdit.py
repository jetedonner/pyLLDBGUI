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
from helper.breakpointHelper import *
from helper.quickToolTip import *
from helper.dialogHelper import *
		
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
	
	def event_bpAdded(self, on = True):
#		self.isBPOn = not self.isBPOn
		if on:
			self.isBPEnabled = True
			self.setIcon(self.iconBPEnabled)
		else:
			self.isBPEnabled = False
			self.setIcon(self.iconStd)
			
	def setBPOn(self, on = True):
#		self.isBPOn = not self.isBPOn
		if on:
			self.isBPEnabled = True
			self.setIcon(self.iconBPEnabled)
		else:
			self.isBPEnabled = False
			self.setIcon(self.iconStd)
			
	def enableBP(self, enabled):
#		self.isBPOn = not self.isBPOn
		if enabled:
			self.isBPEnabled = True
			self.setIcon(self.iconBPEnabled)
		else:
			self.isBPEnabled = False
			self.setIcon(self.iconBPDisabled)
	
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
	quickToolTip = QuickToolTip()
	
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
	
	def handle_deleteAllBPs(self):
		for i in range(self.rowCount()):
			self.item(i, 1).setBPOn(False)
		
	def doEnableBP(self, address, enabled):
		for i in range(self.rowCount()):
			if self.item(i, 3).text() == address:
				item = self.item(i, 1)
#				item.toggleBPEnabled()
				item.enableBP(enabled)
				break
		pass
		
	def handle_enableBP(self):
		item = self.item(self.selectedItems()[0].row(), 1)
		item.enableBP(not item.isBPEnabled)
#		item.toggleBPEnabled()
		self.sigEnableBP.emit(self.item(self.selectedItems()[0].row(), 3).text(), item.isBPEnabled)
#		pass
		
	def handle_editCondition(self):
		BreakpointHelper().handle_editCondition(self, 2, 6)
		
	def handle_setPC(self):
		dlg = InputDialog("Set new PC", "Please enter address for PC", self.item(self.selectedItems()[0].row(), 3).text())
		if dlg.exec():
			print(f'dlg.txtInput: {dlg.txtInput.text()}')
			
			frame = self.driver.getTarget().GetProcess().GetThreadAtIndex(0).GetFrameAtIndex(0)
			if frame:
				newPC = int(str(dlg.txtInput.text()), 16)
				frame.SetPC(newPC)
				self.window().txtMultiline.setPC(newPC)
		
	driver = None
	
	def __init__(self, driver):
		super().__init__()
#	def __init__(self, *args, **kwargs):
#		super().__init__(*args, **kwargs)
		
		self.driver = driver
		self.context_menu = QMenu(self)
#		actionToggleBP = self.context_menu.addAction("Toggle Breakpoint")
#		actionToggleBP.triggered.connect(self.handle_toggleBP)
		self.actionEnableBP = self.context_menu.addAction("Enable / Disable Breakpoint")
		self.actionEnableBP.triggered.connect(self.handle_enableBP)
		self.context_menu.addSeparator()
		actionEditCondition = self.context_menu.addAction("Edit condition")
		actionEditCondition.triggered.connect(self.handle_editCondition)
		
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
		self.actionShowMemoryFor = self.context_menu.addAction("Show memory for ...")
		self.actionShowMemoryFor.setStatusTip("Show memory for ...")
		self.actionShowMemoryFor.triggered.connect(self.handle_showMemoryFor)
		self.context_menu.addSeparator()
		self.actionSetPC = self.context_menu.addAction("Set new PC")
		self.actionSetPC.triggered.connect(self.handle_setPC)
		
		self.setColumnCount(8)
		self.setColumnWidth(0, 24)
		self.setColumnWidth(1, 32)
		self.setColumnWidth(2, 72)
		self.setColumnWidth(3, 108)
		self.setColumnWidth(4, 108)
		self.setColumnWidth(5, 256)
		self.setColumnWidth(6, 324)
		self.setColumnWidth(7, 304)
		self.verticalHeader().hide()
		self.horizontalHeader().show()
		self.horizontalHeader().setHighlightSections(False)
		self.setHorizontalHeaderLabels(['PC', 'BP', '#', 'Address', 'Mnemonic', 'Operands', 'Hex', 'Comment'])
		self.horizontalHeaderItem(0).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(1).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(2).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
#		self.horizontalHeaderItem(2).setFont(ConfigClass.font)
		self.horizontalHeaderItem(0).setFont(ConfigClass.font)
		self.horizontalHeaderItem(1).setFont(ConfigClass.font)
		self.horizontalHeaderItem(2).setFont(ConfigClass.font)
		self.horizontalHeaderItem(3).setFont(ConfigClass.font)
		self.horizontalHeaderItem(4).setFont(ConfigClass.font)
		self.horizontalHeaderItem(5).setFont(ConfigClass.font)
		self.horizontalHeaderItem(6).setFont(ConfigClass.font)
		self.horizontalHeaderItem(7).setFont(ConfigClass.font)
		self.horizontalHeaderItem(3).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
#		self.horizontalHeaderItem(3).setFont(ConfigClass.font)
		self.horizontalHeaderItem(4).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
#		self.horizontalHeaderItem(4).setFont(ConfigClass.font)
		self.horizontalHeaderItem(5).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
#		self.horizontalHeaderItem(5).setFont(ConfigClass.font)
		self.horizontalHeaderItem(6).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(7).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
#		self.horizontalHeaderItem(6).setFont(ConfigClass.font)
		self.setFont(ConfigClass.font)
		
		self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
		self.setShowGrid(False)
		self.setMouseTracking(True)
		self.cellDoubleClicked.connect(self.on_double_click)
		
	itemOld = None
	
	def mouseMoveEvent(self, event):	
		pos = event.pos()
		item = self.itemAt(pos)
		if item != None and self.itemOld != item:
			row, col = item.row(), item.column()
			if col == 5:
#				print(f"Cell: ({row}, {col}), Mouse: ({pos.x()}, {pos.y()})")
				item.setToolTip(self.quickToolTip.getQuickToolTip(item.text(), self.driver.debugger))
			self.itemOld = item
		
		# Call the original method to ensure default behavior continues
		super().mouseMoveEvent(event)
		
	def on_double_click(self, row, col):
		if col in range(3):
			self.toggleBPOn(row)
#			self.sigBPOn.emit(self.item(self.selectedItems()[0].row(), 3).text(), self.item(self.selectedItems()[0].row(), 1).isBPOn)
			
	def contextMenuEvent(self, event):
		
		if self.item(self.selectedItems()[0].row(), 1).isBPEnabled:
			self.actionEnableBP.setText("Disable Breakpoint")
		else:
			self.actionEnableBP.setText("Enable Breakpoint")
		
		self.actionShowMemoryFor.setText("Show memory for:")
		self.actionShowMemoryFor.setEnabled(False)
		self.actionShowMemoryFor.setData("")
		
		operandsText = self.quickToolTip.getOperandsText(self.item(self.selectedItems()[0].row(), 5).text())
		if operandsText != "":
			self.actionShowMemoryFor.setText("Show memory for: " + operandsText)
			self.actionShowMemoryFor.setEnabled(True)
			self.actionShowMemoryFor.setData(operandsText)
			
		self.context_menu.exec(event.globalPos())
		
	def handle_showMemoryFor(self):
		sender = self.sender()  # get the sender object
		if isinstance(sender, QAction):
			action = sender  # it's the QAction itself
		else:
			# Find the QAction within the sender (e.g., QMenu or QToolBar)
			action = sender.findChild(QAction)
			
		self.doReadMemory(self.quickToolTip.get_memory_address(self.driver.debugger, action.data()))
#		print(f"Triggering QAction: {action.text()}")
			
	def doReadMemory(self, address, size = 0x100):
		self.window().tabWidgetDbg.setCurrentWidget(self.window().tabMemory)
		self.window().txtMemoryAddr.setText(hex(address))
		self.window().txtMemorySize.setText(hex(size))
		try:
#           global debugger
			self.handle_readMemory(self.driver.debugger, int(self.window().txtMemoryAddr.text(), 16), int(self.window().txtMemorySize.text(), 16))
		except Exception as e:
			print(f"Error while reading memory from process: {e}")
			
	def handle_readMemory(self, debugger, address, data_size = 0x100):
		error_ref = lldb.SBError()
		process = debugger.GetSelectedTarget().GetProcess()
		memory = process.ReadMemory(address, data_size, error_ref)
		if error_ref.Success():
#           hex_string = binascii.hexlify(memory)
			# `memory` is a regular byte string
#           print(f'BYTES:\n{memory}\nHEX:\n{hex_string}')
			self.window().hxtMemory.setTxtHexNG(memory, True, int(self.window().txtMemoryAddr.text(), 16))
		else:
			print(str(error_ref))
			
	def toggleBPOn(self, row, updateBPWidget = True):
#		print(f'TOGGLE BP: {self.item(row, 3).text()}')
		item = self.item(row, 1)
		item.toggleBPOn()
		if updateBPWidget:
			self.sigBPOn.emit(self.item(row, 3).text(), item.isBPOn)
		pass
		
	def toggleBPAtAddress(self, address, updateBPWidget = True):
#		self.txtMultiline
#		print(f'CHECKING BREAKPOINT ROW-COUNT: {self.rowCount()}')
		for row in range(self.rowCount()):
#			print(f'CHECKING BREAKPOINT AT ADDRESS: {self.item(row, 3).text()}')
			if self.item(row, 3).text() == address:
				self.toggleBPOn(row, updateBPWidget)
				break
		pass
	
	
	def event_bpAdded(self, bp):
#		self.txtMultiline
#		print(f'CHECKING BREAKPOINT ROW-COUNT: {self.rowCount()}')
		for row in range(self.rowCount()):
#			print(f'CHECKING BREAKPOINT AT ADDRESS: {self.item(row, 3).text()}')
			if self.item(row, 3).text() == hex(bp.GetLoadAddress()):
				self.item(row, 1).event_bpAdded(True)
#				if updateBPWidget:
#					self.sigBPOn.emit(self.item(row, 3).text(), on)
				break
		pass
		
	def setBPAtAddress(self, address, on = True, updateBPWidget = True):
#		self.txtMultiline
#		print(f'CHECKING BREAKPOINT ROW-COUNT: {self.rowCount()}')
		for row in range(self.rowCount()):
#			print(f'CHECKING BREAKPOINT AT ADDRESS: {self.item(row, 3).text()}')
			if self.item(row, 3).text() == address:
				self.item(row, 1).setBPOn(on)
				if updateBPWidget:
					self.sigBPOn.emit(self.item(row, 3).text(), on)
				break
		pass
		
	def removeBPAtAddress(self, address):
#		self.txtMultiline
#		print(f'CHECKING BREAKPOINT ROW-COUNT: {self.rowCount()}')
		for row in range(self.rowCount()):
#			print(f'CHECKING BREAKPOINT AT ADDRESS: {self.item(row, 3).text()}')
			if self.item(row, 3).text() == address:
				self.item(row, 1).setBPOn(False)
#				if updateBPWidget:
#					self.sigBPOn.emit(self.item(row, 3).text(), on)
				break
		pass
		
	def resetContent(self):
		for row in range(self.rowCount(), 0):
			self.removeRow(row)
			
	def addRow(self, lineNum, address, instr, args, comment, data, rip = ""):
		currRowCount = self.rowCount()
		self.setRowCount(currRowCount + 1)
		
		item = DisassemblyImageTableWidgetItem()
		
		self.addItem(currRowCount, 0, ('>' if rip == address else ''))
		self.setItem(currRowCount, 1, item)
		self.addItem(currRowCount, 2, str(lineNum) + ":")
		self.addItem(currRowCount, 3, address)
		self.addItem(currRowCount, 4, instr)
		self.addItem(currRowCount, 5, args)
		self.addItem(currRowCount, 6, data)
		self.addItem(currRowCount, 7, comment)
		
		self.setRowHeight(currRowCount, 14)
		
		
	def addItem(self, row, col, txt):
		item = QTableWidgetItem(txt, QTableWidgetItem.ItemType.Type)
		item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) #Qt.ItemFlag.ItemIsSelectable)
		
		# Insert the items into the row
		self.setItem(row, col, item)
		
	def scrollToRow(self, row):
		row_to_scroll = row
		scroll_value = (row_to_scroll - self.viewport().height() / (2 * self.rowHeight(0))) * self.rowHeight(0)
		self.verticalScrollBar().setValue(scroll_value)
		
		
		
# THIS ONE IS USED FOR NG IMPLEMENTATION !!!
class AssemblerTextEdit(QWidget):
	
	lineCountNG = 0
	table = None
	insts = None
	addr = 0
	
	def setInstsAndAddr(self, insts, addr):
		self.insts = insts
		self.addr = addr
#		print(f'CURRENT ADDRESS: {self.addr}')
	
	def clear(self):
		self.lineCountNG = 0
		self.table.resetContent()
		pass
		
	def appendAsmText(self, addr, instr, args, comment, data, addLineNum = True, rip = ""):
		if addLineNum:
			self.lineCountNG += 1
			self.table.addRow(self.lineCountNG, addr, instr, args, comment, data, rip)
		else:
			self.table.addRow(0, addr, instr, args, comment, data, rip)
			
	def setTextColor(self, color = "black", lineNum = False):
		pass
		
	def setPC(self, pc):
		for row in range(self.table.rowCount()):
			if self.table.item(row, 3).text() == hex(pc):
				self.table.item(row, 0).setText('>')
				self.table.scrollToRow(row)
			else:
				self.table.item(row, 0).setText('')
				
		pass
		
	driver = None
	
	def __init__(self, driver):
		super().__init__()
		self.driver = driver
		self.setLayout(QHBoxLayout())
		
		self.frame = QFrame()
		
		self.vlayout = QHBoxLayout()
		self.frame.setLayout(self.vlayout)
		
		self.table = DisassemblyTableWidget(self.driver)
		
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