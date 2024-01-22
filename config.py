#!/usr/bin/env python3
import os

from os.path import abspath
from os.path import dirname, realpath
from os import getcwd, path

import sys

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets


#global font
class ConfigClass():
	font = QFont("Courier New")
	font.setFixedPitch(True)
	
	supportURL = "https://pylldbgui.kimhauser.ch/support"
	githubURL = "https://github.com/jetedonner/pyLLDBGUI"
	
	toolbarIconSize = 24
	
	iconStd = None
	iconBPEnabled = None
	iconBPDisabled = None
	
	@staticmethod
	def initIcons():
		project_root = dirname(realpath(__file__))
		resources_root = os.path.join(project_root, 'resources')
#		print(project_root)
		ConfigClass.iconStd = QIcon()
		ConfigClass.iconBPEnabled = QIcon(os.path.join(resources_root, 'bug.png'))
		ConfigClass.iconBPDisabled = QIcon(os.path.join(resources_root, 'bug_bw_greyscale.png'))
		
#	iconBPEnabled = QIcon(os.path.join("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/resources/", 'bug.png'))
#	iconBPDisabled = QIcon(os.path.join("/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/pyLLDBGUI/resources/", 'bug_bw_greyscale.png'))