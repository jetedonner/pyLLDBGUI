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
	
	companyName = "DaVe_inc"
	appName = "LLDBPyGUI"
	
	initialCommand = "breakpoint set -a 0x100003f6a" # re read
	font = QFont("Courier New") # ("Monaco") #("Courier New")
#	font.setFixedPitch(True)
	
	supportURL = "https://pylldbgui.kimhauser.ch/support"
	githubURL = "https://github.com/jetedonner/pyLLDBGUI"
	testBPsFilename = "/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/LLDBPyGUI/testtarget/testbps_withSubFunc5.json"
	testTarget = "/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/LLDBPyGUI/testtarget/hello_world_test"
	testTargetSource = "/Volumes/Data/dev/_reversing/disassembler/pyLLDBGUI/LLDBPyGUI/testtarget/hello_world_test.c"
	
	toolbarIconSize = 24
	currentDebuggerSubTab = 1
	
	iconLeft = None
	iconRight = None
	
	iconGears = None
	iconGearsGrey = None
	iconAdd = None
	iconSave = None
	iconLoad = None
	iconReload = None
	iconInfo = None
	
	pixGears = None
	pixGearsGrey = None
	pixBug = None
	pixBugGreen = None
	pixAdd = None
	pixInfo = None
	pixSave = None
	pixLoad = None
	pixReload = None
	pixTrash = None
	
	iconEyeRed = None
	iconEyeGrey = None
	iconEyeGreen = None
	
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
	
	colorGreen = QColor(0, 255, 0, 128)
	colorTransparent = QColor(0, 0, 0, 0)
	
	@staticmethod
	def initIcons():
		project_root = dirname(realpath(__file__))
		resources_root = os.path.join(project_root, 'resources', 'img')
		
		ConfigClass.iconStd = QIcon()
		
		ConfigClass.pixGears = QPixmap(os.path.join(resources_root, 'gears.png')).scaled(QSize(48, 48))
		ConfigClass.pixGearsGrey = QPixmap(os.path.join(resources_root, 'gears_grey.png')).scaled(QSize(48, 48))
		ConfigClass.pixBug = QPixmap(os.path.join(resources_root, 'bug.png')).scaled(QSize(18, 18))
		ConfigClass.pixBugGreen = QPixmap(os.path.join(resources_root, 'bug_green2.png')).scaled(QSize(18, 18))
		ConfigClass.pixAdd = QPixmap(os.path.join(resources_root, 'add.png')).scaled(QSize(18, 18))
		ConfigClass.pixSave = QPixmap(os.path.join(resources_root, 'save.png')).scaled(QSize(18, 18))
		ConfigClass.pixLoad = QPixmap(os.path.join(resources_root, 'folder.png')).scaled(QSize(18, 18))
		ConfigClass.pixReload = QPixmap(os.path.join(resources_root, 'reload.png')).scaled(QSize(18, 18))
		ConfigClass.pixInfo = QPixmap(os.path.join(resources_root, 'info.png')).scaled(QSize(18, 18))
		ConfigClass.pixTrash = QPixmap(os.path.join(resources_root, 'delete.png')).scaled(QSize(18, 18))
#		ui->label->setStyleSheet("border-image:url(:/2.png);");
#		ui->label->setPixmap(pix);
		
		
		
		ConfigClass.iconLeft = QIcon(os.path.join(resources_root, 'left-arrow_blue.png'))
		ConfigClass.iconRight = QIcon(os.path.join(resources_root, 'right-arrow_blue.png'))
		
		ConfigClass.iconGears = QIcon(os.path.join(resources_root, 'gears.png'))
		ConfigClass.iconGearsGrey = QIcon(os.path.join(resources_root, 'gears_grey.png'))
		
		ConfigClass.iconAdd = QIcon(os.path.join(resources_root, 'add.png'))
		ConfigClass.iconSave = QIcon(os.path.join(resources_root, 'save.png'))
		ConfigClass.iconLoad = QIcon(os.path.join(resources_root, 'folder.png'))
		ConfigClass.iconInfo = QIcon(os.path.join(resources_root, 'info.png'))
		
		ConfigClass.iconEyeRed = QIcon(os.path.join(resources_root, 'Eye_Red.png'))
		ConfigClass.iconEyeGrey = QIcon(os.path.join(resources_root, 'Eye_Grey.png'))
		ConfigClass.iconEyeGreen = QIcon(os.path.join(resources_root, 'Eye_Green.png'))
		
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
		
		
		