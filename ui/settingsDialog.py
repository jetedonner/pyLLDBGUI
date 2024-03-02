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


class SettingsValues(Enum):
	ConfirmRestartTarget = ("Confirm restart target", True, bool)
	ConfirmQuitApp = ("Confirm quit app", True, bool)
	DisassemblerShowQuickTooltip = ("Disassembler show QuickTooltip", True, bool)
	CmdHistory = ("Commands history", True, bool)
	MemViewShowSelectedStatubarMsg = ("Memory-Viewer on select show statusbar message", True, bool)
	VisualizeCurrentBP = ("Visualise current breakpoint", True, bool)
	UseNativeDialogs = ("Use native dialogs", True, bool)
		
class SettingsHelper(QObject):
	
	settings = QSettings(ConfigClass.companyName, ConfigClass.appName)
	
	def __init__(self):
		super().__init__()
		
	@staticmethod
	def getSettings():
		return QSettings(ConfigClass.companyName, ConfigClass.appName)
		
	@staticmethod
	def GetChecked(setting):
		return SettingsHelper().getChecked(setting)
	
	@staticmethod
	def GetValue(setting):
		return SettingsHelper().getValue(setting)
	
	def initDefaults(self):
		self.settings.setValue(SettingsValues.ConfirmRestartTarget.value[0], True)
		self.settings.setValue(SettingsValues.ConfirmQuitApp.value[0], True)
		self.settings.setValue(SettingsValues.DisassemblerShowQuickTooltip.value[0], True)
		self.settings.setValue(SettingsValues.CmdHistory.value[0], True)
		self.settings.setValue(SettingsValues.MemViewShowSelectedStatubarMsg.value[0], True)
		self.settings.setValue(SettingsValues.VisualizeCurrentBP.value[0], True)
		self.settings.setValue(SettingsValues.UseNativeDialogs.value[0], True)
	
	def setChecked(self, setting, checkableItem):
		self.settings.setValue(setting.value[0], checkableItem.checkState() == Qt.CheckState.Checked)
		
	def getChecked(self, setting):
		return Qt.CheckState.Checked if self.settings.value(setting.value[0], setting.value[1], setting.value[2]) else Qt.CheckState.Unchecked
	
#	def getBool(self, setting):
#		return True if self.settings.value(setting.value[0], setting.value[1], setting.value[2]) else False
	
	def getValue(self, setting):
		return self.settings.value(setting.value[0], setting.value[1], setting.value[2])
	
class SettingsDialog(QDialog):
	
	settings = QSettings("DaVe_inc", "LLDBPyGUI")
	setHelper = None
	
	def initDefaults(self):
		self.settings.setValue(SettingsValues.ConfirmRestartTarget.value[0], True)
		self.settings.setValue(SettingsValues.ConfirmQuitApp.value[0], True)
		self.settings.setValue(SettingsValues.DisassemblerShowQuickTooltip.value[0], True)
		self.settings.setValue(SettingsValues.CmdHistory.value[0], True)
		self.settings.setValue(SettingsValues.MemViewShowSelectedStatubarMsg.value[0], True)
		self.settings.setValue(SettingsValues.VisualizeCurrentBP.value[0], True)
		self.settings.setValue(SettingsValues.UseNativeDialogs.value[0], True)
	
	def __init__(self, settingsHelper = None):
		super().__init__()
		
#		self.initDefaults()
		
		# loading the ui file with uic module
		project_root = dirname(realpath(__file__))
		settingsDialogPath = os.path.join(project_root, '..', 'resources', 'designer', 'settingsDialog.ui')
		
		uic.loadUi(settingsDialogPath, self)
#		print("AFTER INIT settingsDialog.ui")
		
		if settingsHelper != None:
			self.setHelper = settingsHelper
		else:
			self.setHelper = SettingsHelper()
		
		self.tab_first = self.findChild(QtWidgets.QWidget, "tab")
		self.layout = self.tab_first.layout()
		self.table_widget = self.layout.itemAt(0).widget()
		
		self.cmdLoadDefaults.clicked.connect(self.click_loadDefaults)
		self.cmdTest.clicked.connect(self.click_test)
		
		log(f"Loading settings from file: '{self.settings.fileName()}'")
		self.accepted.connect(self.click_saveSettings)
		
		self.loadSettings()
		
	def loadSettings(self):
		for i in range(2):
			self.table_widget.item(0, i).setCheckState(self.setHelper.getChecked(SettingsValues.ConfirmRestartTarget))
			self.table_widget.item(1, i).setCheckState(self.setHelper.getChecked(SettingsValues.ConfirmQuitApp))
			self.table_widget.item(2, 1).setCheckState(self.setHelper.getChecked(SettingsValues.DisassemblerShowQuickTooltip))
			self.table_widget.item(3, i).setCheckState(self.setHelper.getChecked(SettingsValues.CmdHistory))
			self.table_widget.item(4, 1).setCheckState(self.setHelper.getChecked(SettingsValues.MemViewShowSelectedStatubarMsg))
			self.table_widget.item(5, i).setCheckState(self.setHelper.getChecked(SettingsValues.VisualizeCurrentBP))
			self.table_widget.item(6, i).setCheckState(self.setHelper.getChecked(SettingsValues.UseNativeDialogs))
		
	def click_test(self):
		print(f'{SettingsValues.CmdHistory.value[0]} => {self.settings.value(SettingsValues.CmdHistory.value[0], False)}')
		
	def click_loadDefaults(self):
		self.initDefaults()
		
	def click_saveSettings(self):
		colCheckBox = 0
		self.setHelper.setChecked(SettingsValues.ConfirmRestartTarget, self.table_widget.item(0, colCheckBox))
		self.setHelper.setChecked(SettingsValues.ConfirmQuitApp, self.table_widget.item(1, colCheckBox))
		self.setHelper.setChecked(SettingsValues.DisassemblerShowQuickTooltip, self.table_widget.item(2, colCheckBox))
		self.setHelper.setChecked(SettingsValues.CmdHistory, self.table_widget.item(3, colCheckBox))
		self.setHelper.setChecked(SettingsValues.MemViewShowSelectedStatubarMsg, self.table_widget.item(4, colCheckBox))
		self.setHelper.setChecked(SettingsValues.VisualizeCurrentBP, self.table_widget.item(5, colCheckBox))
		self.setHelper.setChecked(SettingsValues.UseNativeDialogs, self.table_widget.item(6, colCheckBox))