#!/usr/bin/env python3
import os

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

class ConfirmDialog(QDialog):
	def __init__(self, title, question):
		super().__init__()
		
		self.setWindowTitle(title)
		
		QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
		
		self.buttonBox = QDialogButtonBox(QBtn)
		self.buttonBox.accepted.connect(self.accept)
		self.buttonBox.rejected.connect(self.reject)
		
		self.layout = QVBoxLayout()
		message = QLabel(question)
		self.layout.addWidget(message)
		self.layout.addWidget(self.buttonBox)
		self.setLayout(self.layout)

class InputDialog(QDialog):
	def __init__(self, title, prompt, preset = ""):
		super().__init__()
		
		self.setWindowTitle(title)
		
		QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
		
		self.buttonBox = QDialogButtonBox(QBtn)
		self.buttonBox.accepted.connect(self.accept)
		self.buttonBox.rejected.connect(self.reject)
		
		self.layout = QVBoxLayout()
		self.message = QLabel(prompt)
		self.txtInput = QLineEdit()
		self.txtInput.setText(preset)
		self.layout.addWidget(self.message)
		self.layout.addWidget(self.txtInput)
		self.layout.addWidget(self.buttonBox)
		self.setLayout(self.layout)
		self.txtInput.setFocus()

def showQuestionDialog(parent, title, question):
	dlg = QMessageBox(parent)
	dlg.setWindowTitle(title)
	dlg.setText(question)
	dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
	dlg.setIcon(QMessageBox.Icon.Warning)
	button = dlg.exec()
	
	return button == QMessageBox.StandardButton.Yes
#		print("Yes!")
#	else:
#		print("No!")
		
def showSaveFileDialog():
	dialog = QFileDialog(None, "Select file to save", "", "JSON (*.json)")
	dialog.setFileMode(QFileDialog.FileMode.AnyFile)
	dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
	dialog.setNameFilter("JSON (*.json)")
	
	if dialog.exec():
		filename = dialog.selectedFiles()[0]
#		while os.path.exists(filename):
#			if dialog.exec():
#				filename = dialog.selectedFiles()[0]
#		print(filename)
		return filename
#			self.start_workerLoadTarget(filename)
	else:
		return None

def showOpenBPFileDialog():
	dialog = QFileDialog(None, "Select JSON with Breakpoints", "", "JSON (*.json)")
	dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
	dialog.setNameFilter("JSON (*.json)")
	
	if dialog.exec():
		filename = dialog.selectedFiles()[0]
		print(filename)
		return filename
#			self.start_workerLoadTarget(filename)
	else:
		return None
	
def showOpenFileDialog():
	dialog = QFileDialog(None, "Select executable or library", "", "All Files (*.*)")
	dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
	dialog.setNameFilter("Executables (*.exe *.com *.bat *);;Libraries (*.dll *.so *.dylib)")
	
	if dialog.exec():
		filename = dialog.selectedFiles()[0]
		print(filename)
		return filename
#			self.start_workerLoadTarget(filename)
	else:
		return None