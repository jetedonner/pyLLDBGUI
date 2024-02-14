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
		
	def setBPOn(self, on = True):
#		self.isBPOn = not self.isBPOn
		if on:
			self.isBPEnabled = True
			self.setIcon(self.iconBPEnabled)
		else:
			self.isBPEnabled = False
			self.setIcon(self.iconStd)
	
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
		
	def handle_enableBP(self):
		item = self.item(self.selectedItems()[0].row(), 1)
		item.toggleBPEnabled()
		self.sigEnableBP.emit(self.item(self.selectedItems()[0].row(), 3).text(), not item.isBPEnabled)
		pass
		
	def handle_editCondition(self):
		BreakpointHelper().handle_editCondition(self, 2, 6)
		
	driver = None
	
	def __init__(self, driver):
		super().__init__()
#	def __init__(self, *args, **kwargs):
#		super().__init__(*args, **kwargs)
		
		self.driver = driver
		self.context_menu = QMenu(self)
		actionToggleBP = self.context_menu.addAction("Toggle Breakpoint")
		actionToggleBP.triggered.connect(self.handle_toggleBP)
		actionDisableBP = self.context_menu.addAction("Enable / Disable Breakpoint")
		actionDisableBP.triggered.connect(self.handle_enableBP)
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
		self.actionShowMemoryFor.triggered.connect(self.handle_showMemoryFor)
		
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
#		# Access mouse cursor position using event.globalX() and event.globalY()
#		# Get the cell under the cursor using self.itemAt(event.pos())
#		# Perform your desired custom logic based on cell position and mouse movement
#		
#		# Example: Print cell coordinates and mouse position
#		pos = event.pos()
#		item = self.itemAt(pos)
#		if item != None and self.itemOld != item:
#			row, col = item.row(), item.column()
#			print(f"Cell: ({row}, {col}), Mouse: ({pos.x()}, {pos.y()})")
#			
#			if col == 5:
#				parts = item.text().split(",")  # Split at the first comma
#				string1 = parts[0].strip()  # "Hello"
#				string2 = parts[1].strip()  # "world"
#		#		print(f'string1: {string1}')
#		#		print(f'string2: {string2}')
#				
#				address = 0
#				if string1.startswith("dword ptr"):
#		#			print("String starts with 'dword'")
#					strOp = self.extractOperand(string1)
#					print(strOp)
#					strOp = strOp.replace(" ", "")
#		#			self.actionShowMemoryFor.setText("Show memory for: " + strOp)
#					# Example usage
#		#			expression = strOp
#					address = self.get_memory_address(self.driver.debugger, strOp)
#					print(f"Memory address: 0x{address:X}")
#	#				self.doReadMemory(address)
#				elif string2.startswith("dword ptr"):
#		#			print("String starts with 'dword'")
#					strOp = self.extractOperand(string2)
#					print(strOp)
#					strOp = strOp.replace(" ", "")
#		#			self.actionShowMemoryFor.setText("Show memory for: " + strOp)
#					# Example usage
#					#			expression = strOp
#					address = self.get_memory_address(self.driver.debugger, strOp)
#					print(f"Memory address: 0x{address:X}")
#	#				self.doReadMemory(address)
#				elif string1.startswith("word ptr"):
#		#			print("String starts with 'dword'")
#					strOp = self.extractOperand(string1)
#					print(strOp)
#					strOp = strOp.replace(" ", "")
#		#			self.actionShowMemoryFor.setText("Show memory for: " + strOp)
#					# Example usage
#		#			expression = strOp
#					address = self.get_memory_address(self.driver.debugger, strOp)
#					print(f"Memory address: 0x{address:X}")
#	#				self.doReadMemory(address)
#				elif string2.startswith("word ptr"):
#		#			print("String starts with 'dword'")
#					strOp = self.extractOperand(string2)
#					print(strOp)
#					strOp = strOp.replace(" ", "")
#		#			self.actionShowMemoryFor.setText("Show memory for: " + strOp)
#					# Example usage
#					#			expression = strOp
#					address = self.get_memory_address(self.driver.debugger, strOp)
#					print(f"Memory address: 0x{address:X}")
#					
#				if address != 0:
#					error_ref = lldb.SBError()
#					process = self.driver.debugger.GetSelectedTarget().GetProcess()
#					memory = process.ReadMemory(address, 0x20, error_ref)
#					if error_ref.Success():
#			#           hex_string = binascii.hexlify(memory)
#						# `memory` is a regular byte string
#			#           print(f'BYTES:\n{memory}\nHEX:\n{hex_string}')
#	#					self.window().hxtMemory.setTxtHexNG(memory, True, int(self.window().txtMemoryAddr.text(), 16))
#						item.setToolTip(str(memory))
#					else:
#						print(str(error_ref))
#			self.itemOld = item
		
		# Modify cell data or appearance within this method as needed
		# Handle other mouse events (e.g., click, drag) if necessary
		
		# Call the original method to ensure default behavior continues
		super().mouseMoveEvent(event)
		
	def on_double_click(self, row, col):
		if col in range(3):
			self.toggleBPOn(row)
#			self.sigBPOn.emit(self.item(self.selectedItems()[0].row(), 3).text(), self.item(self.selectedItems()[0].row(), 1).isBPOn)
			
	def contextMenuEvent(self, event):
		self.actionShowMemoryFor.setText("Show memory for:")
		self.actionShowMemoryFor.setEnabled(False)
		parts = self.item(self.selectedItems()[0].row(), 5).text().split(",")
		if len(parts) >= 2:
			string1 = parts[0].strip()
			string2 = parts[1].strip()
			
			if string1.startswith(("dword ptr", "word ptr", "byte ptr")):
				address, strOp = self.get_memory_addressAndOperands(self.driver.debugger, string1)
				self.actionShowMemoryFor.setText("Show memory for: " + strOp)
				self.actionShowMemoryFor.setEnabled(True)
			elif string2.startswith(("dword ptr", "word ptr", "byte ptr")):
				address, strOp = self.get_memory_addressAndOperands(self.driver.debugger, string2)
				self.actionShowMemoryFor.setText("Show memory for: " + strOp)
				self.actionShowMemoryFor.setEnabled(True)
			else:
				pass
			
		self.context_menu.exec(event.globalPos())
	
	def get_memory_addressAndOperands(self, debugger, operands):
		strOp = self.extractOperand(operands)
		return self.get_memory_address(self.driver.debugger, strOp), strOp
		
	def get_memory_address(self, debugger, expression):
		target = debugger.GetSelectedTarget()
		process = target.GetProcess()
		thread = process.GetSelectedThread()
		frame = thread.GetSelectedFrame()
		
		isMinus = True
		parts = expression.split("-")
		if len(parts) <= 1:
			parts = expression.split("+")
			isMinus = False
		
		if len(parts) == 2:
			rbp_value = frame.EvaluateExpression(f"${parts[0]}").GetValueAsUnsigned()
#			print(f'rbp_value => {rbp_value}')
			# Calculate the desired memory address
			offset_value = int(parts[1].replace("0x", ""), 16)
			if isMinus:
				address = rbp_value - offset_value
			else:
				address = rbp_value + offset_value
		
		print(f"Memory address: 0x{address:X}")
		return address
	
	def extractOperand(self, string):
#		string = "dword ptr [rbp - 0x8]"
		pattern = r"\[([^\]]+)\]"  # Match anything within square brackets, excluding the brackets themselves
		match = re.search(pattern, string)
		
		if match:
			extracted_text = match.group(1)  # Access the captured group
			print(extracted_text)  # Output: rbp - 0x8
			return extracted_text.replace(" ", "")
		else:
			print("No match found")
			return ""
		
	def handle_showMemoryFor(self):
		string = self.item(self.selectedItems()[0].row(), 5).text()
#		print(f'CONTEXT MENU FOR OPERANDS: {string}')
		
		
		parts = string.split(",")  # Split at the first comma
		string1 = parts[0].strip()  # "Hello"
		string2 = parts[1].strip()  # "world"
#		print(f'string1: {string1}')
#		print(f'string2: {string2}')
		
		
		if string1.startswith("dword ptr"):
#			print("String starts with 'dword'")
			strOp = self.extractOperand(string1)
			print(strOp)
			strOp = strOp.replace(" ", "")
#			self.actionShowMemoryFor.setText("Show memory for: " + strOp)
			# Example usage
#			expression = strOp
			address = self.get_memory_address(self.driver.debugger, strOp)
			print(f"Memory address: 0x{address:X}")
			self.doReadMemory(address)
		elif string2.startswith("dword ptr"):
#			print("String starts with 'dword'")
			strOp = self.extractOperand(string2)
			print(strOp)
			strOp = strOp.replace(" ", "")
#			self.actionShowMemoryFor.setText("Show memory for: " + strOp)
			# Example usage
			#			expression = strOp
			address = self.get_memory_address(self.driver.debugger, strOp)
			print(f"Memory address: 0x{address:X}")
			self.doReadMemory(address)
		elif string1.startswith("word ptr"):
#			print("String starts with 'dword'")
			strOp = self.extractOperand(string1)
			print(strOp)
			strOp = strOp.replace(" ", "")
#			self.actionShowMemoryFor.setText("Show memory for: " + strOp)
			# Example usage
#			expression = strOp
			address = self.get_memory_address(self.driver.debugger, strOp)
			print(f"Memory address: 0x{address:X}")
			self.doReadMemory(address)
		elif string2.startswith("word ptr"):
#			print("String starts with 'dword'")
			strOp = self.extractOperand(string2)
			print(strOp)
			strOp = strOp.replace(" ", "")
#			self.actionShowMemoryFor.setText("Show memory for: " + strOp)
			# Example usage
			#			expression = strOp
			address = self.get_memory_address(self.driver.debugger, strOp)
			print(f"Memory address: 0x{address:X}")
			self.doReadMemory(address)
		pass
#	def handle_showMemory(self):
#		address = self.txtMultiline.table.item(self.txtMultiline.table.selectedItems()[0].row(), 3).text()
#		self.doReadMemory(address)
#		
#	def readMemory_click(self):
#		try:
##           global debugger
#			self.handle_readMemory(lldbHelper.debugger, int(self.txtMemoryAddr.text(), 16), int(self.txtMemorySize.text(), 16))
#		except Exception as e:
#			print(f"Error while reading memory from process: {e}")
			
	def doReadMemory(self, address, size = 0x100):
		self.window().tabWidgetDbg.setCurrentWidget(self.window().tabMemory)
#		self.txtMemoryAddr = QLineEdit("0x100003f50")
#		self.txtMemorySize = QLineEdit("0x100")
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
		
		
# THIS ONE IS USED FOR NG IMPLEMENTATION !!!
class AssemblerTextEdit(QWidget):
	
	lineCountNG = 0
	table = None
	
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
#				print("FOUND ROW")
				self.table.item(row, 0).setText('>')
#				index = self.table.model().index(row, 0)
#				self.table.scrollTo(index)
				self.table.scrollTo(self.table.model().index(row, 0))
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