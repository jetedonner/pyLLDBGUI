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

class BreakpointHelper():
	
	table = None
	colNum = 1
	colCond = 5
	
#	@staticmethod
	def handle_editCondition(self, table, colNum, colCond):
		self.table = table
		self.colNum = colNum
		self.colCond = colCond
		itemNum = self.table.item(self.table.selectedItems()[0].row(), self.colNum)
		itemCond = self.table.item(self.table.selectedItems()[0].row(), self.colCond)
		title = f'Condition of breakpoint {itemNum.text()}'
		label = f'Edit the condition of breakpoint {itemNum.text()}'
		
		dialog = QInputDialog()
		dialog.setWindowTitle(title)
		dialog.setLabelText(label)
		self.oldCond = itemCond.text()
		dialog.setTextValue(self.oldCond)
		dialog.textValueChanged.connect(self.handle_editConditionChanged)
		dialog.resize(512, 128)
		# Show the dialog and get the selected process name
		if dialog.exec():
			# OK pressed
#			print(f'self.table.window =====>>>> {self.table.window()}')
			print(self.table.window().updateStatusBar(f"Breakpoint ({itemNum.text()}) condition changed successfully"))
			pass
		else:
			itemCond.setText(self.oldCond)
	
#	@staticmethod
	def handle_editConditionChanged(self, text):
		itemCond = self.table.item(self.table.selectedItems()[0].row(), self.colCond)
		itemCond.setText(text)