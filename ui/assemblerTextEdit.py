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

class BreakpointTreeWidgetItem(QTreeWidgetItem):
	iconStd = None
	iconBPEnabled = None
	iconBPDisabled = None
	
	isBPOn = False
	isBPEnabled = False
	
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setIcon(0, ConfigClass.iconBPEnabled)
	pass
	
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
		if self.item(self.selectedItems()[0].row(), 5) != None:
			item = self.item(self.selectedItems()[0].row(), 5)
			pyperclip.copy(item.text())
		
	def handle_copyInstruction(self):
		if self.item(self.selectedItems()[0].row(), 4) != None:
			item = self.item(self.selectedItems()[0].row(), 4)
			pyperclip.copy(item.text())
		
	def handle_copyAddress(self):
		if self.item(self.selectedItems()[0].row(), 3) != None:
			item = self.item(self.selectedItems()[0].row(), 3)
			pyperclip.copy(item.text())
#		clipboard_contents = pyperclip.paste()
#		print(clipboard_contents)
#		pass
		
	def handle_toggleBP(self):
		if self.item(self.selectedItems()[0].row(), 1) != None:
			item = self.item(self.selectedItems()[0].row(), 1)
			item.toggleBPOn()
			self.sigBPOn.emit(self.item(self.selectedItems()[0].row(), 3).text(), item.isBPOn)
		pass
	
	def handle_deleteAllBPs(self):
		for i in range(self.rowCount()):
			if self.item(i, 1) != None:
				self.item(i, 1).setBPOn(False)
		
	def enableBP(self, address, enabled):
		for i in range(self.rowCount()):
			if self.item(i, 3) != None and self.item(i, 3).text() == address:
				item = self.item(i, 1)
#				item.toggleBPEnabled()
				item.enableBP(enabled)
				break
		pass
		
	def handle_editBP(self):
#		self.sigEnableBP.emit(self.item(self.selectedItems()[0].row(), 3).text(), item.isBPEnabled)
		if self.item(self.selectedItems()[0].row(), 3) != None:
			self.window().tabWidgetDbg.setCurrentIndex(3)
			self.window().wdtBPsWPs.tblBPs.setFocus()
			self.window().wdtBPsWPs.tblBPs.selectBPRow(self.item(self.selectedItems()[0].row(), 3).text())
#		pass
		
	def handle_enableBP(self):
		if self.item(self.selectedItems()[0].row(), 1) != None:
			item = self.item(self.selectedItems()[0].row(), 1)
			item.enableBP(not item.isBPEnabled)
			self.window().wdtBPsWPs.treBPs.enableBPByAddress(self.item(self.selectedItems()[0].row(), 3).text(),  item.isBPEnabled)
	#		item.toggleBPEnabled()
#			self.sigEnableBP.emit(self.item(self.selectedItems()[0].row(), 3).text(), item.isBPEnabled)
	#		pass
		
	def handle_editCondition(self):
		BreakpointHelper().handle_editCondition(self, 2, 6)
		
	def handle_setPC(self):
		if self.item(self.selectedItems()[0].row(), 3) != None:
			dlg = InputDialog("Set new PC", "Please enter address for PC", self.item(self.selectedItems()[0].row(), 3).text())
			if dlg.exec():
				print(f'dlg.txtInput: {dlg.txtInput.text()}')
				
				frame = self.driver.getTarget().GetProcess().GetThreadAtIndex(0).GetFrameAtIndex(0)
				if frame:
					newPC = int(str(dlg.txtInput.text()), 16)
					frame.SetPC(newPC)
					self.window().txtMultiline.setPC(newPC)
					
	def handle_gotoAddr(self):
		if self.item(self.selectedItems()[0].row(), 3) != None:
			gotoDlg = GotoAddressDialog(self.item(self.selectedItems()[0].row(), 3).text())
			if gotoDlg.exec():
				print(f"GOING TO ADDRESS: {gotoDlg.txtInput.text()}")
				newPC = str(gotoDlg.txtInput.text())
				self.window().txtMultiline.viewAddress(newPC)
			pass
		
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
		self.actionEditBP = self.context_menu.addAction("Edit Breakpoint")
		self.actionEditBP.triggered.connect(self.handle_editBP)
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
		self.actionFindReferences = self.context_menu.addAction("Find references")
		self.actionFindReferences.triggered.connect(self.handle_findReferences)
		self.actionShowMemory = self.context_menu.addAction("Show memory")
		self.actionShowMemoryFor = self.context_menu.addAction("Show memory for ...")
		self.actionShowMemoryFor.setStatusTip("Show memory for ...")
		self.actionShowMemoryFor.triggered.connect(self.handle_showMemoryFor)
		self.context_menu.addSeparator()
		self.actionSetPC = self.context_menu.addAction("Set new PC")
		self.actionSetPC.triggered.connect(self.handle_setPC)
		self.actionGotoAddr = self.context_menu.addAction("Goto Address")
		self.actionGotoAddr.triggered.connect(self.handle_gotoAddr)
		
		self.verticalScrollBar().valueChanged.connect(self.handle_valueChanged)
		self.verticalScrollBar().rangeChanged.connect(self.handle_rangeChanged)
		
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
		elif col in range(4, 6):
			if self.item(self.selectedItems()[0].row(), 4) != None:
				if self.item(self.selectedItems()[0].row(), 4).text().startswith(("call", "jmp", "jne", "jz", "jnz")):
	#				frame = self.driver.getTarget().GetProcess().GetThreadAtIndex(0).GetFrameAtIndex(0)
	#				if frame:
	#					newPC = int(str(self.item(self.selectedItems()[0].row(), 5).text()), 16)
	#					frame.SetPC(newPC)
	#					self.window().txtMultiline.setPC(newPC)
#					for row in range(self.window().txtMultiline.table.rowCount()):
#						if self.window().txtMultiline.table.item(row, 3) != None and self.window().txtMultiline.table.item(row, 5) != None: 
#							if self.window().txtMultiline.table.item(row, 3).text() == str(self.item(self.selectedItems()[0].row(), 5).text()):
#		#							self.table.item(row, 0).setText('>')
#								self.window().txtMultiline.table.scrollToRow(row)
#								self.window().txtMultiline.table.selectRow(row)
#		#						else:
#		#							self.table.item(row, 0).setText('')
#								print(f'JUMPING!!!')
#								break
					for row in range(self.rowCount()):
						if self.item(row, 3) != None and self.item(row, 5) != None: 
							if self.item(row, 3).text() == str(self.item(self.selectedItems()[0].row(), 5).text()):
		#							self.table.item(row, 0).setText('>')
								self.scrollToRow(row)
								self.selectRow(row)
		#						else:
		#							self.table.item(row, 0).setText('')
								print(f'JUMPING!!!')
								break
#			pass
#			self.sigBPOn.emit(self.item(self.selectedItems()[0].row(), 3).text(), self.item(self.selectedItems()[0].row(), 1).isBPOn)
			
	def contextMenuEvent(self, event):
		if self.item(self.selectedItems()[0].row(), 1) != None:
			if self.item(self.selectedItems()[0].row(), 1).isBPEnabled:
				self.actionEnableBP.setText("Disable Breakpoint")
			else:
				self.actionEnableBP.setText("Enable Breakpoint")
			self.actionEnableBP.setData(self.item(self.selectedItems()[0].row(), 1).isBPEnabled)
			
			self.actionShowMemoryFor.setText("Show memory for:")
			self.actionShowMemoryFor.setEnabled(False)
			self.actionShowMemoryFor.setData("")
			if self.item(self.selectedItems()[0].row(), 5) != None:
				operandsText = self.quickToolTip.getOperandsText(self.item(self.selectedItems()[0].row(), 5).text())
				if operandsText != "":
					self.actionShowMemoryFor.setText("Show memory for: " + operandsText)
					self.actionShowMemoryFor.setEnabled(True)
					self.actionShowMemoryFor.setData(operandsText)
			
		self.context_menu.exec(event.globalPos())
	
	def getSelItemText(self, col):
		if self.item(self.selectedItems()[0].row(), col) != None:
			return self.item(self.selectedItems()[0].row(), col).text()
		else:
			return ""
	
	def handle_findReferences(self):
		
#		print(f'Find References to address: {self.getSelItemText(3)}')
		
		address = self.getSelItemText(3)
		
		self.window().start_findReferencesWorker(address, True)
#		print(f'Find References to address: {address}')
##		target = self.driver.getTarget()
#		# Now call SBTarget.ResolveSymbolContextForAddress() with address1.
#		try:
#			for i in range(self.rowCount()):
#				if self.item(i, 5) != None and address in self.item(i, 5).text():
#					print(f'Reference found at address: {self.item(i, 3).text()}')
##					item = self.item(i, 1)
##	#				item.toggleBPEnabled()
##					item.enableBP(enabled)
##					break
##			pass
###			context1 = target.ResolveSymbolContextForAddress(lldb.SBAddress(address, target), lldb.eSymbolContextEverything)
##	
##	#		self.assertTrue(context1)
##	#		if self.TraceOn():
###			print("context1:", context1)
##		
##			target = self.driver.getTarget()
##			for module in target.module_iter():
##				for section in module.section_iter():
###					if not section.IsReadable():
###						continue
##					
##					chunk_size = 1024
##					address = section.GetLoadAddress(target)
##					remaining_bytes = section.GetByteSize()
##					
##					while remaining_bytes > 0:
##						# Read a chunk of data
##						error = lldb.SBError()
##						data = target.ReadMemory(lldb.SBAddress(address, target), min(remaining_bytes, chunk_size), error)
##						print(error)
##						address += len(data)
##						remaining_bytes -= len(data)
##						
##						ascii_string = b"Hello"  # Replace with the actual string
##						string_index = data.find(ascii_string)
##						
##						if string_index != -1:
##							# Found the string!
##							print(f"Found string at address: {address + string_index}")
##							break  # Stop searching if found
##					
##					
##					#References
##	#				section_start = section.GetFileAddress()
##	#				section_end = section_start + section.GetByteSize()
##	##			
##	#				try:
##	#					if address >= section_start and address < section_end:
##	#						instructions = target.ReadInstructions(lldb.SBAddress(address, target), 100, 'intel')  # Adjust count as needed
##	#						for instruction in instructions:
##	#							operand = instruction.GetOperands(target)
##	#							print(f'OPERAND: {operand}')
##	#							if operand == hex(address):
##	#								print(f"Found reference at instruction: {instruction}")
##	#	#					pass
##	#						pass
##	#				except Exception as e:
##	#					print(f'EXCEPTION {e}')
##	#		pass
#		except Exception as e:
#			print(f'EXCEPTION {e}')
#		return
		
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
		self.window().tblHex.txtMemAddr.setText(hex(address))
		self.window().tblHex.txtMemSize.setText(hex(size))
		try:
#           global debugger
#			self.handle_readMemory(self.driver.debugger, int(self.window().tblHex.txtMemAddr.text(), 16), int(self.window().tblHex.txtMemSize.text(), 16))
			self.window().tblHex.handle_readMemory(self.driver.debugger, int(self.window().tblHex.txtMemAddr.text(), 16), int(self.window().tblHex.txtMemSize.text(), 16))
		except Exception as e:
			print(f"Error while reading memory from process: {e}")
			
#	def handle_readMemory(self, debugger, address, data_size = 0x100):
##		error_ref = lldb.SBError()
##		process = debugger.GetSelectedTarget().GetProcess()
##		memory = process.ReadMemory(address, data_size, error_ref)
##		if error_ref.Success():
###           hex_string = binascii.hexlify(memory)
##			# `memory` is a regular byte string
###           print(f'BYTES:\n{memory}\nHEX:\n{hex_string}')
###			self.window().hxtMemory.setTxtHexNG(memory, True, int(self.window().txtMemoryAddr.text(), 16))
##			pass
##			
##		else:
##			print(str(error_ref))
#		self.window().tblHex.handle_readMemory(debugger, address, data_size)
			
	def toggleBPOn(self, row, updateBPWidget = True):
#		print(f'TOGGLE BP: {self.item(row, 3).text()}')
		if self.item(row, 1) != None:
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
			if self.item(row, 3) != None and self.item(row, 3).text() == address:
				self.toggleBPOn(row, updateBPWidget)
				break
		pass
	
	
	def event_bpAdded(self, bp):
#		self.txtMultiline
#		print(f'CHECKING BREAKPOINT ROW-COUNT: {self.rowCount()}')
		for row in range(self.rowCount()):
#			print(f'CHECKING BREAKPOINT AT ADDRESS: {self.item(row, 3).text()}')
			if self.item(row, 3) != None and self.item(row, 3).text() == hex(bp.GetLoadAddress()):
				if self.item(row, 1) != None:
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
			if self.item(row, 3) != None and self.item(row, 3).text() == address:
				if self.item(row, 1) != None:
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
			if self.item(row, 3) != None and self.item(row, 3).text() == address:
				if self.item(row, 1) != None:
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
		if self.rowCount() >= 1:
			
			row_to_scroll = row + self.symbolCount
			scroll_value = (row_to_scroll - self.viewport().height() / (2 * self.rowHeight(1))) * self.rowHeight(1)
#			print(f'scroll_value => {scroll_value}')
			self.verticalScrollBar().setValue(int(scroll_value))
#			print(f'self.verticalScrollBar().value() => {self.verticalScrollBar().value()}')
			QApplication.processEvents()
#		QCoreApplication.processEvents()
		
		
	def handle_valueChanged(self, value):
#		print(f'handle_valueChanged => {value}')
		pass
		
	def handle_rangeChanged(self, min, max):
#		print(f'handle_rangeChanged: min => {min} / max => {max}')
		pass
	
	symbolCount = 0
		
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
	
	def appendAsmSymbol(self, addr, symbol):
		# Define the text for the spanning cell
		text = symbol
		
		table_widget = self.table
		# Get the row count
		row_count = table_widget.rowCount()
		
		# Insert a new row
		table_widget.insertRow(row_count)
		
		# Create a spanning cell item
		item = QTableWidgetItem(f'function: {text}')
		
		# Set the item to span all columns
		table_widget.setSpan(row_count, 0, 1, table_widget.columnCount())  # Adjust row and column indices as needed
		
		# Set the item in the table
		table_widget.setItem(row_count, 0, item)
		self.table.symbolCount += 1
		pass
		
	def appendAsmText(self, addr, instr, args, comment, data, addLineNum = True, rip = ""):
		if addLineNum:
			self.lineCountNG += 1
			self.table.addRow(self.lineCountNG, addr, instr, args, comment, data, rip)
		else:
			self.table.addRow(0, addr, instr, args, comment, data, rip)
			
	def setTextColor(self, color = "black", lineNum = False):
		pass
	
	def viewAddress(self, address):
		for row in range(self.table.rowCount()):
			if self.table.item(row, 3) != None:
				if self.table.item(row, 3).text().lower() == address.lower():
#					self.table.item(row, 0).setText('>')
					self.table.setFocus(Qt.FocusReason.NoFocusReason)
					self.table.selectRow(row)
					self.table.scrollToRow(row)
					break
				
	def setPC(self, pc):
		for row in range(self.table.rowCount()):
			if self.table.item(row, 3) != None:
				if self.table.item(row, 3).text().lower() == hex(pc).lower():
					self.table.item(row, 0).setText('>')
					self.table.scrollToRow(row)
#					print(f'scrollToRow: {row}')
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