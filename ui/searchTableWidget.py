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
from ui.widgets.QSwitch import *
#from QSwitch import *

from config import *

class SearchTableWidget(QTableWidget):
		
	def handle_showMemory(self):
		if self.item(self.selectedItems()[0].row(), 1) != None:
			self.window().doReadMemory(int(self.item(self.selectedItems()[0].row(), 1).text(), 16))
		pass
		
	def __init__(self):
		super().__init__()
		self.context_menu = QMenu(self)
		self.actionShowMemory = self.context_menu.addAction("Show Memory")
		self.actionShowMemory.triggered.connect(self.handle_showMemory)
#		actionDisableBP = self.context_menu.addAction("Enable / Disable Breakpoint")
#		actionDisableBP.triggered.connect(self.handle_disableBP)
#		
#		self.context_menu.addSeparator()
		
		self.setColumnCount(5)
		self.setColumnWidth(0, 64)
		self.setColumnWidth(1, 110)
		self.setColumnWidth(2, 210)
		self.setColumnWidth(3, 280)
		self.setColumnWidth(4, 580)
		self.verticalHeader().hide()
		self.horizontalHeader().show()
		self.horizontalHeader().setHighlightSections(False)
		self.setHorizontalHeaderLabels(['Num', 'Address', 'Section', 'Data', 'Hex'])
		self.horizontalHeaderItem(0).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(1).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(2).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(3).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(4).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.setFont(ConfigClass.font)
		
		self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
		self.setShowGrid(False)
		self.cellDoubleClicked.connect(self.on_double_click)
		
	def on_double_click(self, row, col):
#		if col in range(3):
#			self.toggleBPOn(row)
##			self.sigBPOn.emit(self.item(self.selectedItems()[0].row(), 3).text(), self.item(self.selectedItems()[0].row(), 1).isBPOn)
		pass
			
	def contextMenuEvent(self, event):
#		for i in dir(event):
#			print(i)
#		print(event.pos())
#		print(self.itemAt(event.pos().x(), event.pos().y()))
#		print(self.selectedItems())
		self.context_menu.exec(event.globalPos())
		pass
		
	def resetContent(self):
		self.setRowCount(0)
#		for row in range(self.rowCount(), 0):
#			self.removeRow(row)
			
	def addRow(self, num, address, section, data, hexVal):
		currRowCount = self.rowCount()
		self.setRowCount(currRowCount + 1)
		self.addItem(currRowCount, 0, str(num))
		self.addItem(currRowCount, 1, str(address))
		self.addItem(currRowCount, 2, str(section))
		self.addItem(currRowCount, 3, str(data))
		self.addItem(currRowCount, 4, str(hexVal))
		self.setRowHeight(currRowCount, 18)
		
		
	def addItem(self, row, col, txt):
		item = QTableWidgetItem(txt, QTableWidgetItem.ItemType.Type)
		item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) #Qt.ItemFlag.ItemIsSelectable)
		
		# Insert the items into the row
		self.setItem(row, col, item)
		
		
class SearchWidget(QWidget):
		
	driver = None
	caseSensitive = True
	
	def __init__(self, driver):
		super().__init__()
		self.driver = driver
#		self.wdtSearchMain = QWidget()
		self.laySearchMain = QVBoxLayout()
		
		self.wdtSearchTop = QWidget()
		self.laySearchTop = QHBoxLayout()
		self.laySearchTop.addWidget(QLabel("Term:"))
		self.txtSearchTerm = QLineEdit()
		self.txtSearchTerm.setFixedWidth(300)
		self.txtSearchTerm.setText("Hello")
		self.txtSearchTerm.returnPressed.connect(self.click_search)
		self.laySearchTop.addWidget(self.txtSearchTerm)
		self.cmdSearch = QPushButton("Search")
		self.cmdSearch.clicked.connect(self.click_search)
		self.laySearchTop.addWidget(self.cmdSearch)
		self.laySearchTop.addWidget(QLabel("Type:"))
		self.cmbSearchType = QComboBox()
		self.cmbSearchType.addItems(["String", "Address", "Operand", "Data", "RegExp"])
		self.laySearchTop.addWidget(self.cmbSearchType)
		
		self.swtCaseSensitive = QSwitch("Case sensitive", SwitchSize.Small, SwitchLabelPos.Trailing)
		self.swtCaseSensitive.checked.connect(self.swtCaseSensitive_checked)
		self.swtCaseSensitive.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.swtCaseSensitive.setChecked(True)
		self.swtCaseSensitive.setContentsMargins(0, 0, 0, 0)
		self.laySearchTop.addWidget(self.swtCaseSensitive)
		
		self.laySearchTop.addStretch(1)
		self.wdtSearchTop.setLayout(self.laySearchTop)
		self.laySearchMain.addWidget(self.wdtSearchTop)
		self.table = SearchTableWidget()
		self.laySearchMain.addWidget(self.table)
		self.setLayout(self.laySearchMain)
#		self.tabWidgetDbg.addTab(self.wdtSearchMain, "Search")
		
	def swtCaseSensitive_checked(self, checked):
		self.caseSensitive = checked
		
	def click_search(self):
		self.table.resetContent()
		searchTerm = self.txtSearchTerm.text()
		print(f"Starting search for: '{searchTerm}' ...")
		chunk_size = 1024
		self.target = self.driver.getTarget()
		
		thread = self.target.GetProcess().GetSelectedThread()
		
		if self.cmbSearchType.currentText() == "RegExp":
			print(f'Searching with REGEXP!!!!')
#			target = lldb.debugger.GetSelectedTarget()
#			module = target.GetModuleAtIndex(0)  # Assuming the executable is the first module
#			base_address = module.GetObjectFileHeaderAddress().GetLoadAddress(target)
#			size = module.GetByteSize()
			
			pattern = re.compile(b"{searchTerm}")  # Compile the regex pattern
			matches = []
			
			chunk_size = 4096  # Adjust as needed for performance
			numFound = 0
			idxOuter = 0
			for module in self.target.module_iter():
				idx = 0
#				module = target.GetModuleAtIndex(0)  # Assuming the executable is the first module
				base_address = module.GetObjectFileHeaderAddress().GetLoadAddress(self.target)
				size = module.GetAddressByteSize()
				
				for address in range(base_address, base_address + size, chunk_size):
					data = self.target.ReadMemory(lldb.SBAddress(address, self.target), chunk_size, lldb.SBError())
					matches += pattern.findall(data)
			
			print(f'matches => {matches}')
#				for section in module.section_iter():
#					for subsec in section:
#						
#						address = subsec.GetLoadAddress(self.target)
#						remaining_bytes = subsec.GetByteSize()
#						
#						for address in range(base_address, base_address + size, chunk_size):
#							data = target.ReadMemory(address, chunk_size, lldb.SBError())
#							matches += pattern.findall(data)
							
#						while remaining_bytes > 0:
#							# Read a chunk of data
#							error = lldb.SBError()
#							data = self.target.ReadMemory(lldb.SBAddress(address, self.target), min(remaining_bytes, chunk_size), error)
#							if data == None:
#								break
#							
#							if self.caseSensitive:
#								ascii_string = searchTerm.encode("utf-8") # b"Hello"  # Replace with the actual string
#								string_index = data.find(ascii_string)
#							else:
#								ascii_string = searchTerm.encode("utf-8").lower() # b"Hello"  # Replace with the actual string
#								string_index = data.lower().find(ascii_string)
#								
#							if string_index != -1:
#								numFound += 1
#								end_index = data.find(b'\x00', string_index)
#								# Found the string!
#	#							print(f"Found string at address: {address + string_index} / {hex(address + string_index)} => {hex(address)} / {hex(string_index)} ===> {data}")
#								try:
#									self.table.addRow(str(numFound), hex(address + string_index), section.GetName() + "." + subsec.GetName(), data[string_index:end_index].decode(), self.bytearray_to_hex(data[string_index:end_index]))
#								except Exception as e:
#									print(f'Error while searching: {e}')
#	#							break  # Stop searching if found
#									
#							address += len(data)
#							remaining_bytes -= len(data)
#				idx += 1
#			idxOuter += 1
			
		else:
			print(f'Searching WITHOUT REGEXP!!!!')
			
			numFound = 0
			idxOuter = 0
			for module in self.target.module_iter():
				idx = 0
				for section in module.section_iter():
					for subsec in section:
						
						address = subsec.GetLoadAddress(self.target)
						remaining_bytes = subsec.GetByteSize()
						
						while remaining_bytes > 0:
							# Read a chunk of data
							error = lldb.SBError()
							data = self.target.ReadMemory(lldb.SBAddress(address, self.target), min(remaining_bytes, chunk_size), error)
							if data == None:
								break
							
							if self.caseSensitive:
								ascii_string = searchTerm.encode("utf-8") # b"Hello"  # Replace with the actual string
								string_index = data.find(ascii_string)
							else:
								ascii_string = searchTerm.encode("utf-8").lower() # b"Hello"  # Replace with the actual string
								string_index = data.lower().find(ascii_string)
							
							if string_index != -1:
								numFound += 1
								end_index = data.find(b'\x00', string_index)
								# Found the string!
	#							print(f"Found string at address: {address + string_index} / {hex(address + string_index)} => {hex(address)} / {hex(string_index)} ===> {data}")
								try:
									self.table.addRow(str(numFound), hex(address + string_index), section.GetName() + "." + subsec.GetName(), data[string_index:end_index].decode(), self.bytearray_to_hex(data[string_index:end_index]))
								except Exception as e:
									print(f'Error while searching: {e}')
	#							break  # Stop searching if found
							
							address += len(data)
							remaining_bytes -= len(data)
				idx += 1
			idxOuter += 1
		
	def bytearray_to_hex(self, byte_array):
#		return "{:02x}".format(byte_array)
#		"""Converts a byte array to a list of hex strings."""
		return ' '.join([f"{byte:02x}" for byte in byte_array])