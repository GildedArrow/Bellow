from bellow import BELLOW_SIGNATURE, BELLOW_MAJOR_VERSION, BELLOW_MINOR_VERSION, BELLOW_PATCH_VERSION, MAX_BELLOW_ARGS

from enum import Enum, auto

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

ARGS_COUNTS = {
	InstructionType.MOV   : (2, 2),
	InstructionType.ADD   : (3, 3),
	InstructionType.SUB   : (3, 3),
	InstructionType.DIV   : (3, 3),
	InstructionType.MUL   : (3, 3),
	InstructionType.MOD   : (3, 3),
	InstructionType.SHR   : (3, 3),
	InstructionType.SHL   : (3, 3),
	InstructionType.INC   : (1, 2),
	InstructionType.DEC   : (1, 2),
	InstructionType.JMP   : (1, 1),
	InstructionType.JNZ   : (2, 2),
	InstructionType.JSR   : (1, 1),
	InstructionType.JZ    : (2, 2),
	InstructionType.JE    : (3, 3),
	InstructionType.JNE   : (3, 3),
	InstructionType.JLE   : (3, 3),
	InstructionType.JGR   : (3, 3),
	InstructionType.OUT   : (1, 2),
	InstructionType.INPUT : (2, 2),
	InstructionType.RET   : (0, 0),
	InstructionType.VAR   : (1, 2),
	InstructionType.CONST : (2, 2),
	InstructionType.ARRAY : (2, 2),
}

class LexerError(Enum):
	ILLEGAL_CHARACTER = auto()
	FILE_NOT_FOUND = auto()

class ParserError(Enum):
	EXPECTING_STATEMENT = auto()
	EXPECTING_IDENTIFIER = auto()
	EXPECTING_END_OF_LINE = auto()
	UNINITIALIZED_CONSTANT = auto()
	CONST_EXPECTING_NUMBER = auto()
	ARRAY_EXPECTING_NUMBER = auto()
	EXPECTING_COMMA = auto()
	EXPECTING_ARGUMENT = auto()
	TOO_MANY_ARGUMENTS = auto()
	TOO_FEW_ARGUMENTS = auto()
	EXPECTING_NUMBER_OR_IDENTIFIER = auto()
	DUPLICATE_DECLARATION = auto()
	UNDEFINED_IDENTIFIER = auto()

class BToken:
	def __init__(self, tokentype, line, col, value = None):
		self.type = tokentype
		self.line = line
		self.col = col
		self.value = value

	def __repr__(self):
		return f'{self.type} [{self.line}:{self.col}] - "{self.value}"'

class BLexer:
	def __init__(self, file):
		self.src = self.loadSource(file)
		self.pos = 0
		self.line = 1
		self.col = 1
		self.hadError = False

	def throwLexerError(self, errortype, data):
		self.hadError = True
		print('[Lexer Error] ', end='')
		if errortype == LexerError.ILLEGAL_CHARACTER:
			print(f'Illegal character \"{data}\" on line {self.line}, col {self.col}')
		elif errortype == LexerError.FILE_NOT_FOUND:
			print(f'File not found: \"{data}\"')

	def loadSource(self, file):
		try:
			with open(file, "r") as f:
				return f.read()
		except FileNotFoundError:
			self.throwLexerError(LexerError.FILE_NOT_FOUND, file)

	def isEof(self):
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

	def peekNext(self):
		if self.pos + 1 > len(self.src):
			return None
		return self.src[self.pos + 1]

	def skipWhitespace(self):
		while True:
			c = self.peek()

			if c == ' ' or c == '\t' or c == '\r':
				self.advance()
				continue

			if c == '/' and self.peekNext() == '/':
				while not self.isEof() and self.peek() != '\n':
					self.advance()
				continue

			break

	def makeToken(self, tokentype, value = ''):
		return BToken(tokentype=tokentype, line=self.line, col=self.col, value=value)

	def makeNumber(self):
		t = self.makeToken(TokenType.NUMBER)

		start = self.pos - 1
		while self.peek().isnumeric():
			self.advance()
		end = self.pos

		t.value = int(self.src[start:end])
		return t

	def makeIdentifierOrKeyword(self):
		start = self.pos - 1
		while not self.isEof() and (self.peek().isalnum() or self.peek() == '_'):
			self.advance()

		end = self.pos

		value = self.src[start:end]

		if value in LEX_TOKEN_MAP:
			return self.makeToken(TokenType.KEYWORD, LEX_TOKEN_MAP[value])
		else:
			return self.makeToken(TokenType.IDENTIFIER, value)

	def nextToken(self):
		if self.isEof():
			return self.makeToken(TokenType.EOF)

		self.skipWhitespace()

		while not self.isEof() and not self.hadError:
			c = self.advance()

			if c == ';' or c == '\n':
				return self.makeToken(TokenType.NEWLINE, 'new line')
			elif c == '.':
				return self.makeToken(TokenType.PERIOD, '.')
			elif c == ',':
				return self.makeToken(TokenType.COMMA, ',')
			elif c == '#':
				return self.makeToken(TokenType.HASHTAG, '#')
			elif c == '&':
				return self.makeToken(TokenType.AMPERSAND, '&')
			elif c == '-':
				return self.makeToken(TokenType.MINUS, '-')

			if c.isalpha() or c == '_':
				return self.makeIdentifierOrKeyword()

			if c.isnumeric():
				return self.makeNumber()

			self.throwLexerError(LexerError.ILLEGAL_CHARACTER, c)

class DeclarationType(Enum):
	LABEL = auto()
	CONST = auto()
	VARIABLE = auto()
	ARRAY = auto()

class ArgumentMode(Enum):
	IMMEDIATE = auto()
	VALUE = auto()
	POINTER = auto()

class ArgumentType(Enum):
	NUMBER = auto()
	IDENTIFIER = auto()

class Declaration:
	def __init__(self, type, name, line, col):
		self.type = type
		self.name = name
		self.line = line
		self.col = col
		self.value = 0

	def __repr__(self):
		return f'{self.type} "{self.name}" [{self.value}] - [{self.line}:{self.col}]\n'

class BArgument:
	def __init__(self, type, mode, value):
		self.mode = mode
		self.type = type
		self.value = value

	def __repr__(self):
		return f'({self.type}, {self.mode}, "{self.value}")'

class BInstruction:
	def __init__(self, keyword):
		self.keyword = keyword
		self.args = []

	def __repr__(self):
		return f'{self.keyword} - {self.args}\n'

class BProgram:
	def __init__(self):
		self.instructions = []
		self.declarations = []

	def __repr__(self):
		return f'Declarations: {self.declarations}\nInstructions: {self.instructions}'

def FindDeclarationUsingName(program, name):
	for d in program.declarations:
		if d.name != name:
			continue
		return d
	return None


class BParser:
	def __init__(self, lexer: BLexer):
		self.lexer = lexer
		self.current = self.lexer.nextToken()
		self.next = self.lexer.nextToken()
		self.hadError = False
		self.pc = 0
		self.vp = 0

	def throwParserError(self, errortype, data):
		self.hadError = True
		print('[Parser Error] ', end='')
		if errortype == ParserError.EXPECTING_STATEMENT:
			print(f'Expecting statement, but found \"{data}\" instead on line {self.current.line}, col {self.current.col}')
		elif errortype == ParserError.EXPECTING_STATEMENT:
			print(f'Expecting identifier, but found \"{data}\" instead on line {self.current.line}, col {self.current.col}')
		elif errortype == ParserError.EXPECTING_END_OF_LINE:
			print(f'Expecting end of statement, but found \"{data}\" instead on line {self.current.line}, col {self.current.col}')
		elif errortype == ParserError.UNINITIALIZED_CONSTANT:
			print(f'Uninitialized constant on line {self.current.line}, col {self.current.col}')
		elif errortype == ParserError.CONST_EXPECTING_NUMBER:
			print(f'Constant value declarations should be integer literals, but found \"{data}\" instead on line {self.current.line}, col {self.current.col}')
		elif errortype == ParserError.ARRAY_EXPECTING_NUMBER:
			print(f'Array size should be positive integer literal, but found \"{data}\" instead on line {self.current.line}, col {self.current.col}')
		elif errortype == ParserError.EXPECTING_COMMA:
			print(f'Expecting comma, but found \"{data}\" instead on line {self.current.line}, col {self.current.col}')
		elif errortype == ParserError.EXPECTING_ARGUMENT:
			print(f'Expecting argument, but found \"{data}\" instead on line {self.current.line}, col {self.current.col}')
		elif errortype == ParserError.TOO_MANY_ARGUMENTS:
			print(f'Too many arguments for instruction on line {self.current.line}, col {self.current.col}. Takes at most {data}')
		elif errortype == ParserError.EXPECTING_NUMBER_OR_IDENTIFIER:
			print(f'Expecting number or identifier, got \"{data}\" on line {self.current.line}, col {self.current.col}')
		elif errortype == ParserError.TOO_FEW_ARGUMENTS:
			print(f'Too few arguments for instruction on line {self.current.line}, col {self.current.col}. Takes at least {data}')
		elif errortype == ParserError.DUPLICATE_DECLARATION:
			print(f'Duplicate identifier declaration \"{data[0]}\" on line {data[1]}, col {data[2]}')
		elif errortype == ParserError.EXPECTING_IDENTIFIER:
			print(f'Expecting identifier, but found \"{data}\" instead on line {self.current.line}, col {self.current.col}')
		elif errortype == ParserError.UNDEFINED_IDENTIFIER:
			print(f'Undefined identifier \"{data}\" on line {self.current.line}, col {self.current.col}')

	def advance(self):
		self.current = self.next
		self.next = self.lexer.nextToken()

	def isEof(self):
		return self.lexer.isEof()

	def isEndOfStatement(self):
		return self.next.type == TokenType.NEWLINE or self.next.type == TokenType.EOF

	def expectNewlineOrEOF(self):
		self.advance()
		if not self.isEndOfStatement():
			self.throwParserError(ParserError.EXPECTING_END_OF_LINE, self.next.value)
			return

	def parseLabel(self, program):
		if self.next.type != TokenType.IDENTIFIER:
			self.throwParserError(ParserError.EXPECTING_IDENTIFIER, self.next.value)
			return

		self.expectNewlineOrEOF()

		newlabel = Declaration(DeclarationType.LABEL, self.current.value, self.current.line, self.current.col)
		newlabel.value = self.pc #where it exists in the program
		program.declarations.append(newlabel)

	def parseVariable(self, program):
		if self.next.type != TokenType.IDENTIFIER:
			self.throwParserError(ParserError.EXPECTING_IDENTIFIER, self.next.value)
			return

		self.expectNewlineOrEOF()

		newvar = Declaration(DeclarationType.VARIABLE, self.current.value, self.current.line, self.current.col)
		newvar.value = self.vp

		self.vp += 1

		program.declarations.append(newvar)

	def parseConstant(self, program):
		if self.next.type != TokenType.IDENTIFIER:
			self.throwParserError(ParserError.EXPECTING_IDENTIFIER, self.next.value)
			return

		self.advance()

		identifer = self.current.value

		if self.next.type != TokenType.NUMBER:
			self.throwParserError(ParserError.CONST_EXPECTING_NUMBER, self.next.value)
			return

		self.expectNewlineOrEOF()

		newconst = Declaration(DeclarationType.CONST, identifer, self.current.line, self.current.col)
		newconst.value = self.current.value

		program.declarations.append(newconst)

	def parseArray(self, program):
		if self.next.type != TokenType.IDENTIFIER:
			self.throwParserError(ParserError.EXPECTING_IDENTIFIER, self.next.value)
			return

		self.advance()

		identifier = self.current.value

		if self.next.type != TokenType.NUMBER:
			self.throwParserError(ParserError.ARRAY_EXPECTING_NUMBER, self.next.value)
			return

		self.expectNewlineOrEOF()

		newarray = Declaration(DeclarationType.ARRAY, identifier, self.current.line, self.current.col)
		newarray.value = self.vp

		self.vp += self.current.value

		program.declarations.append(newarray)

	def expectComma(self):
		self.advance()
		if self.current.type != TokenType.COMMA:
			self.throwParserError(ParserError.EXPECTING_COMMA, self.current.type)

	def ExpectNumber(self):
		self.advance()
		if self.current.type != TokenType.NUMBER and self.current.type != TokenType.IDENTIFIER:
			self.throwParserError(ParserError.EXPECTING_NUMBER_OR_IDENTIFIER, self.current.type)

	def parseArgument(self, args, mode = ArgumentMode.IMMEDIATE, value = None, argtype = ArgumentType.NUMBER):
		if self.current.type == TokenType.NUMBER:
			argtype = ArgumentType.NUMBER
			value = self.current.value
			args.append(BArgument(argtype, mode, value))
		elif self.current.type == TokenType.IDENTIFIER:
			argtype = ArgumentType.IDENTIFIER
			value = self.current.value
			args.append(BArgument(argtype, mode, value))
		elif self.current.type == TokenType.HASHTAG:
			self.ExpectNumber()
			self.parseArgument(args, ArgumentMode.VALUE, value, argtype)
			return
		elif self.current.type == TokenType.AMPERSAND:
			self.ExpectNumber()
			self.parseArgument(args, ArgumentMode.POINTER, value, argtype)
			return
		else:
			self.throwParserError(ParserError.EXPECTING_ARGUMENT, self.current.type)

		self.advance()

	def parseKeyword(self, program):
		kw = self.current.value

		num_args = ARGS_COUNTS[self.current.value]
		new_instruct = BInstruction(self.current.value)

		args = []

		if not self.isEndOfStatement():
			self.advance()
			self.parseArgument(args)

			while self.current.type != TokenType.NEWLINE and not self.isEof():
				if self.current.type != TokenType.COMMA:
					self.throwParserError(ParserError.EXPECTING_COMMA, self.current.value)
					return

				self.advance()
				self.parseArgument(args)

				if self.hadError:
					return

			new_instruct.args = args

		if len(args) > num_args[1]:
			self.throwParserError(ParserError.TOO_MANY_ARGUMENTS, num_args[1])
			return
		if len(args) < num_args[0]:
			self.throwParserError(ParserError.TOO_FEW_ARGUMENTS, num_args[0])
			return

		self.pc += 1
		program.instructions.append(new_instruct)

	def parseProgram(self):
		program = BProgram()

		#First pass, collect all declarations and instructions
		while not self.isEof() and not self.hadError:
			if self.current.type == TokenType.NEWLINE:
				self.advance()
				continue
			elif self.current.type == TokenType.PERIOD:
				self.parseLabel(program)
			elif self.current.type == TokenType.KEYWORD:
				if self.current.value == InstructionType.VAR:
					self.parseVariable(program)
				elif self.current.value == InstructionType.CONST:
					self.parseConstant(program)
				elif self.current.value == InstructionType.ARRAY:
					self.parseArray(program)
				else:
					self.parseKeyword(program)
			else:
				self.throwParserError(ParserError.EXPECTING_STATEMENT, self.current.type)

			self.advance()

			if self.hadError:
				return None

			#Second pass, check for duplicates/undefined references and resolve identifiers
			for i in range(0, len(program.declarations)):
				for j in range(i + 1, len(program.declarations)):
					p1 = program.declarations[i]
					p2 = program.declarations[j]
					if p1.name == p2.name:
						self.throwParserError(ParserError.DUPLICATE_DECLARATION, (p2.name, p2.line, p2.col))
						return None

			for i in program.instructions:
				for arg in i.args:
					if arg.type != ArgumentType.IDENTIFIER:
						continue

					declaration = FindDeclarationUsingName(program, arg.value)

					if not declaration:
						self.throwParserError(ParserError.UNDEFINED_IDENTIFIER, arg.value)
						return None


		#print(program)
		return program

class BCodeGen:
	def __init__(self, program):
		self.program = program

	def generateBellowCode(self):
		generated_code = []

		for i in self.program.instructions:
			new_instruct = [i.keyword.value - 1]

			for arg in i.args:
				argmode = arg.mode.value - 1

				if arg.type == ArgumentType.IDENTIFIER:
					declaration = FindDeclarationUsingName(self.program, arg.value)
					new_instruct.append((argmode, declaration.value))
				elif arg.type == ArgumentType.NUMBER:
					new_instruct.append((argmode, arg.value))

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


def main():
	lexer = BLexer('fibonacci.bellow')

	parser = BParser(lexer)
	program = parser.parseProgram()

	code = None
	if program:
		codegenerator = BCodeGen(program)
		code = codegenerator.generateBellowCode()
		save_to_file(code, 'code.bec')

if __name__ == '__main__':
	main()