#!/usr/bin/env python3

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

class HistoryLineEdit(QLineEdit):
	
	lstCommands = []
	currCmd = 0
	
	def __init__(self):
		super().__init__()
		
	def keyPressEvent(self, event):
		
		if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down):
			print("Up or down key pressed")
			if event.key() == Qt.Key.Key_Up:
				if self.currCmd > 0:
					self.currCmd -= 1
					if self.currCmd < len(self.lstCommands):
						self.setText(self.lstCommands[self.currCmd])
			else:
				if self.currCmd < len(self.lstCommands) - 1:
					self.currCmd += 1
					self.setText(self.lstCommands[self.currCmd])
			event.accept()  # Prevent event from being passed to QLineEdit for default behavior
		elif event.key() == Qt.Key.Key_Return:
#			self.lstCommands.append(self.text())
			print("INSIDE HISTORY LINE EDIT RETURN PRESSED!!!!!")
			self.addCommandToHistory()
#			newCommand = self.text()
#			if len(self.lstCommands) > 0:
#				if self.lstCommands[len(self.lstCommands) - 1] != newCommand:
#					self.lstCommands.append(newCommand)
#					self.currCmd = len(self.lstCommands) - 1
#			else:
#				self.lstCommands.append(newCommand)
#				self.currCmd = len(self.lstCommands) - 1
			super(HistoryLineEdit, self).keyPressEvent(event)
			pass
		else:
			super(HistoryLineEdit, self).keyPressEvent(event)
		
	def addCommandToHistory(self):
		newCommand = self.text()
		if len(self.lstCommands) > 0:
			if self.lstCommands[len(self.lstCommands) - 1] != newCommand:
				self.lstCommands.append(newCommand)
				self.currCmd = len(self.lstCommands) - 1
		else:
			self.lstCommands.append(newCommand)
			self.currCmd = len(self.lstCommands) - 1