from enum import Enum, auto
from BLex import BToken

class BParseError(Enum):
	DUPLICATELABEL = auto()
	EXPECTINGNEWLINE = auto()
	EXPECTINGARGUMENT = auto()
	NOTINSTRUCTION = auto()
	INVALIDARGCOUNT = auto()
	LABELNOTFOUND = auto()

BELLOW_INSTRUCTION_ARGS = {
	BToken.RET: 0,

	BToken.DEC: 1,
	BToken.INC: 1,
	BToken.JMP: 1,
	BToken.JSR: 1,
	BToken.INP: 1,

	BToken.MOV: 2,
	BToken.JNZ: 2,
	BToken.PRC: 2,
	BToken.JPZ: 2,
	BToken.DEB: 2,

	BToken.ADD: 3,
	BToken.SUB: 3,
	BToken.MUL: 3,
	BToken.DIV: 3,
	BToken.MOD: 3,
	BToken.XOR: 3,
	BToken.SHL: 3,
	BToken.SHR: 3,
	BToken.BND: 3,
	BToken.BOR: 3,
	BToken.AND: 3,
	BToken._OR: 3,

	BToken.OUT: 3,
}


#Goal: take lex tokens and parse them into a runnable bellow program
class BellowParser:
	def __init__(self):
		self.lex_tokens = None
		self.labels = {}
		self.program = []
		self.hadError = False
		self.index = 0

	def parse_tokens(self, lex_tokens):
		self.lex_tokens = lex_tokens
		self.labels = {}
		self.program = []
		self.hadError = False
		self.index = 0

		while not self.is_eof():
			token = self.advance()

			if token.tokentype == BToken.NEWLINE:
				continue

			if token.tokentype == BToken.LABEL_DEF:
				self.parse_label(token)
				continue

			if token.is_instruct:
				self.program.append(self.parse_instruction(token))
				continue

			self.ThrowError(BParseError.NOTINSTRUCTION, token.value, token.line)
			return

		self.resolve_labels()

		return self.program

	def resolve_labels(self):
		resolved_program = []

		for instruction in self.program:
			op = instruction[0]
			args = []

			for arg in instruction[1:]:
				argtype, val = arg

				if argtype == 0:
					if not val in self.labels:
						self.ThrowError(BParseError.LABELNOTFOUND)
						return

					args.append((4, self.labels[val]))

				else:
					args.append(arg)

			#print((op, *args))
			resolved_program.append((op, *args))

		self.program = resolved_program

	def parse_instruction(self, token):
		instruction_type = token.tokentype
		argc = BELLOW_INSTRUCTION_ARGS[instruction_type]
		args = []

		#print("Parsing instruction:",instruction_type,argc)

		while len(args) < argc:
			if self.is_eol():
				self.ThrowError(BParseError.INVALIDARGCOUNT, token.value, token.line)
				return

			val = self.advance()
			arg = ()

			if val.tokentype == BToken.COMMA:
				continue

			if val.tokentype == BToken.LABEL:
				arg = (0, val.value)
			elif val.tokentype == BToken.STRING:
				arg = (1, val.value)
			elif val.tokentype == BToken.HASHTAG:
				n = self.advance()
				arg = (2, int(n.value))
			elif val.tokentype == BToken.AMPERSAND:
				n = self.advance()
				arg = (3, int(n.value))
			elif val.tokentype == BToken.NUMBER:
				arg = (4, int(val.value))

			args.append(arg)

		if not self.is_eof() and not self.is_eol():
			self.ThrowError(BParseError.INVALIDARGCOUNT, token.value, token.line)
			return

		return (instruction_type.value, *args)

	def parse_label(self, token):
		label_name = token.value[1:]

		if label_name in self.labels:
			self.ThrowError(BParseError.DUPLICATELABEL, label_name, token.line)
			return

		self.labels[label_name] = len(self.program)

		if not self.is_eol() and not self.is_eof():
			self.ThrowError(BParseError.EXPECTINGNEWLINE, self.peek().value, token.line)
			return

		self.advance()

	def advance(self):
		token = self.peek()
		self.index += 1
		return token

	def peek(self):
		if self.index >= len(self.lex_tokens):
			return self.lex_tokens[-1]
		return self.lex_tokens[self.index]

	def is_eol(self):
		return self.peek().tokentype == BToken.NEWLINE

	def is_eof(self):
		return self.peek().tokentype == BToken.EOF

	def ThrowError(self, errortype, value = None, line = 1):
		errormsg = f'[PARSE ERROR]'

		if errortype == BParseError.DUPLICATELABEL:
			print(errormsg, f'Duplicate label definition \'{value}\' on line {line}')
		elif errortype == BParseError.EXPECTINGNEWLINE:
			print(errormsg, f'Expecting new line, got \'{value}\' on line {line} instead')
		elif errortype == BParseError.NOTINSTRUCTION:
			print(errormsg, f'Expecting instruction, got \'{value}\' on line {line} instead')
		elif errortype == BParseError.INVALIDARGCOUNT:
			print(errormsg, f'Invalid number of arguments for \'{value}\' on line {line}')
		elif errortype == BParseError.EXPECTINGARGUMENT:
			print(errormsg, f'Expecting argument, got \'{value}\' on line {line}')
		elif errortype == BParseError.LABELNOTFOUND:
			print(errormsg, f'Undefined label reference')
