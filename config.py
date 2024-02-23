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
	
	initialCommand = "breakpoint set -a 0x100003f6a" # re read
	font = QFont("Courier New") # ("Monaco") #("Courier New")
#	font.setFixedPitch(True)
	
	supportURL = "https://pylldbgui.kimhauser.ch/support"
	githubURL = "https://github.com/jetedonner/pyLLDBGUI"
	testBPsFilename = "/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/LLDBPyGUI/testtarget/testbps_withSubFunc3.json"
	
	toolbarIconSize = 24
	
	iconSave = None
	iconLoad = None
	iconReload = None
	iconInfo = None
	pixInfo = None
	pixSave = None
	pixLoad = None
	pixReload = None
	pixTrash = None
	
	iconEyeRed = None
	
	iconBug = None
	iconBugGreen = None
	iconStd = None
	iconBPEnabled = None
	iconBPDisabled = None
	iconBin = None
	iconPause = None
	iconPlay = None
	iconSettings = None
	iconTrash = None
	
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
		resources_root = os.path.join(project_root, 'resources', 'img')
		
		ConfigClass.iconStd = QIcon()
		
		ConfigClass.pixSave = QPixmap(os.path.join(resources_root, 'save.png')).scaled(QSize(18, 18))
		ConfigClass.pixLoad = QPixmap(os.path.join(resources_root, 'folder.png')).scaled(QSize(18, 18))
		ConfigClass.pixReload = QPixmap(os.path.join(resources_root, 'reload.png')).scaled(QSize(18, 18))
		ConfigClass.pixInfo = QPixmap(os.path.join(resources_root, 'info.png')).scaled(QSize(18, 18))
		ConfigClass.pixTrash = QPixmap(os.path.join(resources_root, 'delete.png')).scaled(QSize(18, 18))
#		ui->label->setStyleSheet("border-image:url(:/2.png);");
#		ui->label->setPixmap(pix);
		
		ConfigClass.iconSave = QIcon(os.path.join(resources_root, 'save.png'))
		ConfigClass.iconLoad = QIcon(os.path.join(resources_root, 'folder.png'))
		ConfigClass.iconInfo = QIcon(os.path.join(resources_root, 'info.png'))
		ConfigClass.iconEyeRed = QIcon(os.path.join(resources_root, 'Eye_Red.png'))
		ConfigClass.iconBug = QIcon(os.path.join(resources_root, 'bug.png'))
		ConfigClass.iconBugGreen = QIcon(os.path.join(resources_root, 'bug_green2.png'))
		ConfigClass.iconBPEnabled = QIcon(os.path.join(resources_root, 'bug.png'))
		ConfigClass.iconBPDisabled = QIcon(os.path.join(resources_root, 'bug_bw_greyscale.png'))
		ConfigClass.iconBin = QIcon(os.path.join(resources_root, 'recyclebin.png'))
		ConfigClass.iconPause = QIcon(os.path.join(resources_root, 'Pause_first.png'))
		ConfigClass.iconPlay = QIcon(os.path.join(resources_root, 'play-circular-button.png'))
		ConfigClass.iconSettings = QIcon(os.path.join(resources_root, 'settings.png'))
		ConfigClass.iconTrash = QIcon(os.path.join(resources_root, 'delete.png'))
		
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
		
		
		