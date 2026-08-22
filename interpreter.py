from glob import magic_check

from bellow import BELLOW_SIGNATURE, BELLOW_MAJOR_VERSION, BELLOW_MINOR_VERSION, BELLOW_PATCH_VERSION, MAX_BELLOW_ARGS
import numpy as np

MEMORY_LENGTH = 1024
MAX_CALLSTACK_SIZE = 16

def get_literal(interpreter, arg):
	if arg[0] == 0:
		return arg[1]
	elif arg[0] == 1:
		return interpreter.memory[arg[1]]
	elif arg[0] == 2:
		return interpreter.memory[interpreter.memory[arg[1]]]

def op_mov(interpreter, args):
	interpreter.memory[get_literal(interpreter, args[1])] = get_literal(interpreter, args[0])

def op_add(interpreter, args):
	interpreter.memory[get_literal(interpreter, args[2])] = get_literal(interpreter, args[0]) + get_literal(interpreter, args[1])

def op_sub(interpreter, args):
	interpreter.memory[get_literal(interpreter, args[2])] = get_literal(interpreter, args[0]) - get_literal(interpreter, args[1])

def op_div(interpreter, args):
	interpreter.memory[get_literal(interpreter, args[2])] = get_literal(interpreter, args[0]) // get_literal(interpreter, args[1])

def op_mul(interpreter, args):
	interpreter.memory[get_literal(interpreter, args[2])] = get_literal(interpreter, args[0]) * get_literal(interpreter, args[1])

def op_mod(interpreter, args):
	interpreter.memory[get_literal(interpreter, args[2])] = get_literal(interpreter, args[0]) % get_literal(interpreter, args[1])

def op_shr(interpreter, args):
	interpreter.memory[get_literal(interpreter, args[2])] = get_literal(interpreter, args[0]) >> get_literal(interpreter, args[1])

def op_shl(interpreter, args):
	interpreter.memory[get_literal(interpreter, args[2])] = get_literal(interpreter, args[0]) << get_literal(interpreter, args[1])


def op_inc(interpreter, args):
	interpreter.memory[get_literal(interpreter, args[0])] += 1

def op_dec(interpreter, args):
	interpreter.memory[get_literal(interpreter, args[0])] -= 1

def op_jmp(interpreter, args):
	interpreter.pc = get_literal(interpreter, args[0])

def op_jnz(interpreter, args):
	if get_literal(interpreter, args[1]) != 0:
		interpreter.pc = get_literal(interpreter, args[0]) - 1

def op_jsr(interpreter, args):
	pass

def op_jz(interpreter, args):
	if get_literal(interpreter, args[1]) == 0:
		interpreter.pc = get_literal(interpreter, args[0]) - 1

def op_je(interpreter, args):
	if get_literal(interpreter, args[1]) == get_literal(interpreter, args[2]):
		interpreter.pc = get_literal(interpreter, args[0]) - 1

def op_jne(interpreter, args):
	if get_literal(interpreter, args[1]) != get_literal(interpreter, args[2]):
		interpreter.pc = get_literal(interpreter, args[0]) - 1

def op_jle(interpreter, args):
	if get_literal(interpreter, args[1]) < get_literal(interpreter, args[2]):
		interpreter.pc = get_literal(interpreter, args[0]) - 1

def op_jgr(interpreter, args):
	if get_literal(interpreter, args[1]) > get_literal(interpreter, args[2]):
		interpreter.pc = get_literal(interpreter, args[0]) - 1

def op_out(interpreter, args):
	if get_literal(interpreter, args[1]) == 0:
		print(get_literal(interpreter, args[0]), end='')
	else:
		print(chr(get_literal(interpreter, args[0])), end='')

def op_input(interpreter, args):
	interpreter.memory[get_literal(interpreter, args[0])] = int(input())

bellow_jump_table = [
	op_mov,
	op_add,
	op_sub,
	op_div,
	op_mul,
	op_mod,
	op_shr,
	op_shl,
	op_inc,
	op_dec,
	op_jmp,
	op_jnz,
	op_jsr,
	op_jz,
	op_je,
	op_jne,
	op_jle,
	op_jgr,
	op_out,
	op_input
]

class BInterpreter:
	def __init__(self):
		self.pc = 0
		self.callstack = []
		self.program = []
		self.memory = np.zeros(MEMORY_LENGTH, dtype=int)

	def run(self):

		while self.pc < len(self.program):
			instruction = self.program[self.pc] #Fetch
			op = bellow_jump_table[instruction[0]] #Decode

			op(self, (instruction[1], instruction[2], instruction[3])) #Execute

			self.pc += 1



def loadProgram(filename):
	program = []
	with open(filename, 'rb') as file:
		magic_word = file.read(4)

		if magic_word.hex() != BELLOW_SIGNATURE.hex():
			print(f'[I/O] Invalid Bellow signature {magic_word.hex()}')
			return None

		majorversion = int.from_bytes(file.read(4), 'big')
		minorversion = int.from_bytes(file.read(4), 'big')
		patchversion = int.from_bytes(file.read(4), 'big')

		file_version = f'{majorversion}.{minorversion}.{patchversion}'
		interpreter_version = f'{BELLOW_MAJOR_VERSION}.{BELLOW_MINOR_VERSION}.{BELLOW_PATCH_VERSION}'

		if majorversion != BELLOW_MAJOR_VERSION:
			if majorversion > BELLOW_MAJOR_VERSION:
				print(f'[I/O Error] File is a newer version ({file_version}) than this interpreter ({interpreter_version}).')
			else:
				print(f'[I/O Error] File is an older version ({file_version}) than this interpreter ({interpreter_version})')
			return None

		instruction_count = int.from_bytes(file.read(4), 'big')

		for i in range(0, instruction_count):
			instrlist = []

			instruct = int.from_bytes(file.read(4), 'big')
			instrlist.append(instruct)

			for j in range(0, MAX_BELLOW_ARGS):
				argmode = int.from_bytes(file.read(4), 'big')
				value = int.from_bytes(file.read(4), 'big')

				instrlist.append((argmode, value))

			program.append(instrlist)

		return program

def main():
	interpreter = BInterpreter()

	interpreter.program = loadProgram('code.bec')
	interpreter.run()

if __name__ == '__main__':
	main()