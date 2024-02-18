#!/usr/bin/env python3

import array
import enum
# from enum import StrEnum

# import enum

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

#from helper import *

#from QSwitch import *
from config import *

import re

class HexGroups(enum.Enum):
	NoGrouping = ("No Grouping", 1) #"No grouping"
	TwoChars = ("Two", 2) #"Two characters"
	FourChars = ("Four", 4) #"Four characters"
	EightChars = ("Eight", 8) #"Four characters"
	
class TransparentLineEdit(QLineEdit):
	
	item_sel_changed = pyqtSignal(object, object)
	
	parent_item = None
	def __init__(self, parent=None, parent_item=None):
		super().__init__(parent)
		self.parent_item = parent_item
#		self.setParent(parent)
		self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.selectionChanged.connect(self.transparentLineEdit_selectionchanged)
		
	def paintEvent(self, event):
		painter = QPainter(self)
		painter.fillRect(event.rect(), Qt.GlobalColor.transparent)
		super().paintEvent(event)
		
	def transparentLineEdit_selectionchanged(self):
#		cursor = self.cursor()
		print("TransparentLineEdit Selection start: %d end: %d" % (self.selectionStart(), self.selectionEnd()))
		self.item_sel_changed.emit(self.parent_item, self)
		
		pass
		
		
class QHexTableWidget(QTableWidget):
	
	def __init__(self, parent=None):
		QTableWidget.__init__(self, parent=parent)
		
#		self.context_menu = QMenu(self)
#		actionToggleBP = self.context_menu.addAction("Toggle Breakpoint")
#		actionToggleBP.triggered.connect(self.handle_toggleBP)
#		actionDisableBP = self.context_menu.addAction("Enable / Disable Breakpoint")
#		actionDisableBP.triggered.connect(self.handle_disableBP)
#		
#		self.context_menu.addSeparator()
		
		self.setColumnCount(3)
		self.setColumnWidth(0, 128)
		self.setColumnWidth(1, 512)
		self.setColumnWidth(2, 512)
		self.verticalHeader().hide()
		self.horizontalHeader().show()
		self.horizontalHeader().setHighlightSections(False)
		self.setHorizontalHeaderLabels(['Address', 'Hex-Value', 'Raw-Data'])
		self.horizontalHeaderItem(0).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(1).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.horizontalHeaderItem(2).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
		self.setFont(ConfigClass.font)
		
		self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
		self.setShowGrid(False)
#		self.cellDoubleClicked.connect(self.on_double_click)
		
		
	def resetContent(self):
#		for row in range(self.rowCount(), 0):
#			self.removeRow(row)
		self.setRowCount(0)
		print(f'ROWCOUNT AFTER RESET {self.rowCount()}')
			
	def addRow(self, address, value, raw):
		currRowCount = self.rowCount()
		
		if currRowCount == 0:
			self.setRowCount(currRowCount + 1)
			self.txtAddr = QTextEdit()
			self.txtAddr.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
			self.txtAddr.setText(address)
			self.setCellWidget(currRowCount, 0, self.txtAddr)
			
			self.txtHex = QTextEdit()
			self.txtHex.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
			self.txtHex.setText(value)
			self.setCellWidget(currRowCount, 1, self.txtHex)
			
			self.txtData = QTextEdit()
			self.txtData.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
			self.txtData.setText(raw)
			self.setCellWidget(currRowCount, 2, self.txtData)
		else:
			self.txtAddr.append(address)
			self.txtHex.append(value)
			self.txtData.append(raw)
			
#		self.setRowCount(currRowCount + 1)
#		self.addItem(currRowCount, 0, str(address))
#		
##		item1 = EditableItem(str(value))
##		item2 = EditableItem(str(raw))
##		self.setItem(currRowCount, 1, item1)
##		self.setItem(currRowCount, 2, item2)
#		
##		self.Table.setCellWidget(row, column, widget
#		itemA = QTableWidgetItem()
#		item1 = TransparentLineEdit(None, itemA)
#		item1.setText(str(value))
#		item1.setFont(ConfigClass.font)
#		item1.setStyleSheet("background-color: transparent; border: none;")
#		item1.item_sel_changed.connect(self.handle_selectionChanged)
#
##		custom_widget = CustomCellWidget(item)
#		self.setItem(currRowCount, 1, itemA)
#		self.setCellWidget(currRowCount, 1, item1)
#	
#		itemB = QTableWidgetItem()
#		item2 = TransparentLineEdit(None, itemB)
#		item2.setText(str(raw))
#		item2.setFont(ConfigClass.font)
#		item2.setStyleSheet("background-color: transparent; border: none;")
#		
#		self.setItem(currRowCount, 2, itemB)
#		self.setCellWidget(currRowCount, 2, item2)

		
#		self.setCellWidget(currRowCount, 1, item1)
#		self.setCellWidget(currRowCount, 2, item2)
#		self.addItem(currRowCount, 1, str(value))
#		self.addItem(currRowCount, 2, str(raw))
		self.setRowHeight(currRowCount, self.get_required_row_height(self.txtAddr, self.height()))
		
		
	
	def get_required_height(self, text_edit):
		total_height = 0
		cursor = text_edit.textCursor()
		cursor.movePosition(QTextCursor.MoveOperation.Start)
		while cursor.hasSelection():
			block_format = cursor.blockFormat()
			total_height += block_format.height()
			cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
#		print(f'total_height: {total_height}')
		return total_height - text_edit.verticalScrollBar().height() - text_edit.frameWidth() * 2  # Adjust for margins and padding
	
	def get_required_row_height(self, text_edit, minimum_row_height):
		content_height = self.get_required_height(text_edit)  # Use your previous method
		cell_padding = 5  # Adjust based on your widget properties
		return max(content_height + cell_padding, minimum_row_height)
	
	def handle_selectionChanged(self, tableWidget, item):
		print(f"Item changed: {self.row(tableWidget)} {item.selectionStart()} / {item.selectionEnd()}")
		print(self.cellWidget(self.row(tableWidget), 2).text())
		self.cellWidget(self.row(tableWidget), 2).setSelection((item.selectionStart()/3), ((item.selectionEnd()+1)/3))
	
	def addItem(self, row, col, txt):
		item = QTableWidgetItem(txt, QTableWidgetItem.ItemType.Type)
		if col == 0:
			item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) #Qt.ItemFlag.ItemIsSelectable)
		
		# Insert the items into the row
		self.setItem(row, col, item)