#!/usr/bin/env python3
import os

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets
from config import *
from ui.settingsDialog import *

class ProcessesDialog(QDialog):
	def __init__(self, title = "", prompt = ""):
		super().__init__()
		
		self.setWindowTitle(title)
		
		QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
		
		self.buttonBox = QDialogButtonBox(QBtn)
		self.buttonBox.accepted.connect(self.accept)
		self.buttonBox.rejected.connect(self.reject)
		
		self.wdtInner = QWidget()
		self.layoutMain = QHBoxLayout()
		self.layout = QVBoxLayout()
		# Create QLabel and load image
		self.image_label = QLabel()
#			pixmap = QPixmap("path/to/your/image.jpg")  # Replace with your image path
		self.image_label.setPixmap(ConfigClass.pixGears)
		
			# Add label to layout
			
		self.message = QLabel(prompt)
		self.cmbPID = QComboBox()
#		self.txtInput = QLineEdit()
#		self.txtInput.setText(preset)
		self.layoutMain.addWidget(self.image_label)
		self.layout.addWidget(self.message)
#		self.layout.addWidget(self.txtInput)
		self.layout.addWidget(self.cmbPID)
		
		self.wdtManual = QWidget()
		self.layoutManual = QHBoxLayout()
#		self.layoutManual.addWidget(QLabel("PID:"))
		self.txtPID = QLineEdit()
		self.txtPID.setPlaceholderText("Enter PID manually ...")
		self.txtPID.setText("19091")
#		self.txtPID.setFocus(Qt.FocusReason.NoFocusReason)
		self.layoutManual.addWidget(QLabel("PID:"))
		self.layoutManual.addWidget(self.txtPID)
		self.wdtManual.setLayout(self.layoutManual)
		self.layout.addWidget(self.wdtManual)
		self.layout.addWidget(self.buttonBox)
		self.wdtInner.setLayout(self.layout)
		self.layoutMain.addWidget(self.wdtInner)
		self.setLayout(self.layoutMain)
#		self.txtInput.setFocus()
		self.loadPIDs()
		
	def showEvent(self, event):
		super().showEvent(event)
		# Set focus to line edit after the dialog is shown
		self.txtPID.setFocus()
		
	def loadPIDs(self):
		import psutil
		
		# Get list of all processes
		self.processes = list(psutil.process_iter())
		
		# Extract PID and name for each process
		process_info = []
		for process in self.processes:
			try:
				process_info.append((process.pid, process.name()))
				self.cmbPID.addItem(str(process.name() + " (" + str(process.pid) + ")"), process.pid)
			except (psutil.NoSuchProcess, psutil.AccessDenied):
				# Handle potential errors (process might disappear or insufficient permissions)
				pass
				
#		print(process_info)
	
	def getProcessForPID(self):
		for process in self.processes:
			if str(process.pid) == self.txtPID.text():
				return process
		return None
			
	def getSelectedProcess(self):
		if self.txtPID.text() != "":
			return self.getProcessForPID()
		return self.processes[self.cmbPID.currentIndex()]

	
class MessageDialog(QMessageBox):
	
	app = None
	def __init__(self, title, msg, icon = QMessageBox.Icon.Warning, app = None):
		super().__init__()
		self.app = app
		self.setWindowTitle(title)
		self.setText(msg)
		self.setIcon(icon)
		self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
		self.setDefaultButton(QMessageBox.StandardButton.Yes)
		
	def showModal(self):
		useNativeDlg = SettingsHelper.GetValue(SettingsValues.UseNativeDialogs)
		if self.app != None and not useNativeDlg:
			self.app.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeDialogs, True)
			
		button = self.exec()
	
		doLoadNew = False
		if button == QMessageBox.StandardButton.Yes:
			doLoadNew = True
			
		if self.app != None and not useNativeDlg:
			self.app.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeDialogs, False)
			
		return button
			
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
	def __init__(self, title = "", prompt = "", preset = ""):
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
		
class GotoAddressDialog(InputDialog):
	def __init__(self, presetAddress="0x"):
		super().__init__("Address to goto", "Enter an address to goto:", presetAddress)
		
#		self.setWindowTitle("Select goto address")
#		self.message
#		self.message.setText("Select an address to goto")
#		self.setWindowTitle(title)
#		
#		QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
#		
#		self.buttonBox = QDialogButtonBox(QBtn)
#		self.buttonBox.accepted.connect(self.accept)
#		self.buttonBox.rejected.connect(self.reject)
#		
#		self.layout = QVBoxLayout()
#		self.message = QLabel(prompt)
#		self.txtInput = QLineEdit()
#		self.txtInput.setText(preset)
#		self.layout.addWidget(self.message)
#		self.layout.addWidget(self.txtInput)
#		self.layout.addWidget(self.buttonBox)
#		self.setLayout(self.layout)
#		self.txtInput.setFocus()

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