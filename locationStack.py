#!/usr/bin/env python3

#from PyQt6.QtGui import *
from PyQt6.QtCore import *

#from PyQt6.QtWidgets import *
#from PyQt6 import uic, QtWidgets

class LocationStack(QObject):
	
	locationStack = []
	currentLocation = -1
	
	def __init__(self, parent=None):
		super().__init__(parent)
	
	def clearStack(self):
		self.locationStack.clear()
	
	def currentIsLast(self):
		return self.currentLocation >= len(self.locationStack) - 1
	
	def currentIsFirst(self):
		return self.currentLocation <= 0
	
	def pushLocation(self, location):
		if self.currentLocation == -1 or self.locationStack[self.currentLocation] != location:
			del self.locationStack[self.currentLocation+1:]
			self.locationStack.append(location)
			self.currentLocation = len(self.locationStack) - 1
			print(f"Pushing new location: {location}, currentLocation: {self.currentLocation}")
	
	def popLocation(self):
		return self.locationStack.pop()
	
	def locationAt(self, index):
		if index >= 0 and index <= len(self.locationStack) - 1:
			return self.locationStack[index]
		return None
	
	def backLocation(self):
		if self.currentLocation > 0:
			self.currentLocation -= 1
			return self.locationAt(self.currentLocation)
		return None
		
	def forwardLocation(self):
		if self.currentLocation < len(self.locationStack) - 1:
			self.currentLocation += 1
			return self.locationAt(self.currentLocation)
		return None