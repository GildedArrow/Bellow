from enum import Enum, auto

class LexerError(Enum):
	ILLEGAL_CHARACTER = auto()
	FILE_NOT_FOUND = auto()

class TokenType(Enum):
	KEYWORD = auto()
	NUMBER = auto()
	HASHTAG = auto()
	AMPERSAND = auto()
	COMMA = auto()
	PERIOD = auto()
	NEWLINE = auto()
	IDENTIFIER = auto()
	EOF = auto()

class InstructionType(Enum):
	MOV = auto()
	ADD = auto()
	SUB = auto()
	DIV = auto()
	MUL = auto()
	MOD = auto()
	SHR = auto()
	SHL = auto()
	INC = auto()
	DEC = auto()
	JMP = auto()
	JNZ = auto()
	JSR = auto()
	JZ = auto()
	JE = auto()
	JNE = auto()
	JLE = auto()
	JGR = auto()
	OUT = auto()
	INPUT = auto()
	RET = auto()
	VAR = auto()
	CONST = auto()
	ARRAY = auto()

LEX_TOKEN_MAP = {
	'mov'    : InstructionType.MOV,
	'add'    : InstructionType.ADD,
	'sub'    : InstructionType.SUB,
	'div'    : InstructionType.DIV,
	'mul'    : InstructionType.MUL,
	'mod'    : InstructionType.MOD,
	'shr'    : InstructionType.SHR,
	'shl'    : InstructionType.SHL,
	'inc'    : InstructionType.INC,
	'dec'    : InstructionType.DEC,
	'jmp'    : InstructionType.JMP,
	'jnz'    : InstructionType.JNZ,
	'jsr'    : InstructionType.JSR,
	'jz'     : InstructionType.JZ,
	'je'     : InstructionType.JE,
	'jne'    : InstructionType.JNE,
	'jle'    : InstructionType.JLE,
	'jgr'    : InstructionType.JGR,
	'out'    : InstructionType.OUT,
	'input'  : InstructionType.INPUT,
	'ret'    : InstructionType.RET,
	'var'    : InstructionType.VAR,
	'const'  : InstructionType.CONST,
	'array'  : InstructionType.ARRAY,
}

class BToken:
	def __init__(self, token_type, line, col, value = None):
		self.type = token_type
		self.line = line
		self.col = col
		self.value = value

	def __repr__(self):
		return f'{self.type} [{self.line}:{self.col}] - "{self.value}"'

class BLexer:
	def __init__(self, file:str):
		self.src = self.load_source(file)
		self.pos = 0
		self.line = 1
		self.col = 1
		self.hadError = False

	def throw_lexer_error(self, errortype, data):
		self.hadError = True
		print('[Lexer Error] ', end='')
		if errortype == LexerError.ILLEGAL_CHARACTER:
			print(f'Illegal character \"{data}\" on line {self.line}, col {self.col}')
		elif errortype == LexerError.FILE_NOT_FOUND:
			print(f'File not found: \"{data}\"')

	def load_source(self, file):
		try:
			with open(file, "r") as f:
				return f.read()
		except FileNotFoundError:
			self.throw_lexer_error(LexerError.FILE_NOT_FOUND, file)

	def is_eof(self):
		return self.pos == len(self.src)

	def advance(self):
		c = self.src[self.pos]
		self.pos += 1

		if c == '\n':
			self.line += 1
			self.col = 1
		else:
			self.col += 1

		return c

	def peek(self):
		if self.pos == len(self.src):
			return None
		return self.src[self.pos]

	def peek_next(self):
		if self.pos + 1 > len(self.src):
			return None
		return self.src[self.pos + 1]

	def skip_whitespace(self):
		while True:
			c = self.peek()

			if c == ' ' or c == '\t' or c == '\r':
				self.advance()
				continue

			if c == '/' and self.peek_next() == '/':
				while not self.is_eof() and self.peek() != '\n':
					self.advance()
				continue

			break

	def make_token(self, token_type, value =''):
		return BToken(token_type=token_type, line=self.line, col=self.col, value=value)

	def make_number(self):
		t = self.make_token(TokenType.NUMBER)

		start = self.pos - 1
		while self.peek():
			if not self.peek().isnumeric():
				break
			self.advance()

		end = self.pos

		t.value = int(self.src[start:end])
		return t

	def make_identifier_or_keyword(self):
		start = self.pos - 1
		while not self.is_eof() and (self.peek().isalnum() or self.peek() == '_'):
			self.advance()

		end = self.pos

		value = self.src[start:end]

		if value in LEX_TOKEN_MAP:
			return self.make_token(TokenType.KEYWORD, LEX_TOKEN_MAP[value])
		else:
			return self.make_token(TokenType.IDENTIFIER, value)

	def next_token(self):
		self.skip_whitespace()

		if self.is_eof():
			return self.make_token(TokenType.EOF)

		while not self.is_eof() and not self.hadError:
			c = self.advance()

			if c == ';' or c == '\n':
				return self.make_token(TokenType.NEWLINE, 'new line')
			elif c == '.':
				return self.make_token(TokenType.PERIOD, '.')
			elif c == ',':
				return self.make_token(TokenType.COMMA, ',')
			elif c == '#':
				return self.make_token(TokenType.HASHTAG, '#')
			elif c == '&':
				return self.make_token(TokenType.AMPERSAND, '&')

			if c.isalpha() or c == '_':
				return self.make_identifier_or_keyword()

			if c.isnumeric():
				return self.make_number()

			self.throw_lexer_error(LexerError.ILLEGAL_CHARACTER, c)