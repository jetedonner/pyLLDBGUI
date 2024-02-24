#!/usr/bin/env python3

# import psutil
import os
import os.path
import sys
import sre_constants
import re
#import cgi
import html
# import binascii
# import webbrowser
# import ctypes
# import time

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

APP_NAME = "ConsoleTextEditWindow-TEST"
WINDOW_SIZE = 720

APP_VERSION = "v0.0.1"

class QConsoleTextEdit(QTextEdit):
	
	ansi_dict = {"\x1b[30m": "black", "\x1b[31m": "red", "\x1b[32m": "green", "\x1b[33m": "yellow", "\x1b[34m": "blue", "\x1b[35m": "magenta", "\x1b[36m": "cyan", "\x1b[37m": "white", "\x1b[0m": "white", "\x1b[4m": "white", "\x1b[0;30m": "blacklight", "\x1b[0;31m": "IndianRed", "\x1b[0;32m": "LightGreen", "\x1b[0;33m": "LightYellow", "\x1b[0;34m": "LightBlue", "\x1b[0;35m": "LightPink", "\x1b[0;36m": "LightCyan", "\x1b[0;37m": "WhiteSmoke"}
	
	patternEscapedStdAnsi = re.compile(r"\x1b\[\d{1,}[m]")
	patternEscapedLightAnsi = re.compile(r"\x1b\[[0][;]\d{1,}[m]")
	
	def __init__(self):
		super().__init__()
		self.setAcceptRichText(True)

	def setEscapedText(self, text):
		formattedText = self.formatText(text)
#		print(formattedText)
		self.setHtml(formattedText)
	
	def appendEscapedText(self, text, newLine = True):
		htmlText = self.formatText(text)
		if newLine or self.toHtml() == "":
			self.append(htmlText)
		else:
			self.insertHtml(htmlText)
		
	def formatSpecialChars(self, text):
#		text = text.replace("<", "&lt;")
#		text = text.replace(">", "&gt;")
#		text = text.replace("\r\n", "<br/>")
#		text = text.replace("\n", "<br/>")
#		text = text.replace(" ", "&nbsp;")
#		text = text.replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")
#		return text
		text = html.escape(text, True)
		text = text.replace("\r\n", "<br/>\r\n")
		text = text.replace("\n", "<br/>\r\n")
		text = text.replace(" ", "&nbsp;")
		text = text.replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")
		return text
		
	def formatText(self, text):
#		print(text)
		text = self.formatSpecialChars(text)
		ansi_colors = self.patternEscapedStdAnsi.finditer(text)
		formattedText = "<span color='white'>"
		currPos = 0
		for ansi_color in ansi_colors:
#			print(f"-> Single ansi_color: {ansi_color} ({ansi_color.start()} / {ansi_color.end()})")
			formattedText += text[currPos:(ansi_color.start())]
			formattedText += "</span><span style='color: " + self.ansi_dict[ansi_color.group(0)] + "'>"
			currPos = ansi_color.end()
		formattedText += text[currPos:]
		formattedText += "</span>"

		ansi_colors = self.patternEscapedLightAnsi.finditer(formattedText)
		formattedText2 = "<span color='white'>"
		currPos = 0
		for ansi_color in ansi_colors:
#			print(f"-> Single ansi_color: {ansi_color} ({ansi_color.start()} / {ansi_color.end()})")
			formattedText2 += formattedText[currPos:(ansi_color.start())]
			formattedText2 += "</span><span style='color: " + self.ansi_dict[ansi_color.group(0)] + "'>"
			currPos = ansi_color.end()
		# if currPos > 0:
		formattedText2 += formattedText[currPos:]
		formattedText2 += "</span>"

		return formattedText2
	
class QConsoleTextEditWindow(QMainWindow):
	
	mytext = "thread #1: tid = 0xa8f62d, 0x0000000100003f40 hello_world_test_loop`main, queue = \x1b[32m'com.apple.main-thread'\x1b[0m, stop reason = \x1b[31mbreakpoint 1.1\x1b[0m\nthread #2: tid = 0xa8f62d, 0x0000000100003f40 hello_world_test_loop`main, queue = \x1b[35m'com.apple.main-thread'\x1b[0m, stop reason = \x1b[36mbreakpoint 1.1\x1b[0m"
	
	def __init__(self):
		super().__init__()
		self.setWindowTitle(APP_NAME + " " + APP_VERSION)
		self.setBaseSize(WINDOW_SIZE * 2, WINDOW_SIZE)
		self.setMinimumSize(WINDOW_SIZE * 2, WINDOW_SIZE + 72)
		
		self.layout = QHBoxLayout()
		
		self.centralWidget = QWidget(self)
		self.centralWidget.setLayout(self.layout)
		self.setCentralWidget(self.centralWidget)
		self.txtConsole = QConsoleTextEdit()
		self.layout.addWidget(self.txtConsole)
		self.txtConsole.setEscapedText(self.mytext)
		self.txtConsole.appendEscapedText(self.mytext)