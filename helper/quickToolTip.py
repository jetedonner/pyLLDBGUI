#!/usr/bin/env python3
import lldb
import re
import codecs
import struct

class QuickToolTip:
	operandMemPrefixes = ("dword ptr", "word ptr", "byte ptr", "[")
		
	def get_memory_addressAndOperands(self, debugger, operands):
		strOp = self.extractOperand(operands)
		return self.get_memory_address(debugger, strOp), strOp

	def get_memory_address(self, debugger, expression):
		target = debugger.GetSelectedTarget()
		process = target.GetProcess()
		thread = process.GetSelectedThread()
		frame = thread.GetSelectedFrame()
		
		isMinus = True
		parts = expression.split("-")
		if len(parts) <= 1:
			parts = expression.split("+")
			isMinus = False
			
		if len(parts) == 2:
			rbp_value = frame.EvaluateExpression(f"${parts[0]}").GetValueAsUnsigned()
			# Calculate the desired memory address
			offset_value = int(parts[1].replace("0x", ""), 16)
			if isMinus:
				address = rbp_value - offset_value
			else:
				address = rbp_value + offset_value
				
#		print(f"Memory address: 0x{address:X}")
		return address

	def extractOperand(self, string):
#		string = "dword ptr [rbp - 0x8]"
		pattern = r"\[([^\]]+)\]"  # Match anything within square brackets, excluding the brackets themselves
		match = re.search(pattern, string)
		
		if match:
			extracted_text = match.group(1)  # Access the captured group
#			print(extracted_text)  # Output: rbp - 0x8
			return extracted_text.replace(" ", "")
		else:
			print("No match found")
			return ""

	def splitOperands(self, openrands):
		parts = openrands.split(",")
		if len(parts) >= 2:
			return parts[0].strip(), parts[1].strip()
		else:
			return parts[0].strip(), ""
	
	def getOperandsText(self, openrands):
		operandsText = ""
		
		part1, part2 = self.splitOperands(openrands)
		if part1.startswith(self.operandMemPrefixes):
			operandsText = self.extractOperand(part1)
		elif part2.startswith(self.operandMemPrefixes):
			operandsText = self.extractOperand(part2)
		else:
			pass
		return operandsText
	
	def doReadMemory(self, address, size = 0x100):
#		self.window().tabWidgetDbg.setCurrentWidget(self.window().tabMemory)
##		self.txtMemoryAddr = QLineEdit("0x100003f50")
##		self.txtMemorySize = QLineEdit("0x100")
#		self.window().txtMemoryAddr.setText(hex(address))
#		self.window().txtMemorySize.setText(hex(size))
#		try:
##           global debugger
#			self.handle_readMemory(self.driver.debugger, int(self.window().txtMemoryAddr.text(), 16), int(self.window().txtMemorySize.text(), 16))
#		except Exception as e:
#			print(f"Error while reading memory from process: {e}")
		pass
			
	def getQuickToolTip(self, openrands, debugger):
		tooltip = ""				
		
		address = 0
		operandsText = self.getOperandsText(openrands)
		if operandsText != "":
			address = self.get_memory_address(debugger, operandsText)

		if address != 0:
			tooltip = f'Addr:\t{hex(address)}'
			error_ref = lldb.SBError()
			process = debugger.GetSelectedTarget().GetProcess()
			memory = process.ReadMemory(address, 0x20, error_ref)
			if error_ref.Success():
				dataTillNull = self.extract_data_until_null(memory)
				print(dataTillNull)
				string = codecs.decode(dataTillNull, 'utf-8', errors='ignore')
				
#				isNum = False
#				try:
#					float(string[0])
##					testint = ord(string[0])
#					isNum = True
#				except ValueError:
#					isNum = False
##				if len(string) == 2:
##					string2 = "Hello, world!"
##					first_char_int = ord(string2[0])  # Get the ASCII code using ord()
##					
##					print(first_char_int)  # Output: 72 (ASCII code for 'H')
##					print(f'len({string}) == {len(string)} => ord({string[0]}) == {ord(string[0])}')
				
#				first_byte_hex = f"{dataTillNull[0]:02x}"
#				print(f'CHAR: ({first_byte_hex} / {int(first_byte_hex, 16)})')
#				
#				print(f'STRING: ({string})')
				if dataTillNull != b'\x00' and string != '': # and not isNum:
					tooltip += f'\nString:\t{string}'
					
				try:
					value = struct.unpack('<H', dataTillNull)[0]
					tooltip += f'\nInt:\t{value}'
				except Exception as e:
#					print(f'Error extracting INT: {e}')
					pass
					
#				if len(dataTillNull) <= 1:
				tooltip += f'\nBytes:\t{dataTillNull}'
#				else:
#					tooltip += f'\nBytes:\t{dataTillNull[:-1]}'
			else:
				print(str(error_ref))
				tooltip = str(error_ref)
		
		return tooltip
	
	def extract_data_until_null(self, byte_data):
		null_index = byte_data.find(b'\x00')
		if null_index != -1:
			return byte_data[:null_index + 1]
		else:
			return None