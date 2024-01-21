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

class DisassemblyLineNumTextEdit(QTextEdit):
	
	def __init__(self):
		super().__init__()
		self.context_menu = QMenu(self)
		actionCopyAddress = self.context_menu.addAction("Copy address")
		actionCopyInstruction = self.context_menu.addAction("Copy instruction")
		actionCopyHex = self.context_menu.addAction("Copy hex value")
		self.context_menu.addSeparator()
		actionFindReferences = self.context_menu.addAction("Find references")
#		self.context_menu.addSeparator()
#		actionCopyAddress = self.context_menu.addAction("Find references")
	
	def mouseDoubleClickEvent(self, event):
#		event.position
		for fun in dir(event):
			print(fun)
		print(f"Double click: {event.position()}")
		cursor = self.cursorForPosition(event.pos())
		
		print(cursor.selectedText())
		
	def paintEvent(self, event):
#		painter = QPainter(self.viewport())
#		painter.drawLine(10, 10, 200, 10)
		path = QPainterPath()
#		path.moveTo(50, 50)
#		path.arcTo(40, 40, 10, 10, 0, 270)
		path.moveTo(25, 25);
		path.arcTo(20, 20, 10, 10, 0, 360);
		path.closeSubpath()
		
		# Create a QPainter and attach it to the textEdit
		painter = QPainter(self.viewport())
		
		# Set the painter's pen and brush
		pen = QPen(Qt.GlobalColor.red, 2)
		brush = QBrush(Qt.GlobalColor.red)
		painter.setPen(pen)
		painter.setBrush(brush)
		
#		painter.begin(self)  # Capture painter's actions
		# Paint the circle
		painter.drawPath(path)
		
		# Release the painter
		painter.end()
		
		super(DisassemblyLineNumTextEdit, self).paintEvent(event)
		
	def contextMenuEvent(self, event):
		self.context_menu.exec(event.globalPos())
		
class DisassemblyTextEdit(QTextEdit):
	
	def __init__(self):
		super().__init__()
		self.context_menu = QMenu(self)
		actionCopyAddress = self.context_menu.addAction("Copy address")
		actionCopyInstruction = self.context_menu.addAction("Copy instruction")
		actionCopyHex = self.context_menu.addAction("Copy hex value")
		self.context_menu.addSeparator()
		actionFindReferences = self.context_menu.addAction("Find references")

	def contextMenuEvent(self, event):
		self.context_menu.exec(event.globalPos())
		
class DisassemblyImageTableWidgetItem(QTableWidgetItem):
	
	iconStd = None
	iconBPEnabled = None
	iconBPDisabled = None
	
	isBPOn = False
	isBPEnabled = False
	
	def __init__(self):
		self.iconStd = QIcon()
		super().__init__(self.iconStd, "", QTableWidgetItem.ItemType.Type)
		self.iconBPEnabled = QIcon(os.path.join("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/resources/", 'bug.png'))
		self.iconBPDisabled = QIcon(os.path.join("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/resources/", 'bug_bw_greyscale.png'))
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
		item = self.item(self.selectedItems()[0].row(), 0)
		item.toggleBPOn()
		pass
		
	def handle_disableBP(self):
		item = self.item(self.selectedItems()[0].row(), 0)
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
		
		self.setColumnCount(5)
		self.setColumnWidth(0, 32)
		self.setColumnWidth(1, 72)
		self.setColumnWidth(2, 108)
		self.setColumnWidth(3, 256)
		self.setColumnWidth(4, 512)
		self.verticalHeader().hide()
		self.horizontalHeader().hide()
		self.setFont(ConfigClass.font)
		
		self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
		self.setShowGrid(False)
		self.cellDoubleClicked.connect(self.on_double_click)
		
	def on_double_click(self, row, col):
		if col == 0:
			print(f"Double clicked at row {row} and column {col}")
			self.toggleBPOn(row)
		
	def contextMenuEvent(self, event):
		for i in dir(event):
			print(i)
		print(event.pos())
		print(self.itemAt(event.pos().x(), event.pos().y()))
		print(self.selectedItems())
		self.context_menu.exec(event.globalPos())
	
	def toggleBPOn(self, row):
		item = self.item(row, 0)
		item.toggleBPOn()
		pass
	
	def resetContent(self):
		for row in range(self.rowCount(), 0):
			self.removeRow(row)
			
	def addRow(self, lineNum, address, instr, comment):
		currRowCount = self.rowCount()
		self.setRowCount(currRowCount + 1)

		item = DisassemblyImageTableWidgetItem()
		
		self.setItem(currRowCount, 0, item)
		self.addItem(currRowCount, 1, str(lineNum) + ":")
		self.addItem(currRowCount, 2, address)
		self.addItem(currRowCount, 3, instr)
		self.addItem(currRowCount, 4, comment)
		
		self.setRowHeight(currRowCount, 18)
		
		
	def addItem(self, row, col, txt):
		item = QTableWidgetItem(txt, QTableWidgetItem.ItemType.Type)
		item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable) #Qt.ItemFlag.ItemIsSelectable)
		
		# Insert the items into the row
		self.setItem(row, col, item)
		
class AssemblerTextEdit(QWidget):
	
#	lineCount = 0
	lineCountNG = 0
	
	def clear(self):
#		self.txtCode.clear()
#		self.txtLineCount.clear()
#		self.lineCount = 0
		self.lineCountNG = 0
		self.table.resetContent()
		pass
	
	def appendAsmTextNG(self, addr, instr, comment, addLineNum = True):
#		self.txtCode.append(txt)
		if addLineNum:
			self.lineCountNG += 1
#			self.txtLineCount.append(str(self.lineCount) + ":")
			self.table.addRow(self.lineCountNG, addr, instr, comment)
		else:
			self.table.addRow(0, addr, instr, comment)
#			self.txtLineCount.append(" ")
#			print("addLineNum IS FALSE")
			
#	def appendAsmText(self, txt, addLineNum = True):
#		self.txtCode.append(txt)
#		if addLineNum:
#			self.lineCount += 1
#			self.txtLineCount.append(str(self.lineCount) + ":")
##			self.table.addRow(self.lineCount, txt, "", "")
#		else:
#			self.txtLineCount.append(" ")
##			print("addLineNum IS FALSE")
#			
#	def insertText(self, txt, bold = False, color = "black"):
#		cursor = self.txtCode.textCursor()
#		
#		if bold:
#			boldFormat = QTextCharFormat()
#			boldFormat.setFontWeight(QFont.Weight.Bold)
#			# Merge the bold format with the text cursor
#			cursor.mergeCharFormat(boldFormat)
#
#		# Insert the substring
#		cursor.insertText(txt)
#		# Move the cursor to the end of the paragraph
#		cursor.movePosition(QTextCursor.MoveOperation.EndOfLine)
#		
#		if bold:
#			normalFormat = QTextCharFormat()
#			normalFormat.setFontWeight(QFont.Weight.Normal)
#			# Merge the normal format with the text cursor
#			cursor.mergeCharFormat(normalFormat)
#		
#		# Append the substring to the QTextEdit
#		self.txtCode.setTextColor(QColor(color))
#		self.txtCode.setTextCursor(cursor)
#		
#		self.txtLineCount.insertPlainText(" ")
	
	
	def setTextColor(self, color = "black", lineNum = False):
#		if lineNum:
#			self.txtLineCount.setTextColor(QColor(color))
#		else:
#			self.txtCode.setTextColor(QColor(color))
		pass
		
	def __init__(self):
		super().__init__()
		
		self.setLayout(QHBoxLayout())
		
#		self.txtLineCount = DisassemblyLineNumTextEdit()
#		self.txtLineCount.setFixedWidth(70)
##       self.lineCount.setContentsMargins(0)
##       self.lineCount.setTextBackgroundColor(QColor("lightgray"))
#		self.txtLineCount.setTextColor(QColor("black"))
#		self.txtLineCount.setStyleSheet("background-color: rgb(200, 200, 200); padding-left:0; padding-top:0; padding-bottom:0; padding-right:0; margin-left:0px; margin-right:0px;")
#		self.txtLineCount.setReadOnly(True)
#		self.txtLineCount.setFont(ConfigClass.font)
#		
#		self.txtCode = DisassemblyTextEdit()
#		self.txtCode.setTextColor(QColor("black"))
#		self.txtCode.setStyleSheet("background-color: rgb(200, 200, 200); padding-left:0; padding-top:0; padding-bottom:0; padding-right:0; margin-left:0px; margin-right:0px;")
#		self.txtCode.setReadOnly(True)
#		self.txtCode.setFont(ConfigClass.font)
#		
#		path = QPainterPath()
#		path.moveTo(150, 150)
#		path.arcTo(40, 40, 10, 10, 0, 270)
#		path.closeSubpath()
#		
#		# Create a QPainter and attach it to the textEdit
#		painter = QPainter(self)
#		
#		# Set the painter's pen and brush
#		pen = QPen(Qt.GlobalColor.red, 2)
#		brush = QBrush(Qt.GlobalColor.red)
#		painter.setPen(pen)
#		painter.setBrush(brush)
#		
#		painter.begin(self)  # Capture painter's actions
#		# Paint the circle
#		painter.drawPath(path)
#		
#		# Release the painter
#		painter.end()
##		self.txtCode.show()
#		self.txtLineCount.verticalScrollBar().setVisible(False)
#		self.txtLineCount.verticalScrollBar().hide()
#		self.txtLineCount.horizontalScrollBar().setVisible(False)
#		self.txtLineCount.horizontalScrollBar().hide()
#		
#		self.txtLineCount.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
#		self.txtLineCount.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
#		
#		self.txtLineCount.horizontalScrollBar().valueChanged.connect(
#			self.txtCode.horizontalScrollBar().setValue)
#		self.txtLineCount.verticalScrollBar().valueChanged.connect(
#			self.txtCode.verticalScrollBar().setValue)
#		self.txtCode.horizontalScrollBar().valueChanged.connect(
#			self.txtLineCount.horizontalScrollBar().setValue)
#		self.txtCode.verticalScrollBar().valueChanged.connect(
#			self.txtLineCount.verticalScrollBar().setValue)
#		
		self.frame = QFrame()
#		
		self.vlayout = QHBoxLayout()
		self.frame.setLayout(self.vlayout)
		
#		self.vlayout.addWidget(self.txtLineCount)
#		self.vlayout.addWidget(self.txtCode)
		
		self.table = DisassemblyTableWidget()
#		self.table.setColumnCount(4)
#		self.table.setColumnWidth(3, 256)
#		self.table.setRowCount(1)
#		self.table.verticalHeader().hide()
#		self.table.horizontalHeader().hide()
#		self.table.setFont(ConfigClass.font)
		
#		self.table.addRow(1, "0x10006fe4", "push ebp", "; Some comment")
#		self.table.addRow(2, "0x10006fe8", "mov esi ebp", "; Some comment 123")
#		Create QTableWidgetItem objects for each column
#		item0 = DisassemblyTableWidgetItem("1:", QTableWidgetItem.ItemType.Type)
#		item0.setBackground(QBrush(QColor(255, 0, 0)))
#		item1 = QTableWidgetItem("0x10006fe4", QTableWidgetItem.ItemType.Type)
#		item2 = QTableWidgetItem("push ebp", QTableWidgetItem.ItemType.Type)
#		item3 = QTableWidgetItem("; Some comment", QTableWidgetItem.ItemType.Type)
#		
#		item10 = DisassemblyTableWidgetItem("2:", QTableWidgetItem.ItemType.Type)
#		item11 = QTableWidgetItem("0x10006fe8", QTableWidgetItem.ItemType.Type)
#		item12 = QTableWidgetItem("push esi", QTableWidgetItem.ItemType.Type)
#		item13 = QTableWidgetItem("; Some comment 123", QTableWidgetItem.ItemType.Type)
#		
#		# Insert the items into the row
#		self.table.setItem(0, 0, item0)
#		self.table.setItem(0, 1, item1)
#		self.table.setItem(0, 2, item2)
#		self.table.setItem(0, 3, item3)
#		
#		self.table.setItem(1, 0, item10)
#		self.table.setItem(1, 1, item11)
#		self.table.setItem(1, 2, item12)
#		self.table.setItem(1, 3, item13)
#		
##		self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
##		self.table.setShowGrid(False)
#		self.table.setRowHeight(0, 18)
#		self.table.setRowHeight(1, 18)
		
#		data = [
#			[4, 9, 2],
#			[1, 0, 0],
#			[3, 5, 0],
#			[3, 3, 2],
#			[7, 8, 9],
#		]
#
#		self.model = DisassemblyTableModel(data)
#		self.table.setModel(self.model)
		
		self.vlayout.addWidget(self.table)
						
		self.vlayout.setSpacing(0)
		self.vlayout.setContentsMargins(0, 0, 0, 0)
		
		self.frame.setFrameShape(QFrame.Shape.NoFrame)
		self.frame.setFrameStyle(QFrame.Shape.NoFrame)
		self.frame.setContentsMargins(0, 0, 0, 0)
#       self.frame.spac
		# .setSpacing(0)
		
		self.widget = QWidget()
		self.layFrame = QHBoxLayout()
		self.layFrame.addWidget(self.frame)
		self.widget.setLayout(self.layFrame)
		
		self.layout().addWidget(self.widget)
		
#class CustomTextEdit(QTextEdit):
#   
#   def __init__(self):
#       super().__init__()
#       
#       self.cursorPositionChanged.connect(self.updateLineNumberArea)
##       self.setWordWrapMode(Qt) # .setWordWrapMode(QTextEdit.WordWrapMode.NoWrap)
#       self.highlightCurrentLine()
#       
#       self.lineNumberArea = QWidget(self)
#       self.lineNumberArea.setGeometry(QRect(0, 0, self.width(), 20))
#       self.lineNumberArea.setObjectName("lineNumberArea")
##       self.lineNumberArea.setAlignment(Qt.AlignRight)
#       
#       self.updateLineNumberAreaWidth()
##       self.connect(self, &QTextEdit::cursorPositionChanged, self.updateLineNumberArea)
##       self.connect(self, &QTextEdit::updateRequest, self.updateLineNumberArea)
#       
#   def paintEvent(self, event):
#       super().paintEvent(event)
#       
#       self.lineNumberArea.update()
#       
#       painter = QPainter(self.viewport())
##       painter.fillRect(event.rect(), QColor("lightgray"))
#   
#   def updateLineNumberAreaWidth(self):
#       metrics = QFontMetrics(self.font())
##       lineNumberWidth = metrics.horizontalAdvance("0") * self.blockCount()
#       lineNumberWidth = 20
#       self.lineNumberArea.setFixedWidth(lineNumberWidth + 10)
#       
#   def updateLineNumberArea(self):
#       cursor = self.textCursor()
#       block = cursor.block()
#       blockNumber = block.blockNumber() + 1
#       
#       if blockNumber < 0:
#           blockNumber = 0
#           
#       cursorEnd = cursor.position() + cursor.block().length()
#       lineCount = self.document().lastBlock().blockNumber() + 1
#       
#       self.lineNumberArea.update(0, 0, self.lineNumberArea.width(), lineCount * 20)
#       
#   def highlightCurrentLine(self):
#       cursor = self.textCursor()
#       
#       if not cursor.hasSelection():
#           lineColor = QColor("gray")
#           selectionColor = Qt.BrushStyle.NoBrush
#       else:
#           selectionColor = Qt.highlightSelection()
#           lineColor = self.palette().color(QPalette.Text)
#           
#       format = QTextCharFormat()
#       format.setBackground(lineColor)
#       
##       cursor.setBlockFormat(format)
		