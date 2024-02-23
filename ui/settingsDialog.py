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


class SettingsValues(Enum):
	CmdHistory = ("Commands history", True, bool)
	
	
class SettingsHelper(QObject):
	
	settings = QSettings("DaVe_inc", "LLDBPyGUI")
	
	def __init__(self):
		super().__init__()
		
	def initDefaults(self):
		self.settings.setValue(SettingsValues.CmdHistory.value[0], True)
	
	def setChecked(self, setting, checkableItem):
		self.settings.setValue(setting.value[0], checkableItem.checkState() == Qt.CheckState.Checked)
		
	def getChecked(self, setting):
		print(f'self.settings.value(setting.value[0], True, bool) => {self.settings.value(setting.value[0], True, bool)}')
		return Qt.CheckState.Checked if self.settings.value(setting.value[0], setting.value[1], setting.value[1]) else Qt.CheckState.Unchecked
	
	def getValue(self, setting):
		return self.settings.value(setting.value[0], setting.value[1], setting.value[2])
	
class SettingsDialog(QDialog):
	
	settings = QSettings("DaVe_inc", "LLDBPyGUI")
	setHelper = None
	
	def initDefaults(self):
		self.settings.setValue(SettingsValues.CmdHistory.value[0], True)
	
	
	def __init__(self, settingsHelper = None):
		super().__init__()
		
		# loading the ui file with uic module
		project_root = dirname(realpath(__file__))
		settingsDialogPath = os.path.join(project_root, '..', 'resources', 'designer', 'settingsDialog.ui')
		
		uic.loadUi(settingsDialogPath, self)
		print("AFTER INIT settingsDialog.ui")
		
		if settingsHelper != None:
			self.setHelper = settingsHelper
		else:
			self.setHelper = SettingsHelper()
		
		self.tab_first = self.findChild(QtWidgets.QWidget, "tab")
		self.layout = self.tab_first.layout()
		self.table_widget = self.layout.itemAt(0).widget()
		
		self.cmdLoadDefaults.clicked.connect(self.click_loadDefaults)
		self.cmdTest.clicked.connect(self.click_test)
#		self.settings.setVal
#		self.settings.setValue("TestSetting", "TESTVALUE")
		
		name = self.settings.value("TestSetting", "")
		print(name)
		print(f'SETTINGS-FILE: {self.settings.fileName()}')
		self.accepted.connect(self.click_saveSettings)
		
		self.loadSettings()
		
	def loadSettings(self):
		self.table_widget.item(3, 1).setCheckState(self.setHelper.getChecked(SettingsValues.CmdHistory))
		pass
		
	def click_test(self):
		print(f'{SettingsValues.CmdHistory.value[0]} => {self.settings.value(SettingsValues.CmdHistory.value[0], False)}')
		
	def click_loadDefaults(self):
		self.initDefaults()
		
	def click_saveSettings(self):
		print(f'GOING TO SAVE SETTINGS !!!!')
		
		print(f'IsChecked: {self.table_widget.item(3, 1).checkState() == Qt.CheckState.Checked}')
		print(f'Save Hist: {self.table_widget.item(3, 1).text()}')
		
		self.setHelper.setChecked(SettingsValues.CmdHistory, self.table_widget.item(3, 1))