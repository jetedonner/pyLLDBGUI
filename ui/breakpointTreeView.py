#!/usr/bin/env python3

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from config import *

class EditableTreeItem(QTreeWidgetItem):
	
	def __init__(self, text):
		super().__init__()
		self.setText(0, text)
		self.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled)  # Set flags for editing
		
	def __setData(self, column, value):
		# Intercept data setting behavior to handle editing
		if column == 0 and self.flags() & Qt.ItemFlag.ItemIsEditable:
			# Create a QLineEdit for editing
			editor = QLineEdit(value)
			editor.editingFinished.connect(self.editing_finished)
			self.treeWidget().setCurrentItem(self)
			self.treeWidget().editItem(self, column, editor)
		else:
			super().__setData(column, value)
			
	def editing_finished(self):
		# Handle editing completion and update item text
		editor = self.treeWidget().itemWidget(self, 0)
		self.setText(0, editor.text())
		
class BreakpointTreeWidget(QTreeWidget):
	
#	actionShowMemory = None
	
	def __init__(self):
		super().__init__()
#       self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
		self.context_menu = QMenu(self)
		actionShowInfos = self.context_menu.addAction("Show infos")
		
		self.actionShowMemoryFrom = self.context_menu.addAction("Show memory")
		self.actionShowMemoryTo = self.context_menu.addAction("Show memory after End")
		
		self.setFont(ConfigClass.font)
#		self.setSelectionModel(QItemSelectionModel())
		self.setHeaderLabels(['State', '#', 'Address', 'Name', 'Hit', 'Condition', 'Commands'])
#		self.header().resizeSection(0, 196)
#		self.header().resizeSection(1, 128)
#		self.header().resizeSection(2, 128)
#		self.header().resizeSection(3, 128)
#		self.header().resizeSection(4, 256)
		self.header().resizeSection(0, 24)
		self.header().resizeSection(1, 32)
		self.header().resizeSection(2, 128)
		self.header().resizeSection(3, 128)
		self.header().resizeSection(4, 128)
		self.header().resizeSection(5, 128)
		self.header().resizeSection(6, 32)
		self.header().resizeSection(7, 48)
		self.header().resizeSection(8, 256)
		
		self.editItem = EditableTreeItem("Double click to edit")
#		self.addTopLevelItem(item)
		
	def contextMenuEvent(self, event):
		# Show the context menu
		self.context_menu.exec(event.globalPos())
		
	def mouseDoubleClickEvent(self, event):
		# Ignore double-click events to prevent expansion
		print("MOUSE DOUBLE CLICKEDICLICK !!!!")
		print(self.itemAt(event.pos().x(), event.pos().y()).text(self.columnAt(event.pos().x())))
		self.itemAt(event.pos().x(), event.pos().y())
		col = self.columnAt(event.pos().x())
		if col == 5 or col == 6:
			super().mouseDoubleClickEvent(event)
#		print(self.columnAt(event.pos().x()))
		pass