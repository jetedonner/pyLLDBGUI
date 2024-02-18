#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
	QHEXTextEdit v.0.0.1 - 2023-12-28 (Python3 / PyQt6 GUI extension)

	This is a new Python 3 / PyQt6 Widget that shows only hex values in a specialized QTextEdit namely QHEXTextEdit to represent the string as HEX value.
	The widget aims to follow the PyQt6 coding guidelines and has - beside PyQt6 - no dependensies.
	The drawing of the widget is completely done with PyQt6 functionality

	Author:		DaVe inc. Kim-David Hauser
	License:	MIT
	Git:		https://github.com/jetedonner/ch.kimhauser.python.helper
	Website:	https://kimhauser.ch
"""

import array
import enum
# from enum import StrEnum

# import enum

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

#from helper import *

from QSwitch import *

import re

class HexGrouping(enum.Enum):
	NoGrouping = 1 #"No grouping"
	TwoChars = 2 #"Two characters"
	FourChars = 3 #"Four characters"

#def format_hex_string(hex_string):
#	# Split the hex string into pairs
#	hex_pairs = re.findall(r'....', hex_string)
#	
#	# Separate the pairs with spaces
#	formatted_string = ' '.join(hex_pairs)
#	
#	# Insert two spaces after every 8 pairs
##	for i in range(0, len(formatted_string), 8):
##		formatted_string = formatted_string[:i] + '  ' + formatted_string[i:]
#		
#	return formatted_string

class QHEXTextEdit(QTextEdit):
	
	doUpdateHexString:bool = True
	
	
	
	@property
	def hexGrouping(self):
		return self._hexGrouping
	
	@hexGrouping.setter
	def hexGrouping(self, new_hexGrouping):
		self._hexGrouping = new_hexGrouping
		self.formatHexString()
		
	@property
	def insertSpace(self):
		return self._insertSpace
	
	@insertSpace.setter
	def insertSpace(self, new_insertSpace):
		self._insertSpace = new_insertSpace
		self.formatHexString()
	
	@property
	def insertGroupSpace(self):
		return self._insertGroupSpace
	
	@insertGroupSpace.setter
	def insertGroupSpace(self, new_insertGroupSpace):
		self._insertGroupSpace = new_insertGroupSpace
		self.formatHexString()
		
	@property
	def onlyUpperCase(self):
		return self._onlyUpperCase
	
	@onlyUpperCase.setter
	def onlyUpperCase(self, new_onlyUpperCase):
		self._onlyUpperCase = new_onlyUpperCase
		self.formatHexString()
		
	def __init__(self, parent=None):
		QTextEdit.__init__(self, parent=parent)
		self.doUpdateHexString = True
		self._hexGrouping = HexGrouping.FourChars
		self._insertSpace = True
		self._insertGroupSpace = True
		self._onlyUpperCase = True
		
		
#		self.textChanged.connect(self.formatHexString)
		
		cf = QTextCharFormat()
#		cf.setContentsMargins(0, 0, 0, 0)
		cf.setFontCapitalization(QFont.Capitalization.MixedCase)
		self.setCurrentCharFormat(cf)
		self.textChanged.connect(self.self_textchanged)
		
		# self.insertPlainText("AABBCCDDEEFF00998877665544332211")
		
	def keyPressEvent(self, event):
		key = event.key()
		cmd_modifier = (event.modifiers() == Qt.KeyboardModifier.ControlModifier)
		if cmd_modifier:
#			print(f"cmd_modifier: {cmd_modifier} / key: {key}")
			if key in (Qt.Key.Key_C, Qt.Key.Key_X, Qt.Key.Key_V, Qt.Key.Key_A):
				super().keyPressEvent(event)
				return
			
		if key in (Qt.Key.Key_0, Qt.Key.Key_1, Qt.Key.Key_2, Qt.Key.Key_3, Qt.Key.Key_4, Qt.Key.Key_5, Qt.Key.Key_6, Qt.Key.Key_7, Qt.Key.Key_8, Qt.Key.Key_9, Qt.Key.Key_A, Qt.Key.Key_B, Qt.Key.Key_C, Qt.Key.Key_D, Qt.Key.Key_E, Qt.Key.Key_F, Qt.Key.Key_Space, Qt.Key.Key_Backspace, Qt.Key.Key_Delete, Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
			super().keyPressEvent(event)
		else:
			event.ignore()
			
	def self_textchanged(self):
		if not self.doUpdateHexString:
			return
		self.checkIsHexString()
		self.formatHexString()
		pass
		
	def checkIsHexString(self):
		try:
			int(self.toPlainText(), 16)
		except Exception as e:
			pass
	
	def formatHexStringFourChars(self, hex_string):
		# Split the hex string into pairs
		
		
		no_space_text = hex_string.replace(" ", "")
		strLen = len(no_space_text)
		hex_pairs = re.findall(r'....', no_space_text)
		if len(hex_pairs) < (strLen / 4):
			return hex_string
			pass
		# Separate the pairs with spaces
		formatted_string = ' '.join(hex_pairs)
		
		# Insert two spaces after every 8 pairs
	#	for i in range(0, len(formatted_string), 8):
	#		formatted_string = formatted_string[:i] + '  ' + formatted_string[i:]
		
		return formatted_string

	def formatHexStringNChars(self, hex_string, nChars = 2):
		# Split the hex string into pairs
		
		
		no_space_text = hex_string.replace(" ", "")
		strLen = len(no_space_text)
		hex_pairs = re.findall(r'....', no_space_text)
		if len(hex_pairs) < (strLen / nChars):
			return hex_string
			pass
		# Separate the pairs with spaces
		formatted_string = ' '.join(hex_pairs)
		
		# Insert two spaces after every 8 pairs
	#	for i in range(0, len(formatted_string), 8):
	#		formatted_string = formatted_string[:i] + '  ' + formatted_string[i:]
		
		return formatted_string
	
	def formatHexString(self, hex_string = None):
		self.doUpdateHexString = False
		
		cur = self.textCursor()
		origString = hex_string #self.toPlainText()
		if hex_string is None:
			origString = self.toPlainText()
			
		if self.hexGrouping == HexGrouping.FourChars:
			self.setText(self.formatHexStringFourChars(origString))
			self.setTextCursor(cur)
			self.doUpdateHexString = True
			return
		elif self.hexGrouping == HexGrouping.NoGrouping:
			no_space_text = origString.replace(" ", "")
			self.setText(no_space_text)
#			self.setTextCursor(cur)
			self.doUpdateHexString = True
			return
		
		
		newString = ""
		self.setText("")
		
#		print(format_hex_string(origString))
		
		idx = 0
		for c in origString:
			idx += 1
#			print(f"Char: {c}")
			if self.insertGroupSpace and ((idx % 24 == 0) or idx == 24) and c != " " and c != "  ":
				newString += "  "
				idx += 3
			elif self.insertSpace and ((idx % 3 == 0) or idx == 3) and c != " ":
				newString += " "
				idx += 1
			elif not self.insertSpace and c == " ":
				continue
			
			if self.onlyUpperCase:
				newString += str(c).upper()
			else:
				newString += str(c)

		self.setText(newString)
		self.setTextCursor(cur)
		self.doUpdateHexString = True
		pass
		
		
class QHEXTextEditWindow(QMainWindow):
	"""PyMobiledevice3GUI's main window (GUI or view)."""
	
	def __init__(self):
		super().__init__()
		self.setWindowTitle("QHEXTextEdit - Demo app v0.0.1")
		self.setMinimumSize(512, 320)
		
		self.layMain = QVBoxLayout()
		self.wdtMain = QWidget()
		self.wdtMain.setLayout(self.layMain)
		
		self.lblDesc = QLabel(f"This is a rought demo of the usage of QHEXTextEdit")
		self.layMain.addWidget(self.lblDesc)
		
		self.cmdRefresh = QPushButton("Format")
#		self.cmdRefresh.setIcon(IconHelper.getRefreshIcon())
		self.cmdRefresh.setIconSize(QSize(16, 16))
		self.cmdRefresh.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		self.cmdRefresh.clicked.connect(self.refresh_clicked)
		self.layMain.addWidget(self.cmdRefresh)
		
		self.layOpt = QHBoxLayout()
		self.wdtOpt = QWidget()
		self.wdtOpt.setLayout(self.layOpt)
		
		self.txtHex = QHEXTextEdit()
		
		self.cmbGrouping = QComboBox()
#		self.cmbGrouping.addI
		self.cmbGrouping.addItem(str(HexGrouping.NoGrouping), HexGrouping.NoGrouping)
		self.cmbGrouping.addItem(str(HexGrouping.TwoChars), HexGrouping.TwoChars)
		self.cmbGrouping.addItem(str(HexGrouping.FourChars), HexGrouping.FourChars)
		self.cmbGrouping.currentIndexChanged.connect(self.cmbGrouping_changed)
		self.cmbGrouping.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		
		self.groupingLabel = QLabel(f"Grouping:")
		self.groupingLabel.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
		
		self.layOpt.addWidget(self.groupingLabel)
		self.layOpt.addWidget(self.cmbGrouping)
		
		self.swtInsertSpace = QSwitch("Insert Space", SwitchSize.Small, SwitchLabelPos.Trailing)
		self.swtInsertSpace.setChecked(self.txtHex.insertSpace)
		self.swtInsertSpace.checked.connect(self.swtInsertSpace_checked)
		self.layOpt.addWidget(self.swtInsertSpace)
		
		self.swtUpper = QSwitch("Only UpperCase", SwitchSize.Small, SwitchLabelPos.Trailing)
		self.swtInsertSpace.setChecked(self.txtHex.onlyUpperCase)
		self.swtUpper.checked.connect(self.swtUpper_checked)
		self.layOpt.addWidget(self.swtUpper)
		
		self.layMain.addWidget(self.wdtOpt)
		
		
		self.layMain.addWidget(self.txtHex)
		self.setCentralWidget(self.wdtMain)
		
	def cmbGrouping_changed(self, currentIdx:int):
		print(self.cmbGrouping.itemData(currentIdx))
		self.txtHex.hexGrouping = self.cmbGrouping.itemData(currentIdx)
		pass
#		encoding = "utf-8"
#		if currentIdx == 0:
#			encoding = "utf-8"
#		elif currentIdx == 1:
#			encoding = "utf-16"
#		elif currentIdx == 2:
#			encoding = "ascii"
#		else:
#			encoding = "utf-8"
#		self.setTextWithEncoding(encoding)
		
	def refresh_clicked(self):
		print(self.txtHex.formatHexString(self.txtHex.toPlainText()))
		pass
		
	def swtInsertSpace_checked(self, checked):
		self.txtHex.insertSpace = checked
		pass
		
	def swtUpper_checked(self, checked):
		self.txtHex.onlyUpperCase = checked
		pass
		
if __name__ == '__main__':
	import sys
	app = QApplication(sys.argv)
	win = QHEXTextEditWindow()
	win.show()
	sys.exit(app.exec())