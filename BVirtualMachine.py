import functools
import struct
from enum import Enum, auto

import BParse
from BLex import BToken

import numpy as np


class BRuntimeError:
	MEMORYACCESSVIOLATION = auto()
	STACKOVERFLOW = auto()
	RETURNWITHOUTCALL = auto()


def exec_ret(bvm, args):
	bvm.pc = bvm.callstack.pop()

def exec_dec(bvm, args):
	bvm.data[bvm.parse_arg(args[0])] -= 1

def exec_inc(bvm, args):
	bvm.data[bvm.parse_arg(args[0])] += 1

def exec_jmp(bvm, args):
	bvm.pc = bvm.parse_arg(args[0]) - 1

def exec_jsr(bvm, args):
	if len(bvm.callstack) > bvm.max_stack_size:
		bvm.ThrowError(BRuntimeError.STACKOVERFLOW)
		return
	bvm.callstack.append(bvm.pc)
	exec_jmp(bvm, args)

def exec_inp(bvm, args):
	bvm.data[bvm.parse_arg(args[0])] = int(input())

def exec_mov(bvm, args):
	bvm.data[bvm.parse_arg(args[1])] = bvm.parse_arg(args[0])

def exec_jnz(bvm, args):
	if bvm.parse_arg(args[1]) != 0:
		exec_jmp(bvm, args)

def exec_prc(bvm, args):
	mode = bvm.parse_arg(args[1])

	if mode == 0:
		print(bvm.parse_arg(args[0]), end='')
	elif mode == 1:
		print(chr(bvm.parse_arg(args[0])), end='')

def exec_jpz(bvm, args):
	if bvm.parse_arg(args[1]) == 0:
		exec_jmp(bvm, args)

def exec_jeq(bvm, args):
	if bvm.parse_arg(args[1]) == bvm.parse_arg(args[2]):
		exec_jmp(bvm, args)

def exec_jne(bvm, args):
	if bvm.parse_arg(args[1]) != bvm.parse_arg(args[2]):
		exec_jmp(bvm, args)

def exec_jle(bvm, args):
	if bvm.parse_arg(args[1]) < bvm.parse_arg(args[2]):
		exec_jmp(bvm, args)

def exec_jgr(bvm, args):
	if bvm.parse_arg(args[1]) > bvm.parse_arg(args[2]):
		exec_jmp(bvm, args)

def exec_xor(bvm, args):
	bvm.data[bvm.parse_arg(args[2])] = bvm.parse_arg(args[0]) ^ bvm.parse_arg(args[1])

def exec_shl(bvm, args):
	bvm.data[bvm.parse_arg(args[2])] = bvm.parse_arg(args[0]) << bvm.parse_arg(args[1])

def exec_shr(bvm, args):
	bvm.data[bvm.parse_arg(args[2])] = bvm.parse_arg(args[0]) >> bvm.parse_arg(args[1])

def exec_bnd(bvm, args):
	bvm.data[bvm.parse_arg(args[2])] = bvm.parse_arg(args[0]) & bvm.parse_arg(args[1])

def exec_bor(bvm, args):
	bvm.data[bvm.parse_arg(args[2])] = bvm.parse_arg(args[0]) | bvm.parse_arg(args[1])

def exec_add(bvm, args):
	bvm.data[bvm.parse_arg(args[2])] = bvm.parse_arg(args[0]) + bvm.parse_arg(args[1])

def exec_sub(bvm, args):
	bvm.data[bvm.parse_arg(args[2])] = bvm.parse_arg(args[0]) - bvm.parse_arg(args[1])

def exec_mul(bvm, args):
	bvm.data[bvm.parse_arg(args[2])] = bvm.parse_arg(args[0]) * bvm.parse_arg(args[1])

def exec_div(bvm, args):
	bvm.data[bvm.parse_arg(args[2])] = bvm.parse_arg(args[0]) // bvm.parse_arg(args[1])

def exec_mod(bvm, args):
	bvm.data[bvm.parse_arg(args[2])] = bvm.parse_arg(args[0]) % bvm.parse_arg(args[1])

def exec_out(bvm, args):
	start = bvm.parse_arg(args[0])
	end = bvm.parse_arg(args[1])
	mode = bvm.parse_arg(args[2])

	if mode == 0:
		for i in range(start, end + 1):
			print(bvm.data[i], end='')
	else:
		for i in range(start, end + 1):
			print(chr(bvm.data[i]), end='')


BELLOW_INSTRUCTIONS = {
	BToken.RET.value: exec_ret,

	BToken.DEC.value: exec_dec,
	BToken.INC.value: exec_inc,
	BToken.JMP.value: exec_jmp,
	BToken.JSR.value: exec_jsr,
	BToken.INP.value: exec_inp,

	BToken.MOV.value: exec_mov,
	BToken.JNZ.value: exec_jnz,
	BToken.PRC.value: exec_prc,
	BToken.JPZ.value: exec_jpz,
	BToken.XOR.value: exec_xor,
	BToken.SHL.value: exec_shl,
	BToken.SHR.value: exec_shr,
	BToken.BND.value: exec_bnd,
	BToken.BOR.value: exec_bor,

	BToken.JEQ.value: exec_jeq,
	BToken.JNE.value: exec_jne,
	BToken.JLE.value: exec_jle,
	BToken.JGR.value: exec_jgr,
	BToken.ADD.value: exec_add,
	BToken.SUB.value: exec_sub,
	BToken.MUL.value: exec_mul,
	BToken.DIV.value: exec_div,
	BToken.MOD.value: exec_mod,

	BToken.OUT.value: exec_out,
}


class BVirtualMachine:
	def __init__(self, datasize = 256, max_stack_size = 64):
		self.data = np.zeros(datasize, dtype=np.uint8)
		self.pc = 0
		self.program = []
		self.callstack = []
		self.max_stack_size = max_stack_size
		self.hadError = False

	def load_program(self, program):
		self.program = program


#	def load_bytecode(self, file):
#		with open(file, 'rb') as file:
#			signature = struct.unpack(">I", file.read(4)) #de ca fd ad
#			if signature[0] != 0xdecafdad:
#				print("Signature not recognized.")
#				return
#
#			while True:
#				op_data = file.read(1)
#				if not op_data:
#					break
#
#				op = struct.unpack("B", op_data)[0]
#
#				argc = BParse.BELLOW_INSTRUCTION_ARGS[op]
#
#				args = []

	def parse_arg(self, arg):
		if arg == -1: return -1

		val = arg[1]

		match arg[0]:
			case 0: #label
				return val
			case 1: #string
				return ord(val)
			case 2: #value at memory cell
				return self.data[int(val)]
			case 3: #value at the memory cell stored pointer of memory cell
				return self.data[self.data[int(val)]]
			case 4:
				return int(val)

	def run(self):
		self.hadError = False

		while True:
			if self.pc >= len(self.program):
				break

			if self.hadError:
				break

			line = self.program[self.pc]
			instruction = line[0]

			BELLOW_INSTRUCTIONS[instruction](self, line[1:len(line)])

			self.pc += 1


	def ThrowError(self, errortype, value = None, line = None):
		errormsg = f'[RUNTIME ERROR]'

		if errortype == BRuntimeError.STACKOVERFLOW:
			print(errormsg, f'Stack overflow, recursion depth exceeded ({self.max_stack_size})')