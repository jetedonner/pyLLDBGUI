#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
	QHEXTextEdit / QHEXTextEditSplitter v.0.0.1 - 2023-12-28 (Python3 / PyQt6 GUI extension)

	This are two new Python 3 / PyQt6 Widgets that show text values in a QTextEdit and a synchronized specialized QTextEdit namely QHEXTextEdit to represent the string as HEX value.
	The widget aims to follow the PyQt6 coding guidelines and has - beside PyQt6 - no dependensies.
	The drawing of the widget is completely done with PyQt6 functionality

	Author:		DaVe inc. Kim-David Hauser
	License:	MIT
	Git:		https://github.com/jetedonner/ch.kimhauser.python.helper
	Website:	https://kimhauser.ch
"""
	
import array
#from enum import Enum
import enum

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from QSwitch import *
from QHEXTextEdit import *

class HexTextEditPosition(enum.Enum):
	HexFirst = 1
	HexLast = 2
	HexOnly = 3
	NoHex = 4

class QHEXTextEditSplitter(QWidget):
		
	updateTxt:bool = True
	updateHexTxt:bool = True
	
	updateSel:bool = True
	updateHexSel:bool = True

	layoutTopPlaceholer = None

	txtMultiline = None
	txtMultilineHex = None

	hexTextEditPosition:HexTextEditPosition = HexTextEditPosition.HexFirst
	
	def __init__(self, parent=None):
		QWidget.__init__(self, parent=parent)
		
		self.updateTxt = True
		self.updateHexTxt = True
		
		self.layMain = QVBoxLayout()
		self.setLayout(self.layMain)
		self.splitter = QSplitter()
		self.splitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.splitter.setContentsMargins(0, 0, 0, 0)
		
		self.txtMultiline = QTextEdit()
		self.txtMultiline.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
		self.txtMultiline.textChanged.connect(self.txtMultiline_textchanged)
		self.txtMultiline.selectionChanged.connect(self.txtMultiline_selectionchanged)
		self.txtMultiline.setContentsMargins(0, 0, 0, 0)
		
		self.txtMultilineHex = QHEXTextEdit()
		self.txtMultilineHex.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
		self.txtMultilineHex.textChanged.connect(self.txtMultilineHex_textchanged)
		self.txtMultilineHex.selectionChanged.connect(self.txtMultilineHex_selectionchanged)
		self.txtMultilineHex.setContentsMargins(0, 0, 0, 0)
		
		if self.hexTextEditPosition == HexTextEditPosition.HexLast or self.hexTextEditPosition == HexTextEditPosition.NoHex:
			self.splitter.addWidget(self.txtMultiline)
			if self.hexTextEditPosition != HexTextEditPosition.NoHex:
				self.splitter.addWidget(self.txtMultilineHex)
		elif self.hexTextEditPosition == HexTextEditPosition.HexFirst or self.hexTextEditPosition == HexTextEditPosition.HexOnly:
			self.splitter.addWidget(self.txtMultilineHex)
			if self.hexTextEditPosition != HexTextEditPosition.HexOnly:
				self.splitter.addWidget(self.txtMultiline)
		
		self.swtShowHex = QSwitch("HEX View", SwitchSize.Small, SwitchLabelPos.Trailing)
		self.swtShowHex.checked.connect(self.swtShowHex_checked)
		self.swtShowHex.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.swtShowHex.setChecked(True)
		self.swtShowHex.setContentsMargins(0, 0, 0, 0)
		
		self.cmbEncoding = QComboBox()
		self.cmbEncoding.addItem("utf-8")
		self.cmbEncoding.addItem("utf-16")
		self.cmbEncoding.addItem("ascii")
#		self.cmbEncoding.currentIndexChanged.connect(self.cmbEncoding_changed)
		self.cmbEncoding.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.cmbEncoding.setContentsMargins(0, 0, 0, 0)
		
		encodingLabel = QLabel(f"Encoding:")
		encodingLabel.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		encodingLabel.setContentsMargins(0, 0, 0, 0)
		
		layoutTop = QHBoxLayout()
		self.layoutTopPlaceholer = QHBoxLayout()
		self.widTopPlaceholder = QWidget()

		self.widTop = QWidget()
		self.widTop.setLayout(layoutTop)
		self.widTopPlaceholder.setLayout(self.layoutTopPlaceholer)
		self.widTopPlaceholder.setContentsMargins(0, 0, 0, 0)

		layoutTop.addWidget(self.widTopPlaceholder)
		layoutTop.addStretch()
		layoutTop.addWidget(encodingLabel)
		layoutTop.addWidget(self.cmbEncoding)
		
		layoutTop.addWidget(self.swtShowHex)
		
		self.layMain.addWidget(self.widTop)
		self.layMain.addWidget(self.splitter)
		self.layMain.setContentsMargins(0, 0, 0, 0)
		
		# self.setText("DEV SAYS: Some amended text to test the new toHEX() function and the save function fix - IT WORKS!!! DEVs amendment ... Some addition!!!")
		
	def txtMultilineHex_textchanged(self):
		if not self.updateHexTxt:
			return
		
#		print("txtMultilineHex_textchanged")
		try:
			hex_string = self.txtMultilineHex.toPlainText()
			bytes_list = bytearray.fromhex(hex_string)
			ascii_text = bytes_list.decode("utf-8")
#			print(ascii_text)
			self.updateHexTxt = False
			self.updateTxt = False
			self.txtMultiline.setText(ascii_text)
			self.updateHexTxt = True
			self.updateTxt = True
		except Exception as e:
			pass
		pass
		
	def txtMultilineHex_selectionchanged(self):
		if not self.updateHexSel:
			return
		cursor = self.txtMultilineHex.textCursor()
		print("txtMultilineHex Selection start: %d end: %d" % (cursor.selectionStart(), cursor.selectionEnd()))
		
		self.txtMultiline.setStyleSheet("background-color: control;")
		
		c = self.txtMultiline.textCursor()
		c.clearSelection()
		txtLen = len(self.txtMultiline.toPlainText())
		startPos = int(cursor.selectionStart() / 3)
		if startPos > txtLen:
			startPos -= 1
		c.setPosition(startPos)
		endPos = int((cursor.selectionEnd() + 1) / 3)
		if endPos > txtLen:
			endPos -= 1
		print(f"txtLen = {txtLen}")
		c.setPosition(endPos, QTextCursor.MoveMode.KeepAnchor)
		self.txtMultiline.setStyleSheet("selection-background-color: #ff0000;")
		self.updateHexSel = False
		self.updateSel = False
		self.txtMultiline.setTextCursor(c)
		self.updateHexSel = True
		self.updateSel = True
		self.txtMultiline.ensureCursorVisible()
		
	def txtMultiline_textchanged(self):
		if not self.updateTxt:
			return
		
		print("txtMultiline_textchanged")
		self.updateTxt = False
		self.updateHexTxt = False
		self.setTxtHex()
		self.updateTxt = True
		self.updateHexTxt = True
		
	def txtMultiline_selectionchanged(self):
		if not self.updateSel:
			return
		cursor = self.txtMultiline.textCursor()
		print("txtMultiline Selection start: %d end: %d" % (cursor.selectionStart(), cursor.selectionEnd()))
		
		self.txtMultilineHex.setStyleSheet("background-color: control;")
		
		c = self.txtMultilineHex.textCursor()
		c.clearSelection()
		txtLen = len(self.txtMultilineHex.toPlainText())
		startPos = (cursor.selectionStart() * 3) - 0
		if startPos > txtLen:
			startPos -= 1
		c.setPosition(startPos)
		endPos = (cursor.selectionEnd() * 3) - 1
		if endPos > txtLen:
			endPos -= 1
		print(f"txtLen = {txtLen}")
		c.setPosition(endPos, QTextCursor.MoveMode.KeepAnchor)
		self.txtMultilineHex.setStyleSheet("selection-background-color: #ff0000;")
		self.updateTxt = False
		self.updateHexTxt = False
		self.txtMultilineHex.setTextCursor(c)
		self.updateTxt = True
		self.updateHexTxt = True
		self.txtMultilineHex.ensureCursorVisible()
		
	def setText(self, text):
		if not self.updateTxt:
			return
		
		self.updateTxt = False
		self.txtMultiline.insertPlainText(text)
		self.setTxtHex(text)
		self.updateTxt = True
		
	def setTxtHex(self, text:str = None):
		self.txtAsString = text
		if self.txtAsString is None:
			self.txtAsString = self.txtMultiline.toPlainText()
			
		try:
			self.txtInBytes = self.txtAsString.encode("utf-8")
			self.hexData = [format(byte, '02x') for byte in self.txtInBytes] # self.fileContent]
			self.formattedHexData = ' '.join(self.hexData)
			self.txtMultilineHex.setText(str.upper(self.formattedHexData))
		except Exception as e:
			print(f"Exception: '{e}' while converting text '{self.txtAsString}' to HEX string")
			pass
	
	def setTxtHexNG(self, txtInBytes, showAddress = True, startAddress:int = 0):
		# self.txtAsString = text
		# if self.txtAsString is None:
		# 	self.txtAsString = self.txtMultiline.toPlainText()
			
		try:
			# self.txtInBytes = self.txtAsString.encode("utf-8")
			self.hexData = [format(byte, '02x') for byte in txtInBytes] # self.fileContent]
			# print(f'self.hexData = {self.hexData}')
			# self.formattedHexData = ''
			# if showAddress:
			# 	self.formattedHexData = hex(startAddress) + ': ' + str.upper(' '.join(self.hexData))
			# else:
			
			string2 = ""
			string = ""
			for i in range(0, len(self.hexData), 16):
			    current_values = self.hexData[i:i+16]
			    for single in current_values:
			    	# print(single)
			    	# string2 += chr(int(single, 16))
			    	# string2 += bytearray(int(single, 16)).decode('utf-8')
			    	integer_value = int(single, 16)
			    	utf_8_char = chr(integer_value)
			    	# print(utf_8_char)
			    	string2 += utf_8_char
			    	
			    string2 += "\n"
			    # print(current_values)
			    # ascii_array = bytearray(current_values).decode('utf-8')
			    # string2 = ''.join(ascii_array)
			    # string2 += "\n"
			    current_string = ' '.join(current_values)
			    string += hex(startAddress + i) + ": " + current_string + '\n'

			# print(f'{string}')

			# self.formattedHexData = ' '.join(self.hexData)
			self.updateTxt = False
			self.updateHexTxt = False
			self.txtMultilineHex.doUpdateHexString = False
			self.txtMultilineHex.setText(string)
			self.txtMultiline.setText(string2)
			self.updateTxt = True
			self.updateHexTxt = True
		except Exception as e:
			print(f"Exception: '{e}' while converting bytes '{txtInBytes}' to HEX string")
			pass

	def swtShowHex_checked(self, checked):
		self.splitter.widget(1).setVisible(checked)
		pass
		
	def showHex_changed(self, checked):
		self.splitter.widget(1).setVisible(checked)
		
class QHEXTextEditSplitterWindow(QMainWindow):
	"""PyMobiledevice3GUI's main window (GUI or view)."""
	
	def __init__(self):
		super().__init__()
		self.setWindowTitle("QHEXTextEditSplitter - Demo app v0.0.1")
		self.setMinimumSize(512, 320)
		
		self.layMain = QVBoxLayout()
		self.wdtMain = QWidget()
		self.wdtMain.setLayout(self.layMain)

		self.lblDesc = QLabel(f"This is a rought demo of the usage of QHEXTextEditSplitter with a mixed matrix of its options")
		self.layMain.addWidget(self.lblDesc)
		self.splitter = QHEXTextEditSplitter()
		self.layMain.addWidget(self.splitter)
		self.setCentralWidget(self.wdtMain)
		
if __name__ == '__main__':
	import sys
	app = QApplication(sys.argv)
	win2 = QHEXTextEditSplitterWindow()
	win2.show()
	sys.exit(app.exec())