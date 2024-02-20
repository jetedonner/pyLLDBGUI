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
	CmdHistory = ("Commands history", bool)
	
	
class SettingsHelper(QObject):
	
	settings = QSettings("DaVe_inc", "LLDBPyGUI")
	
	def __init__(self):
		super().__init__()
		
	def initDefaults(self):
		self.settings.setValue(SettingsValues.CmdHistory.value[0], True)
		
	def getValue(self, setting):
		return self.settings.value(setting.value[0], None)
	
class SettingsDialog(QDialog):
	
	settings = QSettings("DaVe_inc", "LLDBPyGUI")
	
	def initDefaults(self):
		self.settings.setValue(SettingsValues.CmdHistory.value[0], True)
	
	
	def __init__(self):
		super().__init__()
		
		# loading the ui file with uic module
		project_root = dirname(realpath(__file__))
		settingsDialogPath = os.path.join(project_root, '..', 'resources', 'designer', 'settingsDialog.ui')
		
		uic.loadUi(settingsDialogPath, self)
		print("AFTER INIT settingsDialog.ui")
		
		self.cmdLoadDefaults.clicked.connect(self.click_loadDefaults)
		self.cmdTest.clicked.connect(self.click_test)
#		self.settings.setVal
#		self.settings.setValue("TestSetting", "TESTVALUE")
		
		name = self.settings.value("TestSetting", "")
		print(name)
		print(f'SETTINGS-FILE: {self.settings.fileName()}')
		self.accepted.connect(self.click_saveSettings)
		
	def click_test(self):
		print(f'{SettingsValues.CmdHistory.value[0]} => {self.settings.value(SettingsValues.CmdHistory.value[0], False)}')
		
	def click_loadDefaults(self):
		self.initDefaults()
		
	def click_saveSettings(self):
		print(f'GOING TO SAVE SETTINGS !!!!')
		self.tab_widget = self.findChild(QtWidgets.QTabWidget, "tabWidget")
		print(f'self.tab_widget: {self.tab_widget}')
		self.tbl_settings = self.tab_widget.findChild(QtWidgets.QTableWidget, "tblSettings")
		print(f'self.tbl_settings: {self.tbl_settings}')
		
		self.tab_first = self.tab_widget.findChild(QtWidgets.QWidget, "tab")
		print(f'self.tab: {self.tab_first}')
		
		self.tbl_settings2 = self.tab_first.findChild(QtWidgets.QTableWidget, "tblSettings")
		print(f'self.tbl_settings2: {self.tbl_settings2}')
		
		layout = self.tab_first.layout()
		self.table_widget = layout.itemAt(0).widget()
		print(self.table_widget)
		
		
		print(f'IsChecked: {self.table_widget.item(3, 1).checkState() == Qt.CheckState.Checked}')
		print(f'Save Hist: {self.table_widget.item(3, 1).text()}')