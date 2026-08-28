from bparse import *

import tomllib

with open('bellow_metadata.toml', 'rb') as f:
	configs = tomllib.load(f)

BELLOW_MAJOR_VERSION = configs['version']['major_version']
BELLOW_MINOR_VERSION = configs['version']['minor_version']
BELLOW_PATCH_VERSION = configs['version']['patch_version']
MAX_BELLOW_ARGS = configs['bellow']['max_args']

BELLOW_SIGNATURE = bytes.fromhex('badfaced')

class BCodeGen:
	def __init__(self, program):
		self.program = program

	def generate_bellow_code(self):
		generated_code = []

		for i in self.program.instructions:
			new_instruct = [i.keyword.value - 1]

			for arg in i.args:
				arg_mode = arg.mode.value - 1

				if arg.type == ArgumentType.IDENTIFIER:
					declaration = find_declaration_using_name(self.program, arg.value)
					new_instruct.append((arg_mode, declaration.value))
				elif arg.type == ArgumentType.NUMBER:
					new_instruct.append((arg_mode, arg.value))

			while (len(new_instruct) - 1) < MAX_BELLOW_ARGS:
				new_instruct.append((0,0))

			#print(new_instruct)
			generated_code.append(new_instruct)

		return generated_code

def save_to_file(generated_code, filename):
	with open(filename, 'wb') as file:
		file.write(BELLOW_SIGNATURE)

		file.write(BELLOW_MAJOR_VERSION.to_bytes(4, 'big'))
		file.write(BELLOW_MINOR_VERSION.to_bytes(4, 'big'))
		file.write(BELLOW_PATCH_VERSION.to_bytes(4, 'big'))

		file.write(len(generated_code).to_bytes(4, 'big'))

		for instruction in generated_code:
			for integer in instruction:
				if isinstance(integer, tuple):
					file.write(integer[0].to_bytes(4, 'big'))
					file.write(integer[1].to_bytes(4, 'big'))
				else:
					file.write(integer.to_bytes(4, 'big'))

def load_program(filename):
	program = []
	with open(filename, 'rb') as file:
		magic_word = file.read(4)

		if magic_word.hex() != BELLOW_SIGNATURE.hex():
			print(f'[I/O Error] Invalid Bellow signature {magic_word.hex()}')
			return None

		major_version = int.from_bytes(file.read(4), 'big')
		minor_version = int.from_bytes(file.read(4), 'big')
		patch_version = int.from_bytes(file.read(4), 'big')

		file_version = f'{major_version}.{minor_version}.{patch_version}'
		interpreter_version = f'{BELLOW_MAJOR_VERSION}.{BELLOW_MINOR_VERSION}.{BELLOW_PATCH_VERSION}'

		if major_version != BELLOW_MAJOR_VERSION:
			if major_version > BELLOW_MAJOR_VERSION:
				print(f'[I/O Error] File "{filename}" is a newer version ({file_version}) than this interpreter allows ({interpreter_version}).')
			else:
				print(f'[I/O Error] File "{filename}" is an older version ({file_version}) than this interpreter allows ({interpreter_version})')
			return None

		instruction_count = int.from_bytes(file.read(4), 'big')

		for i in range(0, instruction_count):
			instruction_list = []

			instruct = int.from_bytes(file.read(4), 'big')
			instruction_list.append(instruct)

			for j in range(0, MAX_BELLOW_ARGS):
				arg_mode = int.from_bytes(file.read(4), 'big')
				value = int.from_bytes(file.read(4), 'big')

				instruction_list.append((arg_mode, value))

			program.append(instruction_list)

		return program