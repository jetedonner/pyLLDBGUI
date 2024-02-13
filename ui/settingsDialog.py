#!/usr/bin/env python3

import os
import sys

from os.path import abspath
from os.path import dirname, realpath
from os import getcwd, path

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

class SettingsDialog(QDialog):
	def __init__(self):
		super().__init__()
		
		# loading the ui file with uic module
		project_root = dirname(realpath(__file__))
		settingsDialogPath = os.path.join(project_root, '..', 'resources', 'designer', 'settingsDialog.ui')
		
		uic.loadUi(settingsDialogPath, self)
		print("AFTER INIT settingsDialog.ui")
		
		settings = QSettings("DaVe_inc", "LLDBPyGUI")
#		settings.setValue("TestSetting", "TESTVALUE")
		
		name = settings.value("TestSetting", "")
		print(name)
#		self.initTable()
		
#	def initTable(self):
#		self.tableView.setColumnCount(3)
#		self.setColumnWidth(0, 48)
#		self.setColumnWidth(1, 48)
#		self.setColumnWidth(2, 512)
##		self.setColumnWidth(3, 108)
##		self.setColumnWidth(4, 32)
##		self.setColumnWidth(5, 256)
##		self.setColumnWidth(5, 324)
##		self.setColumnWidth(6, 304)
#		self.verticalHeader().hide()
#		self.horizontalHeader().show()
#		self.horizontalHeader().setHighlightSections(False)
#		self.setHorizontalHeaderLabels(['Key', 'Value', 'Description'])#, 'Instruction', 'Hex', 'Comment'])
#		self.horizontalHeaderItem(0).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
#		self.horizontalHeaderItem(1).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
#		self.horizontalHeaderItem(2).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
##		self.horizontalHeaderItem(3).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
##		self.horizontalHeaderItem(4).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
##		self.horizontalHeaderItem(5).setTextAlignment(Qt.AlignmentFlag.AlignVCenter)
##		self.horizontalHeaderItem(5).setTextAlignment(Qt.AlignmentFlag.AlignLeft)
##		self.horizontalHeaderItem(6).setTextAlignment(Qt.AlignmentFlag.AlignLeft)
##		self.setFont(ConfigClass.font)
##		
#		self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
#		self.setShowGrid(False)
##		self.cellDoubleClicked.connect(self.on_double_click)
#		pass