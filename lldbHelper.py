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