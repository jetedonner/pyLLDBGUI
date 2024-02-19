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

class ByteGrouping(enum.Enum):
	NoGrouping = ("No Grouping", 1) #"No grouping"
	TwoChars = ("Two", 2) #"Two characters"
	FourChars = ("Four", 4) #"Four characters"
	EightChars = ("Eight", 8) #"Four characters"
	
class MyTextEdit(QTextEdit):
	def __init__(self, parent=None):
		super().__init__(parent)
#		self.line_height = 20  # Set desired line height
#		cursor = self.textCursor()
#		if cursor.block():
#			block_format = cursor.blockFormat()
#			block_format.setLineHeight(30, 2)
			
#	def paintEvent(self, event):
#		painter = QPainter(self)
#		cursor = self.textCursor()
#		while cursor.block():
#			block_format = cursor.blockFormat()
#			block_format.setLineHeight(20, 2)
##			rect = self.cursorRect(cursor)
##			y = rect.top()
##			for j in range(block_format.length()):
##				painter.drawText(rect.left(), y, cursor.charAt(j))
##				y += self.line_height
##			cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
			
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
#		print(f'Reloading BPs {self.rowCount()}')
			
	def addRow(self, address, value, raw):
		currRowCount = self.rowCount()
		
		if currRowCount == 0:
			self.line_height = 30  # Set desired line height
			
			self.setRowCount(currRowCount + 1)
			self.txtAddr = MyTextEdit()
			self.txtAddr.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
			self.txtAddr.setText(address)
#			self.txtAddr.setStyleSheet("QTextEdit { paragraph-spacing: 20px; }")
#			self.txtAddr.setStyleSheet("MyTextEdit { line-height: 3.5; }")
			self.txtAddr.setFont(ConfigClass.font)
			
			blockFmt = QTextBlockFormat()
			blockFmt.setLineHeight(150, 1)
			
			theCursor = self.txtAddr.textCursor()
			theCursor.clearSelection()
			theCursor.select(QTextCursor.SelectionType.Document)
			theCursor.mergeBlockFormat(blockFmt)
			
			self.setCellWidget(currRowCount, 0, self.txtAddr)
#			cursor = self.txtAddr.textCursor()
#			if cursor.block():
#				block_format = cursor.blockFormat()
#				block_format.setLineHeight(self.line_height, 2)
			
			self.txtHex = MyTextEdit()
			self.txtHex.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
			self.txtHex.setText(value)
#			self.txtHex.setStyleSheet("QTextEdit { paragraph-spacing: 20px; }")
#			self.txtHex.setStyleSheet("MyTextEdit { line-height: 3.5; }")
			
			self.txtHex.setFont(ConfigClass.font)
			self.txtHex.setStyleSheet("selection-background-color: #ff0000;")
#			self.txtHex.setStyleSheet("line-height: 13.5;")
			
			theCursor2 = self.txtHex.textCursor()
			theCursor2.clearSelection()
			theCursor2.select(QTextCursor.SelectionType.Document)
			theCursor2.mergeBlockFormat(blockFmt)
			self.txtHex.selectionChanged.connect(self.txtHex_selectionchanged)
			self.setCellWidget(currRowCount, 1, self.txtHex)
#			cursor = self.txtHex.textCursor()
#			if cursor.block():
#				block_format = cursor.blockFormat()
#				block_format.setLineHeight(self.line_height, 2)
			
			self.txtData = MyTextEdit()
			self.txtData.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
			self.txtData.setText(raw)
#			self.txtData.setStyleSheet("MyTextEdit { line-height: 3.5; }")
			self.txtData.setFont(ConfigClass.font)
			self.txtData.setStyleSheet("selection-background-color: #ff0000;")
			
#			theCursor3 = self.txtData.textCursor()
#			theCursor3.clearSelection()
#			theCursor3.select(QTextCursor.SelectionType.Document)
#			theCursor3.mergeBlockFormat(blockFmt)
			self.txtData.selectionChanged.connect(self.txtData_selectionchanged)
			self.setCellWidget(currRowCount, 2, self.txtData)
#			cursor = self.txtData.textCursor()
#			if cursor.block():
#				block_format = cursor.blockFormat()
#				block_format.setLineHeight(self.line_height, 2)
			
			self.txtAddr.verticalScrollBar().valueChanged.connect(self.handle_scroll_change)	
			self.txtHex.verticalScrollBar().valueChanged.connect(self.handle_scroll_change)	
			self.txtData.verticalScrollBar().valueChanged.connect(self.handle_scroll_change)	
			
#			reference_line_height = self.txtData.textCursor().blockFormat().lineHeight(20)  # Get reference line height
#			stylesheet = self.create_line_height_stylesheet(reference_line_height)
#			self.txtHex.setStyleSheet(stylesheet)
			
#			self.synchronize_scroll(self.txtAddr, self.txtHex)
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
	
	def create_line_height_stylesheet(self, reference_line_height):
		stylesheet = ""
		# Loop through lines in the second text edit
		for line_index, line in enumerate(self.txtData.toPlainText().splitlines()):
			# Calculate desired font size or spacing based on reference line height
			# Adjust stylesheet rulesaa as needed (e.g., using line numbers or custom markers)
			stylesheet += f":global(.QTextEdit) line[{line_index}] {{ font-size: {reference_line_height * 1.2}px; }}"  # Example font size adjustment
		return stylesheet
	
#	def synchronize_scroll(self, widget1, widget2):
	def handle_scroll_change(self, value):
		self.txtAddr.verticalScrollBar().setValue(value)
		self.txtHex.verticalScrollBar().setValue(value)
		self.txtData.verticalScrollBar().setValue(value)
			
#		widget1.verticalScrollBar().valueChanged.connect(handle_scroll_change)	
	
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
#		print(f"Item changed: {self.row(tableWidget)} {item.selectionStart()} / {item.selectionEnd()}")
#		print(self.cellWidget(self.row(tableWidget), 2).text())
#		self.cellWidget(self.row(tableWidget), 2).setSelection((item.selectionStart()/3), ((item.selectionEnd()+1)/3))
		cursor = self.textCursor()
		pass
	
	def addItem(self, row, col, txt):
		item = QTableWidgetItem(txt, QTableWidgetItem.ItemType.Type)
		if col == 0:
			item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) #Qt.ItemFlag.ItemIsSelectable)
		
		# Insert the items into the row
		self.setItem(row, col, item)
		
	updateHexSel = True
	updateSel = True
	
	def txtHex_selectionchanged(self):
		if not self.updateHexSel and not self.updateTxt:
			return
		
		cursorHex = self.txtHex.textCursor()
		print("txtHex Selection start: %d end: %d" % (cursorHex.selectionStart(), cursorHex.selectionEnd()))
		
		cursorData = self.txtData.textCursor()
		cursorData.clearSelection()
		txtLen = len(self.txtData.toPlainText())
#		cursor = self.txtHex.textCursor()
		print("txtData Selection start: %d end: %d" % (cursorData.selectionStart(), cursorData.selectionEnd()))
		startPos = int(cursorHex.selectionStart() / 3)
		if startPos > txtLen:
			startPos -= 1
		cursorData.setPosition(startPos)
		endPos = int((cursorHex.selectionEnd() + 1) / 3)
		if endPos > txtLen:
			endPos -= 1
		print(f"txtLen = {txtLen}")
		cursorData.setPosition(endPos, QTextCursor.MoveMode.KeepAnchor)
		print("txtData Selection start: %d end: %d" % (startPos, endPos))
		self.updateHexSel = False
		self.updateSel = False
		self.txtData.setTextCursor(cursorData)
		self.updateHexSel = True
		self.updateSel = True
		self.txtData.ensureCursorVisible()
		
	updateTxt = True
	updateHexTxt = True
	
	def txtData_selectionchanged(self):
		if not self.updateSel and not self.updateTxt:
			return
		cursorData = self.txtData.textCursor()
		print("txtData Selection start: %d end: %d" % (cursorData.selectionStart(), cursorData.selectionEnd()))
		
		cursorHex = self.txtHex.textCursor()
		cursorHex.clearSelection()
		txtLen = len(self.txtHex.toPlainText())
		startPos = (cursorData.selectionStart() * 3)
		if startPos > txtLen:
			startPos -= 1
		cursorHex.setPosition(startPos)
		endPos = (cursorData.selectionEnd() * 3) - 1
		if endPos > txtLen:
			endPos -= 1
		print(f"txtLen = {txtLen}")
		cursorHex.setPosition(endPos, QTextCursor.MoveMode.KeepAnchor)
		self.updateTxt = False
		self.updateHexTxt = False
		self.txtHex.setTextCursor(cursorHex)
		self.updateTxt = True
		self.updateHexTxt = True
		self.txtHex.ensureCursorVisible()
		