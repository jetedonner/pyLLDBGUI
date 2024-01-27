#!/usr/bin/env python3

import lldb
import os
import sys
import re

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
	
	def handle_toggleBP(self):
		item = self.item(self.selectedItems()[0].row(), 1)
		item.toggleBPOn()
		pass
		
	def handle_disableBP(self):
		item = self.item(self.selectedItems()[0].row(), 1)
		item.toggleBPEnabled()
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
		actionCopyInstruction = self.context_menu.addAction("Copy instruction")
		actionCopyHex = self.context_menu.addAction("Copy hex value")
		self.context_menu.addSeparator()
		actionFindReferences = self.context_menu.addAction("Find references")
		
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
		self.horizontalHeaderItem(2).setTextAlignment(Qt.AlignmentFlag.AlignLeft)
		self.horizontalHeaderItem(3).setTextAlignment(Qt.AlignmentFlag.AlignLeft)
		self.horizontalHeaderItem(4).setTextAlignment(Qt.AlignmentFlag.AlignLeft)
		self.horizontalHeaderItem(5).setTextAlignment(Qt.AlignmentFlag.AlignLeft)
		self.horizontalHeaderItem(6).setTextAlignment(Qt.AlignmentFlag.AlignLeft)
		self.setFont(ConfigClass.font)
		
		self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
		self.setShowGrid(False)
		self.cellDoubleClicked.connect(self.on_double_click)
		
	def on_double_click(self, row, col):
		if col in range(3):
			self.toggleBPOn(row)
		
	def contextMenuEvent(self, event):
		for i in dir(event):
			print(i)
		print(event.pos())
		print(self.itemAt(event.pos().x(), event.pos().y()))
		print(self.selectedItems())
		self.context_menu.exec(event.globalPos())
	
	def toggleBPOn(self, row):
		item = self.item(row, 1)
		item.toggleBPOn()
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