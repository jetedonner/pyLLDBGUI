#!/usr/bin/env python3
import lldb

debugger = None
target = None
process = None
thread = None

def GuessLanguage(frame):
	return lldb.SBLanguageRuntime.GetNameForLanguageType(frame.GuessLanguage())

#class lldbHelper():
#	
#	def GuessLanguage(self, frame):
#		return lldb.SBLanguageRuntime.GetNameForLanguageType(frame.GuessLanguage())