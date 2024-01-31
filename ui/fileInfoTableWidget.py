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

class FileInfosTableWidget(QTableWidget):
	
#	sigEnableBP = pyqtSignal(str, bool)
#	sigBPOn = pyqtSignal(str, bool)
#	
#	actionShowMemory = None
	
#	def handle_copyHexValue(self):
#		item = self.item(self.selectedItems()[0].row(), 5)
#		pyperclip.copy(item.text())
#		
#	def handle_copyInstruction(self):
#		item = self.item(self.selectedItems()[0].row(), 4)
#		pyperclip.copy(item.text())
#		
#	def handle_copyAddress(self):
#		item = self.item(self.selectedItems()[0].row(), 3)
#		pyperclip.copy(item.text())
##		clipboard_contents = pyperclip.paste()
##		print(clipboard_contents)
##		pass
#		
#	def handle_toggleBP(self):
#		item = self.item(self.selectedItems()[0].row(), 1)
#		item.toggleBPOn()
#		self.sigBPOn.emit(self.item(self.selectedItems()[0].row(), 3).text(), item.isBPOn)
#		pass
#		
#	def handle_disableBP(self):
#		item = self.item(self.selectedItems()[0].row(), 1)
#		item.toggleBPEnabled()
#		self.sigEnableBP.emit(self.item(self.selectedItems()[0].row(), 3).text(), not item.isBPEnabled)
#		pass
		
	def __init__(self):
		super().__init__()
		self.context_menu = QMenu(self)
#		actionToggleBP = self.context_menu.addAction("Toggle Breakpoint")
#		actionToggleBP.triggered.connect(self.handle_toggleBP)
#		actionDisableBP = self.context_menu.addAction("Enable / Disable Breakpoint")
#		actionDisableBP.triggered.connect(self.handle_disableBP)
#		
#		self.context_menu.addSeparator()
#		actionCopyAddress = self.context_menu.addAction("Copy address")
#		actionCopyAddress.triggered.connect(self.handle_copyAddress)
#		actionCopyInstruction = self.context_menu.addAction("Copy instruction")
#		actionCopyInstruction.triggered.connect(self.handle_copyInstruction)
#		actionCopyHex = self.context_menu.addAction("Copy hex value")
#		actionCopyHex.triggered.connect(self.handle_copyHexValue)
#		self.context_menu.addSeparator()
#		actionFindReferences = self.context_menu.addAction("Find references")
#		self.actionShowMemory = self.context_menu.addAction("Show memory")
		
		self.setColumnCount(2)
		self.setColumnWidth(0, 128)
		self.setColumnWidth(1, 256)
#		self.setColumnWidth(2, 72)
#		self.setColumnWidth(3, 108)
#		self.setColumnWidth(4, 256)
#		self.setColumnWidth(5, 324)
#		self.setColumnWidth(6, 304)
		self.verticalHeader().hide()
		self.horizontalHeader().show()
		self.setHorizontalHeaderLabels(['Key', 'Value']) #, '#', 'Address', 'Instruction', 'Hex', 'Comment'])
		self.horizontalHeaderItem(0).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
#		self.horizontalHeaderItem(2).setFont(ConfigClass.font)
		self.horizontalHeaderItem(1).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
##		self.horizontalHeaderItem(3).setFont(ConfigClass.font)
#		self.horizontalHeaderItem(4).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
##		self.horizontalHeaderItem(4).setFont(ConfigClass.font)
#		self.horizontalHeaderItem(5).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
##		self.horizontalHeaderItem(5).setFont(ConfigClass.font)
#		self.horizontalHeaderItem(6).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
##		self.horizontalHeaderItem(6).setFont(ConfigClass.font)
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
#		self.context_menu.exec(event.globalPos())
		pass
		
#	def toggleBPOn(self, row):
##		print(f'TOGGLE BP: {self.item(row, 3).text()}')
#		item = self.item(row, 1)
#		item.toggleBPOn()
#		self.sigBPOn.emit(self.item(row, 3).text(), item.isBPOn)
#		pass
#		
#	def toggleBPAtAddress(self, address):
##		self.txtMultiline
##		print(f'CHECKING BREAKPOINT ROW-COUNT: {self.rowCount()}')
#		for row in range(self.rowCount()):
##			print(f'CHECKING BREAKPOINT AT ADDRESS: {self.item(row, 3).text()}')
#			if self.item(row, 3).text() == address:
#				self.toggleBPOn(row)
#				break
#		pass
		
	def resetContent(self):
		for row in range(self.rowCount(), 0):
			self.removeRow(row)
			
	def addRow(self, key, value): #, instr, comment, data, rip = ""):
		currRowCount = self.rowCount()
		self.setRowCount(currRowCount + 1)
		
#		item = DisassemblyImageTableWidgetItem()
#		
#		self.addItem(currRowCount, 0, ('>' if rip == address else ''))
		self.addItem(currRowCount, 0, str(key))
		self.addItem(currRowCount, 1, str(value))
#		self.addItem(currRowCount, 3, address)
#		self.addItem(currRowCount, 4, instr)
#		self.addItem(currRowCount, 5, data)
#		self.addItem(currRowCount, 6, comment)
		
		self.setRowHeight(currRowCount, 18)
		
		
	def addItem(self, row, col, txt):
		item = QTableWidgetItem(txt, QTableWidgetItem.ItemType.Type)
		item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) #Qt.ItemFlag.ItemIsSelectable)
		
		# Insert the items into the row
		self.setItem(row, col, item)