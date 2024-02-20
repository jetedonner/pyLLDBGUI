#!/usr/bin/env python3

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

class HistoryLineEdit(QLineEdit):
	
	lstCommands = []
	currCmd = 0
	doAddCmdToHist = True
	
	def __init__(self, doAddCmdToHist = True):
		super().__init__()
		self.doAddCmdToHist = doAddCmdToHist
		
	def keyPressEvent(self, event):
		
		if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down):
#			print("Up or down key pressed")
			if event.key() == Qt.Key.Key_Up:
				if self.currCmd > 0:
					self.currCmd -= 1
					if self.currCmd < len(self.lstCommands):
						self.setText(self.lstCommands[self.currCmd])
			else:
				if self.currCmd < len(self.lstCommands) - 1:
					self.currCmd += 1
					self.setText(self.lstCommands[self.currCmd])
			# Prevent event from being passed to QLineEdit for default behavior
			event.accept()
		elif event.key() == Qt.Key.Key_Return:
			self.addCommandToHistory()
			super(HistoryLineEdit, self).keyPressEvent(event)
			pass
		else:
			super(HistoryLineEdit, self).keyPressEvent(event)
		
	def addCommandToHistory(self):
		if self.doAddCmdToHist:
			newCommand = self.text()
			if len(self.lstCommands) > 0:
				if self.lstCommands[len(self.lstCommands) - 1] != newCommand:
					self.lstCommands.append(newCommand)
					self.currCmd = len(self.lstCommands) - 1
			else:
				self.lstCommands.append(newCommand)
				self.currCmd = len(self.lstCommands) - 1