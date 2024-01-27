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
		else:
			super(HistoryLineEdit, self).keyPressEvent(event)