#!/usr/bin/env python3

import lldb

class VariablesHelper():
	
	driver = None
	
	def __init__(self, driver):
		self.driver = driver
	
	@staticmethod
	def GetVariable(driver, varName):
		return VariablesHelper(driver).getVariable(varName)
	
	def getVariable(self, varName):
		# Get the frame object from the current debugging session
		frame = self.driver.getTarget().GetProcess().GetThreadAtIndex(0).GetFrameAtIndex(0)
		
		# Get the variable you want to modify by name
		var = frame.FindVariable(varName)
		return var
	
	@staticmethod
	def SetVariableDataInt(driver, varName, data, byteOrder = lldb.eByteOrderLittle):
		return VariablesHelper(driver).setVariableDataInt(varName, data, byteOrder)
	
	def setVariableDataInt(self, varName, data, byteOrder = lldb.eByteOrderLittle):
		var = self.getVariable(varName)
		if var:
			error = lldb.SBError()
			if var.GetType().GetBasicType() == lldb.eBasicTypeInt:
				var.SetData(lldb.SBData().CreateDataFromSInt32Array(byteOrder, var.GetByteSize(), [data]), error)
				
			if error.Success():
				successMsg = f"Variable '{varName}' with type: '{var.GetType()}' ('{var.GetType().GetBasicType()}') updated to: {data}"
				print(successMsg)
#				self.window().updateStatusBar(successMsg)
			#			self.window().updateStatusBar(successMsg)
				return True
			else:
				print(f"ERROR: {error}")
				
		return False