#!/usr/bin/env python3

import os
import sys

from enum import Enum
#import re	
	
from os.path import abspath
from os.path import dirname, realpath
from os import getcwd, path

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from config import *
from helper.dbgHelper import *


#class SettingsValues(Enum):
#	ConfirmRestartTarget = ("Confirm restart target", True, bool)
#	ConfirmQuitApp = ("Confirm quit app", True, bool)
#	DisassemblerShowQuickTooltip = ("Disassembler show QuickTooltip", True, bool)
#	CmdHistory = ("Commands history", True, bool)
#	MemViewShowSelectedStatubarMsg = ("Memory-Viewer on select show statusbar message", True, bool)
		
#class SettingsHelper(QObject):
#	
#	settings = QSettings(ConfigClass.companyName, ConfigClass.appName)
#	
#	def __init__(self):
#		super().__init__()
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
##		print(f'self.settings.value(setting.value[0], True, bool) => {self.settings.value(setting.value[0], True, bool)} / Key: {setting.value[0]} / Default: {setting.value[1]} / Datatype: {setting.value[2]}')
##		if self.settings.value(setting.value[0], setting.value[1], setting.value[2]):
##			print(f'IF => YESSSSSSS!!!!!')
##		else:
##			print(f'IF => NOOOOOOOOO!!!!!')
#		return Qt.CheckState.Checked if self.settings.value(setting.value[0], setting.value[1], setting.value[2]) else Qt.CheckState.Unchecked
#	
#	def getValue(self, setting):
#		return self.settings.value(setting.value[0], setting.value[1], setting.value[2])
	
class AddBreakpointDialog(QDialog):
	
#	settings = QSettings("DaVe_inc", "LLDBPyGUI")
#	setHelper = None
	
#	def initDefaults(self):
#		self.settings.setValue(SettingsValues.ConfirmRestartTarget.value[0], True)
#		self.settings.setValue(SettingsValues.ConfirmQuitApp.value[0], True)
#		self.settings.setValue(SettingsValues.DisassemblerShowQuickTooltip.value[0], True)
#		self.settings.setValue(SettingsValues.CmdHistory.value[0], True)
#		self.settings.setValue(SettingsValues.MemViewShowSelectedStatubarMsg.value[0], True)
	
	def __init__(self):
		super().__init__()
		
#		self.initDefaults()
		
		# loading the ui file with uic module
		project_root = dirname(realpath(__file__))
		addBreakpointDialogPath = os.path.join(project_root, '..', 'resources', 'designer', 'addBreakpointDialog.ui')
		
		uic.loadUi(addBreakpointDialogPath, self)
#		print("AFTER INIT settingsDialog.ui")
		
#		if settingsHelper != None:
#			self.setHelper = settingsHelper
#		else:
#			self.setHelper = SettingsHelper()
#		
		self.lblAddress = self.findChild(QtWidgets.QLabel, "lblAddress")
		
		self.optByAddress = self.findChild(QtWidgets.QRadioButton, "optByAddress")
		self.optByAddress.toggled.connect(self.handle_ByAddress_Toggled)
		self.optByName = self.findChild(QtWidgets.QRadioButton, "optByName")
		self.optByName.toggled.connect(self.handle_ByName_Toggled)
		self.optForException = self.findChild(QtWidgets.QRadioButton, "optForException")
		self.optForException.toggled.connect(self.handle_ByException_Toggled)
		self.optByRegExp = self.findChild(QtWidgets.QRadioButton, "optByRegExp")
		self.optByRegExp.toggled.connect(self.handle_ByRegExp_Toggled)
		
	def handle_ByAddress_Toggled(self, checked):
		if checked:
			self.lblAddress.setText("Address:")
			
	def handle_ByName_Toggled(self, checked):
		if checked:
			self.lblAddress.setText("Name:")
	
	def handle_ByException_Toggled(self, checked):
		if checked:
			self.lblAddress.setText("Exception:")
	
	def handle_ByRegExp_Toggled(self, checked):
		if checked:
			self.lblAddress.setText("Regular Expression:")

#		self.layout = self.tab_first.layout()
#		self.table_widget = self.layout.itemAt(0).widget()
#		
#		self.cmdLoadDefaults.clicked.connect(self.click_loadDefaults)
#		self.cmdTest.clicked.connect(self.click_test)
#		
#		log(f"Loading settings from file: '{self.settings.fileName()}'")
#		self.accepted.connect(self.click_saveSettings)
#		
#		self.loadSettings()
#		
#	def loadSettings(self):
#		self.table_widget.item(0, 1).setCheckState(self.setHelper.getChecked(SettingsValues.ConfirmRestartTarget))
#		self.table_widget.item(1, 1).setCheckState(self.setHelper.getChecked(SettingsValues.ConfirmQuitApp))
#		self.table_widget.item(2, 1).setCheckState(self.setHelper.getChecked(SettingsValues.DisassemblerShowQuickTooltip))
#		self.table_widget.item(3, 1).setCheckState(self.setHelper.getChecked(SettingsValues.CmdHistory))
#		self.table_widget.item(4, 1).setCheckState(self.setHelper.getChecked(SettingsValues.MemViewShowSelectedStatubarMsg))
#		
#	def click_test(self):
#		print(f'{SettingsValues.CmdHistory.value[0]} => {self.settings.value(SettingsValues.CmdHistory.value[0], False)}')
#		
#	def click_loadDefaults(self):
#		self.initDefaults()
#		
#	def click_saveSettings(self):
#		self.setHelper.setChecked(SettingsValues.ConfirmRestartTarget, self.table_widget.item(0, 1))
#		self.setHelper.setChecked(SettingsValues.ConfirmQuitApp, self.table_widget.item(1, 1))
#		self.setHelper.setChecked(SettingsValues.DisassemblerShowQuickTooltip, self.table_widget.item(2, 1))
#		self.setHelper.setChecked(SettingsValues.CmdHistory, self.table_widget.item(3, 1))
#		self.setHelper.setChecked(SettingsValues.MemViewShowSelectedStatubarMsg, self.table_widget.item(4, 1))