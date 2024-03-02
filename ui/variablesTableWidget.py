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

from ui.editVariableDialog import *
from helper.variableHelper import *

class VariablesTableWidget(QTableWidget):
	
	ommitCellChanged = False
	
	def __init__(self):
		super().__init__()
		self.context_menu = QMenu(self)
		self.actionShowMemory = self.context_menu.addAction("Show Memory")
		self.actionShowMemory.triggered.connect(self.handle_showMemory)
		self.actionEditValue = self.context_menu.addAction("Edit variable value")
		self.actionEditValue.triggered.connect(self.handle_editValue)
#		actionToggleBP = self.context_menu.addAction("Toggle Breakpoint")
#		actionToggleBP.triggered.connect(self.handle_toggleBP)
#		actionDisableBP = self.context_menu.addAction("Enable / Disable Breakpoint")
#		actionDisableBP.triggered.connect(self.handle_disableBP)
#		
#		self.context_menu.addSeparator()
		
		self.setColumnCount(5)
		self.setColumnWidth(0, 196)
		self.setColumnWidth(1, 196)
		self.setColumnWidth(2, 196)
		self.setColumnWidth(3, 196)
		self.setColumnWidth(4, 450)
		self.verticalHeader().hide()
		self.horizontalHeader().show()
		self.horizontalHeader().setHighlightSections(False)
		self.setHorizontalHeaderLabels(['Name', 'Value', 'Type', 'Address', 'Data'])
		
		self.horizontalHeaderItem(0).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(1).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(2).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(3).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(4).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.setFont(ConfigClass.font)
		
		self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
		self.setShowGrid(False)
		self.cellDoubleClicked.connect(self.on_double_click)
		self.cellChanged.connect(self.item_changed_handler)
		
	def on_double_click(self, row, col):
		if col == 3:
			if self.item(row, col) != None:
				item = self.item(row, col)
				self.window().updateStatusBar(f"Showing memory for variable '{self.item(row, 0).text()}' at address: {item.text()}")
				self.window().doReadMemory(int(item.text(), 16))
		
#	def doReadMemory(self, address, size = 0x100):
#		self.window().tabWidgetDbg.setCurrentWidget(self.window().tabMemory)
#		self.window().tblHex.txtMemAddr.setText(hex(address))
#		self.window().tblHex.txtMemSize.setText(hex(size))
#		try:
##           global debugger
##			self.handle_readMemory(self.driver.debugger, int(self.window().tblHex.txtMemAddr.text(), 16), int(self.window().tblHex.txtMemSize.text(), 16))
#			self.window().tblHex.handle_readMemory(self.window().driver.debugger, int(self.window().tblHex.txtMemAddr.text(), 16), int(self.window().tblHex.txtMemSize.text(), 16))
#		except Exception as e:
#			print(f"Error while reading memory from process: {e}")
			
	def contextMenuEvent(self, event):
#		for i in dir(event):
#			print(i)
#		print(event.pos())
#		print(self.itemAt(event.pos().x(), event.pos().y()))
#		print(self.selectedItems())
		self.context_menu.exec(event.globalPos())
		
	def handle_editValue(self):
		item = self.item(self.selectedItems()[0].row(), 0)
		print(f'Editing Value For: {item.text()}')
		
		# Get the frame object from the current debugging session
		frame = self.window().driver.getTarget().GetProcess().GetThreadAtIndex(0).GetFrameAtIndex(0)
		
		# Get the variable you want to modify by name
		variable = frame.FindVariable(item.text())
		# Check if the variable was found
		if variable.IsValid():
			
			if EditVariableDialog(variable).exec():
				# Get the variable's type using GetType()
#				variable_type = variable.GetType()
#			
#				val = lldb.SBValue()
#				valNew = val.CreateValueFromData(item.text(), lldb.SBData().CreateDataFromSInt32Array(lldb.eByteOrderLittle, 0x1, [0xa]), variable_type)
#				# Create an SBValue corresponding to the new value and data type
#	#			new_value_object = variable_type.MakeDataValue(321)
#				
#				# Update the variable's value using SetData()
#				error = lldb.SBError()
#				variable.SetData(lldb.SBData().CreateDataFromSInt32Array(lldb.eByteOrderLittle, 0x1, [0xa]), error)
#				if error == None:
#					successMsg = f"Variable '{item.text()}' with type: '{variable_type}' updated to: {variable.GetValue()}"
#	#				print(successMsg)
#					self.window().updateStatusBar(successMsg)
#				else:
#					print(f"ERROR: {error}")
				pass
		else:
			print("Variable not found.")
		
		pass
		
	def handle_showMemory(self):
		item = self.item(self.selectedItems()[0].row(), 3)
		print(f'SHOWING MEM For: {item.text()}')
		self.window().doReadMemory(int(item.text(), 16))
		pass
		
	def resetContent(self):
		self.setRowCount(0)
#		for row in range(self.rowCount(), 0):
#			self.removeRow(row)
	
	def updateRow(self, name, value, datatype, address, data):
		self.ommitCellChanged = True
		for i in range(self.rowCount()):
			if self.item(i, 0).text() == name:
				self.item(i, 1).setText(value)
				self.item(i, 2).setText(datatype)
				self.item(i, 3).setText(address)
				self.item(i, 4).setText(data)
				break
		self.ommitCellChanged = False
		
	def addRow(self, name, value, datatype, address, data):
		self.ommitCellChanged = True
		currRowCount = self.rowCount()
		self.setRowCount(currRowCount + 1)
		self.addItem(currRowCount, 0, str(name))
		self.addItem(currRowCount, 1, str(value), True if str(datatype) == "int" else False)
		self.addItem(currRowCount, 2, str(datatype))
		self.addItem(currRowCount, 3, str(address))
		self.addItem(currRowCount, 4, str(data), True if str(datatype) == "int" else False)
		self.setRowHeight(currRowCount, 18)
		self.ommitCellChanged = False
		
	def addItem(self, row, col, txt, editable = False):
		item = QTableWidgetItem(txt, QTableWidgetItem.ItemType.Type)
		if not editable: # or (col != 1 and col != 2):
			item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) #Qt.ItemFlag.ItemIsSelectable)
		
		# Insert the items into the row
		self.setItem(row, col, item)
	
	def item_changed_handler(self, row, col):
#		print(f"item_changed_handler => row: {row} / col: {col}")
		if not self.ommitCellChanged:
			if self.item(row, 2).text() == "int":
				if col == 1: #  or col == 2 or col == 2
					changedItem = self.item(row, col)
#					print(f"Item changed: {row} / {col} => NewVal: {changedItem.text()}")
					newVal = ''
					if col == 1:
						varName = self.item(row, 0).text()
						newVal = self.item(row, 1).text()
						if newVal.lower().startswith("0x"):
							newVal = int(newVal, 16)
						else:
							newVal = int(newVal)
						# Get the frame object from the current debugging session
#						frame = self.window().driver.getTarget().GetProcess().GetThreadAtIndex(0).GetFrameAtIndex(0)
#						
#						# Get the variable you want to modify by name
#						var = frame.FindVariable(varName)
#						var = VariablesHelper.GetVariable(self.window().driver, varName)
						
						if VariablesHelper.SetVariableDataInt(self.window().driver, varName, newVal):
							self.item(row, 4).setText(hex(newVal))
							self.item(row, 1).setText(str(newVal))
						
#						self.variable_type = var.GetType()
#						print(f"self.variable_type => {self.variable_type}")
#						
#						value = str(var.GetValue())
#						
#						error = lldb.SBError()
#						if self.variable_type.GetBasicType() == lldb.eBasicTypeInt:
#							var.SetData(lldb.SBData().CreateDataFromSInt32Array(lldb.eByteOrderLittle, var.GetByteSize(), [int(self.item(row, 1).text())]), error)
##						elif str(self.variable_type).startswith("char"):
##							self.variable.SetData(lldb.SBData().CreateDataFromCString(lldb.eByteOrderLittle, int(self.txtSize.text(), 16), self.txtValue.text()), error)
##							
##							pass
#							
#						if error.Success():
#							successMsg = f"Variable '{varName}' with type: '{self.variable_type}' ('{self.variable_type.GetBasicType()}') updated to: {self.item(row, 1).text()}"
#							print(successMsg)
#							self.window().updateStatusBar(successMsg)
#						#			self.window().updateStatusBar(successMsg)
#						else:
#							print(f"ERROR: {error}")
#						newVal = int(changedItem.text())
#						self.item(row, 1).setText(hex(newVal))
#					else:
#						newVal = int(changedItem.text(), 16)
#						self.item(row, 1).setText(str(newVal))
					
#					varName = self.item(row, 0).text()
#					self.window().driver.handleCommand(f"expr {varName}={newVal}")
#					self.window().updateStatusBar(f"Updated value of variable '{varName}' to '{newVal}'")