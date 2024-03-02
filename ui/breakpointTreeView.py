#!/usr/bin/env python3
import lldb

from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets

from helper.breakpointHelper import *
from config import *

class EditableTreeItem(QTreeWidgetItem):
	
	isBPEnabled = True
	textEdited = pyqtSignal(object, int, str)
	
	def __init__(self, parent, text):
		super().__init__(parent, text)
#		self.setText(0, text)
#		self.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled)  # Set flags for editing

	def toggleBP(self):
		self.enableBP(not self.isBPEnabled)
	
	def enableBP(self, enabled):
		if self.isBPEnabled and not enabled:
			self.isBPEnabled = False
			self.setIcon(1, ConfigClass.iconBug)
			print(f'ENABLING BP!!!!!!!!!!!!!!!!!!!')
		elif not self.isBPEnabled and enabled: 
			self.isBPEnabled = True
			self.setIcon(1, ConfigClass.iconBugGreen)
		else:
			if enabled:
				self.setIcon(1, ConfigClass.iconBugGreen) 
			else:
				self.setIcon(1, ConfigClass.iconBug) 
	
	
	
#	def setData(self, column, role, value):
#		print(f"SET DATA {column}")
#		# Intercept data setting behavior to handle editing
#		if column == 5: # and self.flags() & Qt.ItemFlag.ItemIsEditable:
#			print(f'Column {column} was edited')
#			# Create a QLineEdit for editing
#			#			self.itemAt(event.pos().x(), event.pos().y()).
#			#			editor = QLineEdit(value)
#			#			editor.editingFinished.connect(self.editing_finished)
#			#			self.treeWidget().setCurrentItem(self)
#			#			self.treeWidget().editItem(self, column, editor)
#			
#		super().setData(column, role, value)
		
#		self.textEdited.emit(self, column, value)
		
			
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
	
	def __init__(self, driver):
		super().__init__()
		self.driver = driver
#       self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
		self.breakpointHelper = BreakpointHelper(self.window(), self.driver)
		self.context_menu = QMenu(self)
		
		self.actionShowInfos = self.context_menu.addAction("Show infos")
		self.context_menu.addSeparator()
		self.actionEnableBP = self.context_menu.addAction("Enable / Disable Breakpoint")
		self.actionDeleteBP = self.context_menu.addAction("Delete Breakpoint")
		self.actionDeleteBP.triggered.connect(self.handle_deleteBP)
		self.actionEnableAllBP = self.context_menu.addAction("Enable All Breakpoints")
		self.actionDisableAllBP = self.context_menu.addAction("Disable All Breakpoints")
		self.context_menu.addSeparator()
		
		self.actionShowMemoryFrom = self.context_menu.addAction("Show memory")
		self.actionShowMemoryTo = self.context_menu.addAction("Show memory after End")
		self.context_menu.addSeparator()
		self.actionGoToAddress = self.context_menu.addAction("GoTo address")
		self.actionGoToAddress.triggered.connect(self.handle_gotoAddr)
		
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
		self.setMouseTracking(True)
#		self.treBPs.itemDoubleClicked.connect(self.handle_itemDoubleClicked)
		self.currentItemChanged.connect(self.handle_currentItemChanged)
		self.itemChanged.connect(self.handle_itemChanged)
		self.itemEntered.connect(self.handle_itemEntered)

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
	
#	def keyPressEvent(self, event):
#		print(f'keyPressEvent: {event}')
#		return super().keyPressEvent(event)
		
#	self.window().wdtBPsWPs.treBPs.viewAddress
	
	def setPC(self, address, setPC=True):
		items = self.getAllItemsAndSubitems()
		for item in items:
			for subitem in item.subItems:
				if int(subitem.text(2), 16) == int(address, 16):
#					if self.invisibleRootItem().child(childPar).child(childChild).text(2) == address:
#						print(f'FOUND ADDRESS FOR PC: {address}')
					if setPC:
						for i in range(subitem.columnCount()):
							subitem.setBackground(i, ConfigClass.colorGreen)
					self.scrollToItem(subitem, 
						QAbstractItemView.ScrollHint.PositionAtCenter)
					if not setPC:
						break
				else:
					if setPC:
						for i in range(subitem.columnCount()):
							subitem.setBackground(i, ConfigClass.colorTransparent)
						
#		for childPar in range(self.invisibleRootItem().childCount()):
#			for childChild in range(self.invisibleRootItem().child(childPar).childCount()):
#				if self.invisibleRootItem().child(childPar).child(childChild) != None:
##					print(f'self.invisibleRootItem().child(childPar).child(childChild): {self.invisibleRootItem().child(childPar).child(childChild).text(2)} / {address}')
#					if int(self.invisibleRootItem().child(childPar).child(childChild).text(2), 16) == int(address, 16):
##					if self.invisibleRootItem().child(childPar).child(childChild).text(2) == address:
##						print(f'FOUND ADDRESS FOR PC: {address}')
#						for i in range(self.invisibleRootItem().child(childPar).child(childChild).columnCount()):
#							self.invisibleRootItem().child(childPar).child(childChild).setBackground(i, ConfigClass.colorGreen)
#						self.scrollToItem(self.invisibleRootItem().child(childPar).child(childChild), 
#							QAbstractItemView.ScrollHint.PositionAtCenter)
#					else:
#						for i in range(self.invisibleRootItem().child(childPar).child(childChild).columnCount()):
#							self.invisibleRootItem().child(childPar).child(childChild).setBackground(i, ConfigClass.colorTransparent)

	def handle_deleteBP(self):
		print(f"Going to delete Breakpoint: {self.currentItem().text(0)}")
		if self.breakpointHelper.handle_deleteBP(self.currentItem().text(0)):
			print(f"Breakpoint: {self.currentItem().text(0)} deleted SUCCESSFULLY")
#			self.currentItem().parent().removeChild(self.currentItem())
			# Get the index of the item to remove
			index = self.currentIndex()
			
			# Check if a valid item is selected
			if index.isValid():
				# Remove and delete the item
				removed_item = self.takeTopLevelItem(index.row())
				del removed_item  # Alternatively, you can use removed_item.delete()
		else:
			print(f"Breakpoint: {self.currentItem().text(0)} COULD NOT BE deleted!!!")
		
		pass
		
	def handle_gotoAddr(self):
		newAddr = self.currentItem().text(2)
		if newAddr != "":
			self.window().txtMultiline.viewAddress(newAddr)
			
	oldBPName = ""
	def handle_itemEntered(self, item, col):
		if col == 1:
			item.setToolTip(col, "State: " + str(item.isBPEnabled))
			
		self.oldBPName = item.text(3)
		pass
		
	def event(self, event):
		if isinstance(event, QKeyEvent):
#			print(f"event: {event.key()}")
			if event.key() == Qt.Key.Key_Return:
				if self.isPersistentEditorOpen(self.currentItem(), self.currentColumn()):
					self.closePersistentEditor(self.currentItem(), self.currentColumn())
#					return True
				else:
					if self.currentItem().childCount() == 0:
						col = self.currentColumn()
						if col == 3 or col == 5 or col == 6:
							self.openPersistentEditor(self.currentItem(), col)
							self.editItem(self.currentItem(), col)
		return super().event(event)

	def contextMenuEvent(self, event):
		self.context_menu.exec(event.globalPos())
	
	def handle_itemChanged(self, item, col):
		print(f'ITEM CHANGED => {item.text(col)} / {col}')
		if col == 5 and item.childCount() == 0:
#			print(f"UPDATEING BP Condition of BP {item.text(0)} to '{item.text(col)}'")
			target = self.window().driver.getTarget()
			
			for i in range(target.GetNumBreakpoints()):
				bp = target.GetBreakpointAtIndex(i)
				for bl in bp:
					if item.text(0) == str(bp.GetID()) + "." + str(bl.GetID()):
						bp.SetCondition(item.text(col))
						bl.SetCondition(item.text(col))
						rootItem = self.invisibleRootItem()
						for childPar in range(rootItem.childCount()):
							parentItem = rootItem.child(childPar)
							if parentItem.text(0) == str(bp.GetID()):
#								parentItem.setText(4, str(bp.GetHitCount()))
								if item.text(col) != None and item.text(col) != "":
									parentItem.setText(5, str(item.text(col)))
								else:
									parentItem.setText(5, "")
								break
#						print(f"GOT BP {item.text(0)}")
						break
		elif col == 3 and item.childCount() == 0:
#			print(f"UPDATEING BP-NAME: {item.text(0)} => {item.text(col)}")
			target = self.window().driver.getTarget()
			bpFound = False
			for i in range(target.GetNumBreakpoints()):
				bp = target.GetBreakpointAtIndex(i)
				for bl in bp:
					name_list = lldb.SBStringList()
					bp.GetNames(name_list)
					num_names = name_list.GetSize()
					name_list.AppendString("")
					num_names = 1
					for j in range(num_names):
						name = name_list.GetStringAtIndex(j)
						if name == self.oldBPName:
							bp.RemoveName(self.oldBPName)
							bp.AddName(item.text(col))
							bpFound = True
							break
					if bpFound:
						break
		
	def getAllItemsAndSubitems(self):
		itemsRet = []
		for childPar in range(self.invisibleRootItem().childCount()):
			itemsRet.append(self.invisibleRootItem().child(childPar))
			itemsRet[-1].subItems = []
			for childChild in range(self.invisibleRootItem().child(childPar).childCount()):
				if self.invisibleRootItem().child(childPar).child(childChild) != None:
					itemsRet[-1].subItems.append(self.invisibleRootItem().child(childPar).child(childChild))
#					self.invisibleRootItem().child(childPar).child(childChild).enableBP(True)
				
		return itemsRet
					
	def enableAllBPs():
		for childPar in range(self.invisibleRootItem().childCount()):
			for childChild in range(self.invisibleRootItem().child(childPar).childCount()):
				if self.invisibleRootItem().child(childPar).child(childChild) != None:
					self.invisibleRootItem().child(childPar).child(childChild).enableBP(True)
		pass
		
	def enableBPByAddress(self, address, enabled):
		for childPar in range(self.invisibleRootItem().childCount()):
			for childChild in range(self.invisibleRootItem().child(childPar).childCount()):
				if self.invisibleRootItem().child(childPar).child(childChild) != None:
					print(f'self.invisibleRootItem().child(childPar).child(childChild): {self.invisibleRootItem().child(childPar).child(childChild).text(2)} / {address}')
					if self.invisibleRootItem().child(childPar).child(childChild).text(2) == address:
						self.invisibleRootItem().child(childPar).child(childChild).enableBP(enabled)
#						if daItem.parent() != None:
		#				newEnabled = daItem.isBPEnabled
						allDisabled = True
						for i in range(self.invisibleRootItem().child(childPar).childCount()):
							if self.invisibleRootItem().child(childPar).child(i).isBPEnabled:
								allDisabled = False
								break
						self.invisibleRootItem().child(childPar).enableBP(not allDisabled)
						break
		pass
		
	def mouseDoubleClickEvent(self, event):
		daItem = self.itemAt(event.pos().x(), event.pos().y())
#		print(f"MOUSE DOUBLE => Children: {daItem.childCount()}")
		
		col = self.columnAt(event.pos().x())
		if daItem.childCount() > 0:
			super().mouseDoubleClickEvent(event)
		elif col == 1:
			
			daItem.toggleBP()
			self.window().txtMultiline.table.enableBP(daItem.text(2), daItem.isBPEnabled)
			self.breakpointHelper.handle_enableBP(daItem.text(2), daItem.isBPEnabled)
			if daItem.parent() != None:
#				newEnabled = daItem.isBPEnabled
				allDisabled = True
				for i in range(daItem.parent().childCount()):
					if daItem.parent().child(i).isBPEnabled:
						allDisabled = False
						break
				daItem.parent().enableBP(not allDisabled)
#					aItem.parent().child(i)
		elif col == 2:
			self.window().txtMultiline.viewAddress(daItem.text(2))
			pass
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
#		print("ITEM CHANGED")
		self.closeAllEditors(prev)
		
	def closeAllEditors(self, item):
		if self.isPersistentEditorOpen(item, 3):
#			print("Closing 3")
			self.closePersistentEditor(item, 3)
		if self.isPersistentEditorOpen(item, 5):
#			print("Closing 5")
			self.closePersistentEditor(item, 5)
		if self.isPersistentEditorOpen(item, 6):
#			print("Closing 6")
			self.closePersistentEditor(item, 6)
#		pass
		
#	def handle_itemDoubleClicked(self, item, col):
##		print(f'ITEM DOUBLECLICKED: {item} => {col}')
#		if col == 5 or col == 6:
##			self.treBPs.closePe
#			self.treBPs.openPersistentEditor(item, col)
#		pass