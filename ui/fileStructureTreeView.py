#!/usr/bin/env python3

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from config import *

class FileStructureTreeWidget(QTreeWidget):
	
#	actionShowMemory = None
	
	def __init__(self):
		super().__init__()
#       self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
		self.context_menu = QMenu(self)
		actionShowInfos = self.context_menu.addAction("Show infos")
		
		self.actionShowMemoryFrom = self.context_menu.addAction("Show memory")
		self.actionShowMemoryTo = self.context_menu.addAction("Show memory after End")
		
		self.setFont(ConfigClass.font)
		self.setHeaderLabels(['Sections / Symbols', 'Address From', 'Address To', 'File-Size', 'Byte-Size', 'Type'])
		self.header().resizeSection(0, 196)
		self.header().resizeSection(1, 128)
		self.header().resizeSection(2, 128)
		self.header().resizeSection(3, 128)
		self.header().resizeSection(4, 256)
		
	def contextMenuEvent(self, event):
		# Show the context menu
		self.context_menu.exec(event.globalPos())