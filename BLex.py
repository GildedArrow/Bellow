from enum import Enum, auto
import re

BELLOW_LEX_PATTERNS = [
	('NEWLINE', '\n'),
	('WS', r'\s+'),
	('COMMENT', r';.*'),
	('NUMBER', r'\d+'),
	('STRING', r'"([^"\\]|\\.)*"'),
	('LABEL_DEF', r'\.[A-Za-z_][A-Za-z0-9]*'),
	('LABEL', r'[A-Za-z_][A-Za-z0-9]*'),
	('HASHTAG', r'#'),
	('AMPERSAND', r'&'),
	('COMMA', r','),
	('MISMATCH', r'.'),
]

class BLexerError(Enum):
	ILLEGALCHARACTER = auto()

class BToken(Enum):
	#Misc
	LABEL_DEF = auto()
	LABEL = auto()
	NUMBER = auto()
	STRING = auto()
	HASHTAG = auto()
	AMPERSAND = auto()
	COMMA = auto()
	EOF = auto()
	NEWLINE = auto()

	#0 arg instructions
	RET = auto()

	#1 arg instructions
	DEC = auto()
	INC = auto()
	JMP = auto()
	JSR = auto()
	INP = auto()

	#2 argument instructions
	MOV = auto()
	JNZ = auto()
	JPZ = auto()
	DEB = auto() #Define bytes with a start location. ex: deb "Hello, world!", 0
	OUT = auto()

	#3 arg instructions
	ADD = auto()
	SUB = auto()
	MUL = auto()
	DIV = auto()
	MOD = auto()

BELLOW_RESERVED_KEYWORDS = {
	'ret': BToken.RET,

	'dec': BToken.DEC,
	'inc': BToken.INC,
	'jmp': BToken.JMP,
	'jsr': BToken.JSR,
	'inp': BToken.INP,

	'mov': BToken.MOV,
	'jnz': BToken.JNZ,
	'jpz': BToken.JPZ,
	'deb': BToken.DEB,
	'out': BToken.OUT,

	'add': BToken.ADD,
	'sub': BToken.SUB,
	'mul': BToken.MUL,
	'div': BToken.DIV,
	'mod': BToken.MOD,
}

BELLOW_PATTERN = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in BELLOW_LEX_PATTERNS))

class Token:
	def __init__(self, tokentype, line, value = None):
		self.tokentype = tokentype
		self.line = line
		self.value = value

	def __repr__(self):
		return f'(Token = {self.tokentype}, line = {self.line}, value = \'{self.value}\'\n'



class BellowLexer:
	def __init__(self):
		self.size = 256
		self.code = ''
		self.hadError = False
		self.parseTokens = []

	def scan_tokens(self, code):
		self.code = code
		self.parseTokens = []
		self.hadError = False

		line = 1
		pos = 0

		while pos < len(self.code):
			match = BELLOW_PATTERN.match(self.code, pos)

			kind = match.lastgroup
			value = match.group()

			if kind == 'NEWLINE':
				line += 1
			elif kind == 'WS' or kind == 'COMMENT':
				pass
			elif kind == 'MISMATCH':
				self.ThrowError(BLexerError.ILLEGALCHARACTER, value, line)
				break
			elif kind == 'LABEL_DEF':
				self.add_token(BToken.LABEL_DEF, line, value)
			elif kind == 'LABEL':
				val = value.lower()
				if BELLOW_RESERVED_KEYWORDS.get(val):
					self.add_token(BELLOW_RESERVED_KEYWORDS[val], line, value)
				else:
					self.add_token(BToken.LABEL, line, value)
			elif kind == 'HASHTAG':
				self.add_token(BToken.HASHTAG, line, value)
			elif kind == 'AMPERSAND':
				self.add_token(BToken.AMPERSAND, line, value)
			elif kind == 'COMMA':
				self.add_token(BToken.COMMA, line, value)
			elif kind == 'NUMBER':
				self.add_token(BToken.NUMBER, line, value)
			elif kind == 'STRING':
				self.add_token(BToken.STRING, line, value[1:-1])

			pos = match.end()

		self.add_token(BToken.EOF, line)
		return self.parseTokens

	def ThrowError(self, errortype, value = None, line = 0):
		self.hadError = True

		errormsg = f'[LEXER ERROR]'

		if errortype == BLexerError.ILLEGALCHARACTER:
			if value == '"':
				print(errormsg, f'Malformed string on line {line}')
			else:
				print(errormsg, f'Illegal character: \'{value}\' on line {line}')


	def add_token(self, kind, line, value = None):
		self.parseTokens.append(Token(kind, line, value))