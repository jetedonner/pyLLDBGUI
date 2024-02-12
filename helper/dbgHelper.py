#!/usr/bin/env python3

import lldb
from enum import Enum
import re

class DbgLogLevel(Enum):
	NONE = 1
	STD = 2
	EXTENDED = 4
	VERBOSE = 8
	
#class DbgMsg():
	
dbgMode:bool = True
dbgLogLevel = DbgLogLevel.STD

#@classmethod
def log(msg, dbgLogLevelOverwrite = DbgLogLevel.STD):
	if dbgLogLevelOverwrite.value >= dbgLogLevel.value:
		print(msg)

def read_memory(process, address, size):
	error = lldb.SBError()
	target = process.GetTarget()
	
	# Read memory using ReadMemory function
	data = target.ReadMemory(address, size, error)
	
	if error.Success():
		return data
	else:
		print("Error reading memory:", error)
		return None
	
def getMemoryValueAtAddress(target, process, address):
	memoryValue = ""
	try:
		# Specify the memory address and size you want to read
		size = 32  # Adjust the size based on your data type (e.g., int, float)
		
		# Read memory and print the result
		data = read_memory(process, target.ResolveLoadAddress(int(address, 16)), size)
		hex_string = ''.join("%02x" % byte for byte in data)
		memoryValue = ' '.join(re.findall(r'.{2}', hex_string))
#		memoryValue = formatted_hex_string
	except Exception as e:
#		print(f"Error getting memory for addr: {e}")
		pass
	return memoryValue