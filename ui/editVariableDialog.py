##!/usr/bin/env python3

import lldb

import os
import sys
import re
#
#from enum import Enum
##import re	
#	
from os.path import abspath
from os.path import dirname, realpath
from os import getcwd, path
#
from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets
#
from config import *

#from helper.dbgHelper import *
#
#
#class SettingsValues(Enum):
#	ConfirmRestartTarget = ("Confirm restart target", True, bool)
#	ConfirmQuitApp = ("Confirm quit app", True, bool)
#	DisassemblerShowQuickTooltip = ("Disassembler show QuickTooltip", True, bool)
#	CmdHistory = ("Commands history", True, bool)
#	MemViewShowSelectedStatubarMsg = ("Memory-Viewer on select show statusbar message", True, bool)
#	VisualizeCurrentBP = ("Visualise current breakpoint", True, bool)
		
#class SettingsHelper(QObject):
#	
#	settings = QSettings(ConfigClass.companyName, ConfigClass.appName)
#	
#	def __init__(self):
#		super().__init__()
#		
#	@staticmethod
#	def getSettings():
#		return QSettings(ConfigClass.companyName, ConfigClass.appName)
#		
#	@staticmethod
#	def GetChecked(setting):
#		return SettingsHelper().getChecked(setting)
#	
#	@staticmethod
#	def GetValue(setting):
#		return SettingsHelper().getValue(setting)
#	
#	def initDefaults(self):
#		self.settings.setValue(SettingsValues.ConfirmRestartTarget.value[0], True)
#		self.settings.setValue(SettingsValues.ConfirmQuitApp.value[0], True)
#		self.settings.setValue(SettingsValues.DisassemblerShowQuickTooltip.value[0], True)
#		self.settings.setValue(SettingsValues.CmdHistory.value[0], True)
#		self.settings.setValue(SettingsValues.MemViewShowSelectedStatubarMsg.value[0], True)
#	
#	def setChecked(self, setting, checkableItem):
#		self.settings.setValue(setting.value[0], checkableItem.checkState() == Qt.CheckState.Checked)
#		
#	def getChecked(self, setting):
#		return Qt.CheckState.Checked if self.settings.value(setting.value[0], setting.value[1], setting.value[2]) else Qt.CheckState.Unchecked
#	
##	def getBool(self, setting):
##		return True if self.settings.value(setting.value[0], setting.value[1], setting.value[2]) else False
#	
#	def getValue(self, setting):
#		return self.settings.value(setting.value[0], setting.value[1], setting.value[2])
	
class IntHexValidator(QValidator):
	def __init__(self, parent=None):
		super().__init__(parent)
#		self.int_regex = QtCore.QRegExp(r"^-?\d+$")  # Allows signed integers
#		self.hex_regex = QtCore.QRegExp(r"^0x[0-9a-fA-F]+$")  # Allows hex values with 0x prefix
		
		self.int_regex = r"^-?\d+$"  # Match anything within square brackets, excluding the brackets themselves
		self.hex_regex = r"^(0[xX])?[A-Fa-f0-9]+$" #"^(0x|0X)?[a-fA-F0-9]+$" # ^0x[0-9a-fA-F]+$"
		
	def validate(self, input_text, pos):
		try:
#			help(QValidator.validate)
#			print(help(QValidator.validate))
			print(f"Validating: '{input_text}', pos: {pos}")
			# Check if input is empty or a single minus sign
			if input_text == "" or input_text == "-":
				return (QValidator.State.Acceptable, input_text, pos)
			
			if re.search(self.int_regex, input_text): #.exactMatch(input_text):
				return (QValidator.State.Acceptable, input_text, pos)
			
			# Check for valid hex value
			if re.search(self.hex_regex, input_text): #if self.hex_regex.exactMatch(input_text):
				return (QValidator.State.Acceptable, input_text, pos)
			elif input_text.lower() == "0x": # or input_text == "0X":
				return (QValidator.State.Acceptable, input_text, pos)
	
		except Exception as e:
			print(f"Error validating: {e}")
			
		# Invalid input
		return (QValidator.State.Invalid, input_text, pos)
	
class EditVariableDialog(QDialog):
	
#	settings = QSettings("DaVe_inc", "LLDBPyGUI")
#	setHelper = None
	
#	def initDefaults(self):
#		self.settings.setValue(SettingsValues.ConfirmRestartTarget.value[0], True)
#		self.settings.setValue(SettingsValues.ConfirmQuitApp.value[0], True)
#		self.settings.setValue(SettingsValues.DisassemblerShowQuickTooltip.value[0], True)
#		self.settings.setValue(SettingsValues.CmdHistory.value[0], True)
#		self.settings.setValue(SettingsValues.MemViewShowSelectedStatubarMsg.value[0], True)
	variable = None
	
	def __init__(self, variable, parent=None):
		super().__init__()
		
		self.variable = variable
		
##		self.initDefaults()
#		
		# loading the ui file with uic module
		project_root = dirname(realpath(__file__))
		editVarDialogPath = os.path.join(project_root, '..', 'resources', 'designer', 'editVariableData.ui')
#		
		uic.loadUi(editVarDialogPath, self)
##		print("AFTER INIT settingsDialog.ui")
#		
#		if settingsHelper != None:
#			self.setHelper = settingsHelper
#		else:
#			self.setHelper = SettingsHelper()
#		
		self.lblVariableName = self.findChild(QtWidgets.QLineEdit, "lblVariableName")
		self.lblVariableAddress = self.findChild(QtWidgets.QLineEdit, "lblVariableAddress")
		
		
		
		self.optInt = self.findChild(QtWidgets.QRadioButton, "optInt")
		self.optFloat = self.findChild(QtWidgets.QRadioButton, "optFloat")
		self.optChar = self.findChild(QtWidgets.QRadioButton, "optChar")
		
		self.txtSize = self.findChild(QtWidgets.QLineEdit, "txtSize")
		self.txtSize.setValidator(IntHexValidator())
#		self.txtSize.setInputMask("HHHH;H{0,7}")
		
		self.txtValue = self.findChild(QtWidgets.QLineEdit, "txtValue")
#		line_edit.setValidator(IntHexValidator())
		
#		self.layout = self.tab_first.layout()
#		self.table_widget = self.layout.itemAt(0).widget()
#		
#		self.cmdLoadDefaults.clicked.connect(self.click_loadDefaults)
#		self.cmdTest.clicked.connect(self.click_test)
#		
#		log(f"Loading settings from file: '{self.settings.fileName()}'")
		self.accepted.connect(self.click_saveVar)
#		
		self.loadVariable(self.variable)
#		
	
	def loadVariable(self, var):
		
		self.lblVariableName.setText(var.GetName())
		self.lblVariableAddress.setText(hex(int(var.GetLocation(), 16)))
			# Get the variable's type using GetType()
		self.variable_type = var.GetType()
		print(f"self.variable_type => {self.variable_type}")
		
		value = str(var.GetValue())
		if self.variable_type.GetBasicType() == lldb.eBasicTypeInt:
			self.optInt.setChecked(True)
		elif self.variable_type.GetBasicType() == lldb.eBasicTypeChar: #eBasicTypeChar: # eBasicTypeInvalid
			self.optChar.setChecked(True)
			byte_array = var.GetPointeeData(0, var.GetByteSize())
			error = lldb.SBError()
			sRet = byte_array.GetString(error, 0)
			value = "" if sRet == 0 else sRet
		elif str(self.variable_type.GetName()).startswith("char["):
			print(f"GOT CHAR-ARRAY!!!")
			self.optChar.setChecked(True)
			byte_array = var.GetPointeeData(0, var.GetByteSize())
			error = lldb.SBError()
			sBytes = byte_array.GetString(error, 0)
			value = "" if sBytes == 0 else sBytes
			
		
		self.txtSize.setText(hex(var.GetByteSize()))
		self.txtValue.setText(value)
	
	
	def click_saveVar(self):
		error = lldb.SBError()
		if self.variable_type.GetBasicType() == lldb.eBasicTypeInt:
			self.variable.SetData(lldb.SBData().CreateDataFromSInt32Array(lldb.eByteOrderLittle, int(self.txtSize.text(), 16), [int(self.txtValue.text(), 16)]), error)
		elif str(self.variable_type).startswith("char"):
			self.variable.SetData(lldb.SBData().CreateDataFromCString(lldb.eByteOrderLittle, int(self.txtSize.text(), 16), self.txtValue.text()), error)
			
			pass
			
		if error.Success():
			successMsg = f"Variable '{self.lblVariableName.text()}' with type: '{self.variable_type}' ('{self.variable_type.GetBasicType()}') updated to: {self.txtValue.text()}"
			print(successMsg)
		#			self.window().updateStatusBar(successMsg)
		else:
			print(f"ERROR: {error}")
		pass
		# Update the variable's value using SetData()
#		error = lldb.SBError()
#		var.SetData(lldb.SBData().CreateDataFromSInt32Array(lldb.eByteOrderLittle, 0x1, [0xa]), error)
#		if error.Success():
#			successMsg = f"Variable '{var.GetName()}' with type: '{variable_type}' ('{variable_type.GetBasicType()}') updated to: {var.GetValue()}"
#			print(successMsg)
#			
##			self.window().updateStatusBar(successMsg)
#		else:
#			print(f"ERROR: {error}")