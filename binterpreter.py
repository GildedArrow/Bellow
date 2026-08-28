from enum import Enum, auto
import numpy as np

MEMORY_LENGTH = 1024
MAX_CALLSTACK_SIZE = 16

def getnum(interpreter, arg):
	if arg[0] == 0:
		return arg[1]
	elif arg[0] == 1:
		return interpreter.memory[arg[1]]
	elif arg[0] == 2:
		return interpreter.memory[interpreter.memory[arg[1]]]

def op_mov(interpreter, args):
	interpreter.memory[getnum(interpreter, args[1])] = getnum(interpreter, args[0])

def op_add(interpreter, args):
	interpreter.memory[getnum(interpreter, args[2])] = getnum(interpreter, args[0]) + getnum(interpreter, args[1])

def op_sub(interpreter, args):
	interpreter.memory[getnum(interpreter, args[2])] = getnum(interpreter, args[0]) - getnum(interpreter, args[1])

def op_div(interpreter, args):
	interpreter.memory[getnum(interpreter, args[2])] = getnum(interpreter, args[0]) // getnum(interpreter, args[1])

def op_mul(interpreter, args):
	interpreter.memory[getnum(interpreter, args[2])] = getnum(interpreter, args[0]) * getnum(interpreter, args[1])

def op_mod(interpreter, args):
	interpreter.memory[getnum(interpreter, args[2])] = getnum(interpreter, args[0]) % getnum(interpreter, args[1])

def op_shr(interpreter, args):
	interpreter.memory[getnum(interpreter, args[2])] = getnum(interpreter, args[0]) >> getnum(interpreter, args[1])

def op_shl(interpreter, args):
	interpreter.memory[getnum(interpreter, args[2])] = getnum(interpreter, args[0]) << getnum(interpreter, args[1])

def op_inc(interpreter, args):
	interpreter.memory[getnum(interpreter, args[0])] += 1

def op_dec(interpreter, args):
	interpreter.memory[getnum(interpreter, args[0])] -= 1

def op_jmp(interpreter, args):
	interpreter.pc = getnum(interpreter, args[0]) - 1

def op_jnz(interpreter, args):
	if getnum(interpreter, args[1]) != 0:
		interpreter.pc = getnum(interpreter, args[0]) - 1

def op_jsr(interpreter, args):
	interpreter.callstack.append(interpreter.pc)
	interpreter.pc = getnum(interpreter, args[0]) - 1

def op_jz(interpreter, args):
	if getnum(interpreter, args[1]) == 0:
		interpreter.pc = getnum(interpreter, args[0]) - 1

def op_je(interpreter, args):
	if getnum(interpreter, args[1]) == getnum(interpreter, args[2]):
		interpreter.pc = getnum(interpreter, args[0]) - 1

def op_jne(interpreter, args):
	if getnum(interpreter, args[1]) != getnum(interpreter, args[2]):
		interpreter.pc = getnum(interpreter, args[0]) - 1

def op_jle(interpreter, args):
	if getnum(interpreter, args[1]) < getnum(interpreter, args[2]):
		interpreter.pc = getnum(interpreter, args[0]) - 1

def op_jgr(interpreter, args):
	if getnum(interpreter, args[1]) > getnum(interpreter, args[2]):
		interpreter.pc = getnum(interpreter, args[0]) - 1

def op_out(interpreter, args):
	if getnum(interpreter, args[1]) == 0:
		print(getnum(interpreter, args[0]), end='')
	else:
		print(chr(getnum(interpreter, args[0])), end='')

def op_input(interpreter, args):
	interpreter.memory[getnum(interpreter, args[0])] = int(input())

def op_ret(interpreter, args):
	interpreter.pc = interpreter.callstack.pop()

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
	op_input,
	op_ret
]

class RuntimeError(Enum):
	MEMORY_ACCESS_VIOLATION = auto()
	DIVISION_BY_ZERO = auto()

class BInterpreter:
	def __init__(self):
		self.pc = 0
		self.callstack = []
		self.program = []
		self.memory = np.zeros(MEMORY_LENGTH, dtype=np.uint32)
		self.haderror = False

	def throw_runtime_error(self, errortype):
		pass
		#TBA

	def run(self):
		while self.pc < len(self.program):
			instruction = self.program[self.pc] #Fetch
			op = bellow_jump_table[instruction[0]] #Decode

			op(self, (instruction[1], instruction[2], instruction[3])) #Execute

			self.pc += 1