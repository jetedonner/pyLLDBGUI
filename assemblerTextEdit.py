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
#		self.context_menu.addSeparator()
#		actionCopyAddress = self.context_menu.addAction("Find references")

	def contextMenuEvent(self, event):
		self.context_menu.exec(event.globalPos())
		
class AssemblerTextEdit(QWidget):
	
	lineCount = 0
	
	def clear(self):
		self.txtCode.clear()
		self.txtLineCount.clear()
		self.lineCount = 0
		pass
		
	def appendAsmText(self, txt, addLineNum = True):
		self.txtCode.append(txt)
		if addLineNum:
			self.lineCount += 1
			self.txtLineCount.append(str(self.lineCount) + ":")
		else:
			self.txtLineCount.append(" ")
#			print("addLineNum IS FALSE")
			
	def insertText(self, txt, bold = False, color = "black"):
		cursor = self.txtCode.textCursor()
		
		if bold:
			boldFormat = QTextCharFormat()
			boldFormat.setFontWeight(QFont.Weight.Bold)
			# Merge the bold format with the text cursor
			cursor.mergeCharFormat(boldFormat)

		# Insert the substring
		cursor.insertText(txt)
		# Move the cursor to the end of the paragraph
		cursor.movePosition(QTextCursor.MoveOperation.EndOfLine)
		
		if bold:
			normalFormat = QTextCharFormat()
			normalFormat.setFontWeight(QFont.Weight.Normal)
			# Merge the normal format with the text cursor
			cursor.mergeCharFormat(normalFormat)
		
		# Append the substring to the QTextEdit
		self.txtCode.setTextColor(QColor(color))
		self.txtCode.setTextCursor(cursor)
		
		self.txtLineCount.insertPlainText(" ")
	
	
	def setTextColor(self, color = "black", lineNum = False):
		if lineNum:
			self.txtLineCount.setTextColor(QColor(color))
		else:
			self.txtCode.setTextColor(QColor(color))
		
	def __init__(self):
		super().__init__()
		
		self.setLayout(QHBoxLayout())
		
#		self.font = QFont("Courier New")
#		self.font.setFixedPitch(True)
		
		self.txtLineCount = DisassemblyLineNumTextEdit()
		self.txtLineCount.setFixedWidth(70)
#       self.lineCount.setContentsMargins(0)
#       self.lineCount.setTextBackgroundColor(QColor("lightgray"))
		self.txtLineCount.setTextColor(QColor("black"))
		self.txtLineCount.setStyleSheet("background-color: rgb(200, 200, 200); padding-left:0; padding-top:0; padding-bottom:0; padding-right:0; margin-left:0px; margin-right:0px;")
		self.txtLineCount.setReadOnly(True)
		self.txtLineCount.setFont(ConfigClass.font)
#       self.layout().addWidget(self.lineCount)
		# Create a QPainterPath and draw the circle
		
		
		
		
		self.txtCode = DisassemblyTextEdit()
		self.txtCode.setTextColor(QColor("black"))
		self.txtCode.setStyleSheet("background-color: rgb(200, 200, 200); padding-left:0; padding-top:0; padding-bottom:0; padding-right:0; margin-left:0px; margin-right:0px;")
		self.txtCode.setReadOnly(True)
		self.txtCode.setFont(ConfigClass.font)
		
		path = QPainterPath()
		path.moveTo(150, 150)
		path.arcTo(40, 40, 10, 10, 0, 270)
		path.closeSubpath()
		
		# Create a QPainter and attach it to the textEdit
		painter = QPainter(self)
		
		# Set the painter's pen and brush
		pen = QPen(Qt.GlobalColor.red, 2)
		brush = QBrush(Qt.GlobalColor.red)
		painter.setPen(pen)
		painter.setBrush(brush)
		
		painter.begin(self)  # Capture painter's actions
		# Paint the circle
		painter.drawPath(path)
		
		# Release the painter
		painter.end()
#		self.txtCode.show()
		self.txtLineCount.verticalScrollBar().setVisible(False)
		self.txtLineCount.verticalScrollBar().hide()
		self.txtLineCount.horizontalScrollBar().setVisible(False)
		self.txtLineCount.horizontalScrollBar().hide()
		
		self.txtLineCount.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.txtLineCount.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		
		self.txtLineCount.horizontalScrollBar().valueChanged.connect(
			self.txtCode.horizontalScrollBar().setValue)
		self.txtLineCount.verticalScrollBar().valueChanged.connect(
			self.txtCode.verticalScrollBar().setValue)
		self.txtCode.horizontalScrollBar().valueChanged.connect(
			self.txtLineCount.horizontalScrollBar().setValue)
		self.txtCode.verticalScrollBar().valueChanged.connect(
			self.txtLineCount.verticalScrollBar().setValue)
		
		self.frame = QFrame()
		
		self.vlayout = QHBoxLayout()
		self.frame.setLayout(self.vlayout)
		
		self.vlayout.addWidget(self.txtLineCount)
		self.vlayout.addWidget(self.txtCode)
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
		