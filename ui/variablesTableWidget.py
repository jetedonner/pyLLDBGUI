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

class VariablesTableWidget(QTableWidget):
	
	ommitCellChanged = False
	
	def __init__(self):
		super().__init__()
		self.context_menu = QMenu(self)
		actionShowMemory = self.context_menu.addAction("Show Memory")
		actionShowMemory.triggered.connect(self.handle_showMemory)
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
		
	def handle_showMemory(self):
		item = self.item(self.selectedItems()[0].row(), 3)
		print(f'SHOWING MEM For: {item.text()}')
		self.window().doReadMemory(int(item.text(), 16))
		pass
		
	def resetContent(self):
		for row in range(self.rowCount(), 0):
			self.removeRow(row)
	
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
		if not self.ommitCellChanged:
			if self.item(row, 3).text() == "int":
				if col == 1 or col == 2:
					changedItem = self.item(row, col)
#					print(f"Item changed: {row} / {col} => NewVal: {changedItem.text()}")
					newVal = 0
					if col == 1:
						newVal = int(changedItem.text())
						self.item(row, 2).setText(hex(newVal))
					else:
						newVal = int(changedItem.text(), 16)
						self.item(row, 1).setText(str(newVal))
					
					varName = self.item(row, 0).text()
					self.window().driver.handleCommand(f"expr {varName}={newVal}")
					self.window().updateStatusBar(f"Updated value of variable '{varName}' to '{newVal}'")