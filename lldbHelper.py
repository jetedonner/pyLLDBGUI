#!/usr/bin/env python3
import lldb
import enum

from ctypes import *
from struct import *
from binascii import *

exec2Dbg = None
debugger = None
target = None
process = None
thread = None

class MachoFileType(enum.Enum):
	# Mach haeder "filetype" constants
	MH_OBJECT = 0x00000001
	MH_EXECUTE = 0x00000002
	MH_FVMLIB = 0x00000003
	MH_CORE = 0x00000004
	MH_PRELOAD = 0x00000005
	MH_DYLIB = 0x00000006
	MH_DYLINKER = 0x00000007
	MH_BUNDLE = 0x00000008
	MH_DYLIB_STUB = 0x00000009
	MH_DSYM = 0x0000000A
	MH_KEXT_BUNDLE = 0x0000000B
	
	def create_filetype_value(value):
		# Create an enum value from an integer
		return MachoFileType.__new__(MachoFileType, value)
	
	@classmethod
	def to_str(cls, magic):
		if magic == cls.MH_OBJECT:
			return "MH_OBJECT"
		elif magic == cls.MH_EXECUTE:
			return "MH_EXECUTE"
		elif magic == cls.MH_FVMLIB:
			return "MH_FVMLIB"
		elif magic == cls.MH_CORE:
			return "MH_CORE"
		elif magic == cls.MH_PRELOAD:
			return "MH_PRELOAD"
		elif magic == cls.MH_DYLIB:
			return "MH_DYLIB"
		elif magic == cls.MH_DYLINKER:
			return "MH_DYLINKER"
		elif magic == cls.MH_BUNDLE:
			return "MH_BUNDLE"
		elif magic == cls.MH_DYLIB_STUB:
			return "MH_DYLIB_STUB"
		elif magic == cls.MH_DSYM:
			return "MH_DSYM"
		elif magic == cls.MH_KEXT_BUNDLE:
			return "MH_KEXT_BUNDLE"
		else:
			return "UNKNOWN"
		

class MachoMagic(enum.Enum):	
	# Mach header "magic" constants
	MH_MAGIC = 0xfeedface
	MH_CIGAM = 0xcefaedfe
	MH_MAGIC_64 = 0xfeedfacf
	MH_CIGAM_64 = 0xcffaedfe
	FAT_MAGIC = 0xcafebabe
	FAT_CIGAM = 0xbebafeca
	
#	@classmethod
	def create_magic_value(value):
		# Create an enum value from an integer
		return MachoMagic.__new__(MachoMagic, value)
	
	@classmethod
	def to_str(cls, magic):
		if magic == cls.MH_MAGIC:
			return "MH_MAGIC"
		elif magic == cls.MH_CIGAM:
			return "MH_CIGAM"
		elif magic == cls.MH_MAGIC_64:
			return "MH_MAGIC_64"
		elif magic == cls.MH_CIGAM_64:
			return "MH_CIGAM_64"
		elif magic == cls.FAT_MAGIC:
			return "FAT_MAGIC"
		elif magic == cls.FAT_CIGAM:
			return "FAT_CIGAM"
		else:
			return "UNKNOWN"

# Thanks for MACH* part of the code - Jonathan Salwan
class MACH_HEADER(Structure):
	_fields_ = [
				("magic",           c_uint),
				("cputype",         c_uint),
				("cpusubtype",      c_uint),
				("filetype",        c_uint),
				("ncmds",           c_uint),
				("sizeofcmds",      c_uint),
				("flags",           c_uint)
				]
				
def GetFileHeader(exe):
	with open(exe,'rb') as fopen:
		data = bytearray(fopen.read())
		mach_header = MACH_HEADER.from_buffer_copy(data)
#		print(mach_header.magic)
		return mach_header
	return None

def GuessLanguage(frame):
	return lldb.SBLanguageRuntime.GetNameForLanguageType(frame.GuessLanguage())

#class lldbHelper():
#	
#	def GuessLanguage(self, frame):
#		return lldb.SBLanguageRuntime.GetNameForLanguageType(frame.GuessLanguage())

def SectionTypeString(secType):
	if secType == lldb.eSectionTypeInvalid: # = _lldb.eSectionTypeInvalid
		return "Invalid"
	elif secType == lldb.eSectionTypeCode:
		return "Code"
	elif secType == lldb.eSectionTypeContainer:
		return "Container"
	elif secType == lldb.eSectionTypeData:
		return "Data"
	elif secType == lldb.eSectionTypeDataCString:
		return "DataCString"
	elif secType == lldb.eSectionTypeDataCStringPointers:
		return "DataCStringPointers"
	elif secType == lldb.eSectionTypeDataSymbolAddress:
		return "DataSymbolAddress"
	elif secType == lldb.eSectionTypeData4:
		return "Data4"
	elif secType == lldb.eSectionTypeData8:
		return "Data8"
	elif secType == lldb.eSectionTypeData16:
		return "Data16"
	elif secType == lldb.eSectionTypeDataPointers:
		return "DataPointers"
	elif secType == lldb.eSectionTypeDebug:
		return "Debug"
	elif secType == lldb.eSectionTypeZeroFill:
		return "ZeroFill"
	elif secType == lldb.eSectionTypeDataObjCMessageRefs: 
		return 'DataObjCMessageRefs'
	elif secType == lldb.eSectionTypeDataObjCCFStrings: 
		return 'DataObjCCFStrings'
	elif secType == lldb.eSectionTypeDWARFDebugAbbrev: 
		return 'DWARFDebugAbbrev'	
	elif secType == lldb.eSectionTypeDWARFDebugAddr: 
		return 'DWARFDebugAddr'	
	elif secType == lldb.eSectionTypeDWARFDebugAranges: 
		return 'DWARFDebugAranges'
	elif secType == lldb.eSectionTypeDWARFDebugCuIndex: 
		return 'DWARFDebugCuIndex'
	elif secType == lldb.eSectionTypeDWARFDebugFrame: 
		return 'DWARFDebugFrame'
	elif secType == lldb.eSectionTypeDWARFDebugInfo: 
		return 'DWARFDebugInfo'
	elif secType == lldb.eSectionTypeDWARFDebugLine: 
		return 'DWARFDebugLine'
	elif secType == lldb.eSectionTypeDWARFDebugLoc: 
		return 'DWARFDebugLoc'
	elif secType == lldb.eSectionTypeDWARFDebugMacInfo: 
		return 'DWARFDebugMacInfo'
	elif secType == lldb.eSectionTypeDWARFDebugMacro: 
		return 'DWARFDebugMacro'
	elif secType == lldb.eSectionTypeDWARFDebugPubNames: 
		return 'DWARFDebugPubNames'
	elif secType == lldb.eSectionTypeDWARFDebugPubTypes: 
		return 'DWARFDebugPubTypes'
	elif secType == lldb.eSectionTypeDWARFDebugRanges: 
		return 'DWARFDebugRanges'
	elif secType == lldb.eSectionTypeDWARFDebugStr: 
		return 'DWARFDebugStr'
	elif secType == lldb.eSectionTypeDWARFDebugStrOffsets: 
		return 'DWARFDebugStrOffsets'
	elif secType == lldb.eSectionTypeDWARFAppleNames: 
		return 'DWARFAppleNames'
	elif secType == lldb.eSectionTypeDWARFAppleTypes: 
		return 'DWARFAppleTypes'
	elif secType == lldb.eSectionTypeDWARFAppleNamespaces: 
		return 'DWARFAppleNamespaces'
	elif secType == lldb.eSectionTypeDWARFAppleObjC: 
		return 'DWARFAppleObjC'
	elif secType == lldb.eSectionTypeELFSymbolTable: 
		return 'ELFSymbolTable'
	elif secType == lldb.eSectionTypeELFDynamicSymbols: 
		return 'ELFDynamicSymbols'
	elif secType == lldb.eSectionTypeELFRelocationEntries: 
		return 'ELFRelocationEntries'
	elif secType == lldb.eSectionTypeELFDynamicLinkInfo: 
		return 'ELFDynamicLinkInfo'
	elif secType == lldb.eSectionTypeEHFrame: 
		return 'EHFrame'
	elif secType == lldb.eSectionTypeARMexidx: 
		return 'ARMexidx'
	elif secType == lldb.eSectionTypeARMextab: 
		return 'ARMextab'
	elif secType == lldb.eSectionTypeCompactUnwind: 
		return 'CompactUnwind'
	elif secType == lldb.eSectionTypeGoSymtab: 
		return 'GoSymtab'
	elif secType == lldb.eSectionTypeAbsoluteAddress: 
		return 'AbsoluteAddress'
	elif secType == lldb.eSectionTypeDWARFGNUDebugAltLink: 
		return 'DWARFGNUDebugAltLink'
	elif secType == lldb.eSectionTypeDWARFDebugTypes: 
		return 'DWARFDebugTypes'
	elif secType == lldb.eSectionTypeDWARFDebugNames: 
		return 'DWARFDebugNames'
	elif secType == lldb.eSectionTypeOther: 
		return 'Other'
	elif secType == lldb.eSectionTypeDWARFDebugLineStr: 
		return 'DWARFDebugLineStr'
	elif secType == lldb.eSectionTypeDWARFDebugRngLists: 
		return 'DWARFDebugRngLists'
	elif secType == lldb.eSectionTypeDWARFDebugLocLists: 
		return 'DWARFDebugLocLists'
	elif secType == lldb.eSectionTypeDWARFDebugAbbrevDwo: 
		return 'DWARFDebugAbbrevDwo'
	elif secType == lldb.eSectionTypeDWARFDebugInfoDwo: 
		return 'DWARFDebugInfoDwo'
	elif secType == lldb.eSectionTypeDWARFDebugStrDwo: 
		return 'DWARFDebugStrDwo'
	elif secType == lldb.eSectionTypeDWARFDebugStrOffsetsDwo: 
		return 'DWARFDebugStrOffsetsDwo'
	elif secType == lldb.eSectionTypeDWARFDebugTypesDwo: 
		return 'DWARFDebugTypesDwo'
	elif secType == lldb.eSectionTypeDWARFDebugRngListsDwo: 
		return 'DWARFDebugRngListsDwo'
	elif secType == lldb.eSectionTypeDWARFDebugLocDwo: 
		return 'DWARFDebugLocDwo'
	elif secType == lldb.eSectionTypeDWARFDebugLocListsDwo: 
		return 'DWARFDebugLocListsDwo'
	elif secType == lldb.eSectionTypeDWARFDebugTuIndex: 
		return 'DWARFDebugTuIndex'
	elif secType == lldb.eSectionTypeCTF: 
		return 'CTF'	
	elif secType == lldb.eSectionTypeSwiftModules: 
		return 'SwiftModules'
	else:
		return "Other"