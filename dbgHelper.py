#!/usr/bin/env python3

from enum import Enum

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
#		flags = ""
#		if flag and cls.MH_NOUNDEFS.value:
#			flags += "MH_NOUNDEFS "
#		if flag and cls.MH_INCRLINK.value:
#			flags += "MH_INCRLINK "
#		if flag and cls.MH_DYLDLINK.value:
#			flags += "MH_DYLDLINK "
#			
#		return flags