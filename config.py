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

class ConfigClass():
	
	font = QFont("Courier New")
#	font.setFixedPitch(True)
	
	supportURL = "https://pylldbgui.kimhauser.ch/support"
	githubURL = "https://github.com/jetedonner/pyLLDBGUI"
	
	toolbarIconSize = 24
	
	iconBug = None
	iconBugGreen = None
	iconStd = None
	iconBPEnabled = None
	iconBPDisabled = None
	iconBin = None
	iconPause = None
	iconPlay = None
	iconSettings = None
	
	iconStepOver = None
	iconStepInto = None
	iconStepOut = None
	
	iconResume = None
	
	iconRestart = None
	iconStop = None
	
	iconGithub = None
	
	@staticmethod
	def initIcons():
		project_root = dirname(realpath(__file__))
		resources_root = os.path.join(project_root, 'resources')
		
		ConfigClass.iconStd = QIcon()
		ConfigClass.iconBug = QIcon(os.path.join(resources_root, 'bug.png'))
		ConfigClass.iconBugGreen = QIcon(os.path.join(resources_root, 'bug_green2.png'))
		ConfigClass.iconBPEnabled = QIcon(os.path.join(resources_root, 'bug.png'))
		ConfigClass.iconBPDisabled = QIcon(os.path.join(resources_root, 'bug_bw_greyscale.png'))
		ConfigClass.iconBin = QIcon(os.path.join(resources_root, 'recyclebin.png'))
		ConfigClass.iconPause = QIcon(os.path.join(resources_root, 'pause-circular-button.png'))
		ConfigClass.iconPlay = QIcon(os.path.join(resources_root, 'play-circular-button.png'))
		ConfigClass.iconSettings = QIcon(os.path.join(resources_root, 'settings.png'))
		
		ConfigClass.iconStepOver = QIcon(os.path.join(resources_root, 'step_over_ng2.png'))
		ConfigClass.iconStepInto = QIcon(os.path.join(resources_root, 'step_into.png'))
		ConfigClass.iconStepOut = QIcon(os.path.join(resources_root, 'step_out_ng.png'))
		
		ConfigClass.iconResume = QIcon(os.path.join(resources_root, 'Resume.png'))
		ConfigClass.iconStepOver = QIcon(os.path.join(resources_root, 'StepOver.png'))
		ConfigClass.iconStepInto = QIcon(os.path.join(resources_root, 'StepInto.png'))
		ConfigClass.iconStepOut = QIcon(os.path.join(resources_root, 'StepOut.png'))
		ConfigClass.iconRestart = QIcon(os.path.join(resources_root, 'Restart.png'))
		ConfigClass.iconStop = QIcon(os.path.join(resources_root, 'Stop.png'))
		
		ConfigClass.iconGithub = QIcon(os.path.join(resources_root, 'github.png'))
		
		
		