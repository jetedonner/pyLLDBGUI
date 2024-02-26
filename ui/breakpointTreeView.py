#!/usr/bin/env python3

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from config import *

class EditableTreeItem(QTreeWidgetItem):
	
	isBPEnabled = True
	
	def __init__(self, parent, text):
		super().__init__(parent, text)
#		self.setText(0, text)
#		self.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled)  # Set flags for editing

	def toggleBP(self):
		self.enableBP(not self.isBPEnabled)
	
	def enableBP(self, enabled):
		if self.isBPEnabled and not enabled:
			self.isBPEnabled = False
			self.setIcon(1, ConfigClass.iconBPDisabled)
		elif not self.isBPEnabled and enabled: 
			self.isBPEnabled = True
			self.setIcon(1, ConfigClass.iconBPEnabled)
#	def setData(self, column, role, value):
#		print("SET DATA")
#		# Intercept data setting behavior to handle editing
#		if column == 0 and self.flags() & Qt.ItemFlag.ItemIsEditable:
#			# Create a QLineEdit for editing
##			self.itemAt(event.pos().x(), event.pos().y()).
##			editor = QLineEdit(value)
##			editor.editingFinished.connect(self.editing_finished)
##			self.treeWidget().setCurrentItem(self)
##			self.treeWidget().editItem(self, column, editor)
#			
#			super().setData(column, role, value)
#		else:
#			super().setData(column, role, value)
#		self.treeWidget().closeAllEditors(self)
			
		
#	def __setData(self, column, value):
#		print("SET DATA")
#		# Intercept data setting behavior to handle editing
#		if column == 0 and self.flags() & Qt.ItemFlag.ItemIsEditable:
#			# Create a QLineEdit for editing
##			self.itemAt(event.pos().x(), event.pos().y()).
##			editor = QLineEdit(value)
##			editor.editingFinished.connect(self.editing_finished)
##			self.treeWidget().setCurrentItem(self)
##			self.treeWidget().editItem(self, column, editor)
#			super().__setData(column, value)
#		else:
#			super().__setData(column, value)
			
#	def editing_finished(self):
#		# Handle editing completion and update item text
#		editor = self.treeWidget().itemWidget(self, 0)
#		self.setText(0, editor.text())
		
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
		self.setHeaderLabels(['#', 'State', 'Address', 'Name', 'Hit', 'Condition', 'Commands'])
#		self.header().resizeSection(0, 196)
#		self.header().resizeSection(1, 128)
#		self.header().resizeSection(2, 128)
#		self.header().resizeSection(3, 128)
#		self.header().resizeSection(4, 256)
		self.header().resizeSection(0, 96)
		self.header().resizeSection(1, 56)
		self.header().resizeSection(2, 128)
		self.header().resizeSection(3, 128)
		self.header().resizeSection(4, 128)
		self.header().resizeSection(5, 128)
		self.header().resizeSection(6, 32)
		self.header().resizeSection(7, 48)
		self.header().resizeSection(8, 256)
#		self.treBPs.itemDoubleClicked.connect(self.handle_itemDoubleClicked)
		self.currentItemChanged.connect(self.handle_currentItemChanged)
#		self.currentItem()
#		self.chan
#		self.model().dataChanged.connect(self.handle_return_pressed)
#		self.model().dataChanged.connect(self.handle_tableView_changed)
#		self.tableView_model.dataChanged.connect(self.handle_tableView_changed)
		
#		self.editItem = EditableTreeItem("Double click to edit")
#		self.addTopLevelItem(item)
#		shorcut = QtWidgets.QShortcut(Qt.Key.Key_Return, 
#					self, 
#					context=Qt.ShortcutContext.WidgetShortcut,
#					activated=self.some_function)
	
	def keyPressEvent(self, event):
		print(f'keyPressEvent: {event}')
		return super().keyPressEvent(event)
		
	def event(self, event):
		if isinstance(event, QKeyEvent):
#			print(f"event: {event.key()}")
			if event.key() == Qt.Key.Key_Return:
				print('Return PRESSED!!!')
				if self.isPersistentEditorOpen(self.currentItem(), self.currentColumn()):
#					self.closeAllEditors(self.currentItem())
					self.closePersistentEditor(self.currentItem(), self.currentColumn())
#					return True
				else:
					if self.currentItem().childCount() == 0:
						col = self.currentColumn()
						if col == 3 or col == 5 or col == 6:
							self.openPersistentEditor(self.currentItem(), col)
							self.editItem(self.currentItem(), col)
#						return True
#			print(dir(event))
		return super().event(event)
		
	def some_function(self):
		print("some_function")
		
	def contextMenuEvent(self, event):
		# Show the context menu
		self.context_menu.exec(event.globalPos())
		
	def mouseDoubleClickEvent(self, event):
		daItem = self.itemAt(event.pos().x(), event.pos().y())
#		print(f"MOUSE DOUBLE => Children: {daItem.childCount()}")
		
		col = self.columnAt(event.pos().x())
		if daItem.childCount() > 0:
			super().mouseDoubleClickEvent(event)
		elif col == 0x1:
			daItem.toggleBP()
			if daItem.parent() != None:
#				newEnabled = daItem.isBPEnabled
				allDisabled = True
				for i in range(daItem.parent().childCount()):
					if daItem.parent().child(i).isBPEnabled:
						allDisabled = False
						break
				daItem.parent().enableBP(not allDisabled)
#					aItem.parent().child(i)
		else:
			if col == 3 or col == 5 or col == 6:
				self.openPersistentEditor(daItem, col)
				self.editItem(daItem, col)
#		if col == 5 or col == 6 or (self.columnAt(event.pos().x()) == 0 and daItem.childCount() > 0):
#			super().mouseDoubleClickEvent(event)
#		pass
	
#	def handle_return_pressed(self, editor, one, two):
#		print(f"commitData: {editor}")
##		self.closeAllEditors(editor.parentWidget())
##		editor.close()
#		#		super().commitData(editor)

#	handle_return_pressed
	def handle_tableView_changed(self, index):
		print(f'handle_tableView_changed => {index}')
#		self.closeAllEditors
		
	def handle_currentItemChanged(self, cur, prev):
		print("ITEM CHANGED")
		self.closeAllEditors(prev)
		
	def closeAllEditors(self, item):
		if self.isPersistentEditorOpen(item, 3):
			print("Closing 3")
			self.closePersistentEditor(item, 3)
		if self.isPersistentEditorOpen(item, 5):
			print("Closing 5")
			self.closePersistentEditor(item, 5)
		if self.isPersistentEditorOpen(item, 6):
			print("Closing 6")
			self.closePersistentEditor(item, 6)
#		pass
		
#	def handle_itemDoubleClicked(self, item, col):
##		print(f'ITEM DOUBLECLICKED: {item} => {col}')
#		if col == 5 or col == 6:
##			self.treBPs.closePe
#			self.treBPs.openPersistentEditor(item, col)
#		pass