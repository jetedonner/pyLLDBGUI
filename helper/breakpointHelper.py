#!/usr/bin/env python3

import lldb
import os
import sys
import re
import pyperclip

from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6 import uic, QtWidgets
from config import *

class BreakpointHelper():
	
	table = None
	colNum = 1
	colCond = 5
	
	window = None
	driver = None
	
	def __init__(self, window, driver):
		self.window = window
		self.driver = driver
		
		
	def handle_saveBreakpoints(self, target, filepath):
		path_spec = lldb.SBFileSpec(filepath)
		target.BreakpointsWriteToFile(path_spec)
		pass
		
#	@staticmethod
	def handle_editCondition(self, table, colNum, colCond):
		if len(table.selectedItems()) > 0:
			self.table = table
			self.colNum = colNum
			self.colCond = colCond
			itemNum = self.table.item(self.table.selectedItems()[0].row(), self.colNum)
			itemCond = self.table.item(self.table.selectedItems()[0].row(), self.colCond)
			title = f'Condition of breakpoint {itemNum.text()}'
			label = f'Edit the condition of breakpoint {itemNum.text()}'
			
			dialog = QInputDialog()
			dialog.setWindowTitle(title)
			dialog.setLabelText(label)
			self.oldCond = itemCond.text()
			dialog.setTextValue(self.oldCond)
			dialog.textValueChanged.connect(self.handle_editConditionChanged)
			dialog.resize(512, 128)
			# Show the dialog and get the selected process name
			if dialog.exec():
				# OK pressed
	#			print(f'self.table.window =====>>>> {self.table.window()}')
#				idx = 0
#				for i in range(target.GetNumBreakpoints()):
#					idx += 1
				bp_cur = self.table.window().driver.getTarget().GetBreakpointAtIndex(self.table.selectedItems()[0].row())
				bp_cur.SetCondition(itemCond.text())
				print(self.table.window().updateStatusBar(f"Breakpoint ({itemNum.text()}) condition changed successfully"))
				pass
			else:
				itemCond.setText(self.oldCond)
	
#	@staticmethod
	def handle_editConditionChanged(self, text):
		if len(self.table.selectedItems()) > 0:
			itemCond = self.table.item(self.table.selectedItems()[0].row(), self.colCond)
			itemCond.setText(text)
			
	def handle_enableBP(self, address, enabled = True):
		print(f'handle_enableBP: {address} => {enabled}')
		target = self.driver.getTarget()
		for i in range(target.GetNumBreakpoints()):
			bp = self.driver.getTarget().GetBreakpointAtIndex(i)
			found = False
			for j in range(bp.GetNumLocations()):
				bl = bp.GetLocationAtIndex(j)
				if hex(bl.GetAddress().GetLoadAddress(target)) == address:
#					bp_cur = self.driver.getTarget().GetBreakpointAtIndex(bpId)
					bl.SetEnabled(enabled)
					bp.SetEnabled(enabled)
					found = True
					break
			if found:
				break
		
	def handle_checkBPExists(self, address):
		bpRet = None
		print(f'handle_checkBPExists: {address}')
		target = self.driver.getTarget()
		for i in range(target.GetNumBreakpoints()):
			bp = self.driver.getTarget().GetBreakpointAtIndex(i)
			found = False
			for j in range(bp.GetNumLocations()):
				bl = bp.GetLocationAtIndex(j)
				if hex(bl.GetAddress().GetLoadAddress(target)) == address:
					bpRet = bp
##					bp_cur = self.driver.getTarget().GetBreakpointAtIndex(bpId)
#					bp.SetEnabled(enabled)
					found = True
					break
			if found:
				break
		print(f'handle_checkBPExists => Found: {bpRet}')
		return bpRet
		
	def handle_deleteBP(self, bpId, enabled = True):
		print(f'handle_enableBP: {bpId} => {enabled}')
		target = self.driver.getTarget()
		if target.BreakpointDelete(int(bpId)):
			print(f"Breakpoint (ID: {bpId}) deleted successfully!")
			return True
		else:
			print(f"Breakpoint (ID: {bpId}) COULD NOT BE DELETED!")
			return False
#		for i in range(target.GetNumBreakpoints()):
#			bp = self.driver.getTarget().GetBreakpointAtIndex(i)
#			found = False
#			for j in range(bp.GetNumLocations()):
#				bl = bp.GetLocationAtIndex(j)
#				if hex(bl.GetAddress().GetLoadAddress(target)) == bpId:
##					bp_cur = self.driver.getTarget().GetBreakpointAtIndex(bpId)
##					bp_cur.SetEnabled(enabled)
#					found = True
#					break
#			if found:
#				break
		pass
		
	def handle_deleteAllBPs(self):
		print(f'handle_deleteAllBPs!!!')
		self.driver.getTarget().DeleteAllBreakpoints()