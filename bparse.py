from blex import *

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
	InstructionType.INPUT : (1, 1),
	InstructionType.RET   : (0, 0),
	InstructionType.VAR   : (1, 2),
	InstructionType.CONST : (2, 2),
	InstructionType.ARRAY : (2, 2),
}

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
	def __init__(self, type_, name, line, col):
		self.type = type_
		self.name = name
		self.line = line
		self.col = col
		self.value = 0

	def __repr__(self):
		return f'{self.type} "{self.name}" [{self.value}] - [{self.line}:{self.col}]\n'

class BArgument:
	def __init__(self, type_, mode, value):
		self.mode = mode
		self.type = type_
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

def find_declaration_using_name(program, name):
	for d in program.declarations:
		if d.name != name:
			continue
		return d
	return None


class BParser:
	def __init__(self, lexer: BLexer):
		self.lexer = lexer
		self.current = self.lexer.next_token()
		self.next = self.lexer.next_token()
		self.hadError = False
		self.pc = 0
		self.vp = 0

	def throw_parser_error(self, errortype, data):
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
			print(f'Too many arguments for instruction on line {self.current.line}, col {self.current.col}. Takes at most {data[1]}, but found {data[0]}')
		elif errortype == ParserError.EXPECTING_NUMBER_OR_IDENTIFIER:
			print(f'Expecting number or identifier, got \"{data}\" on line {self.current.line}, col {self.current.col}')
		elif errortype == ParserError.TOO_FEW_ARGUMENTS:
			print(f'Too few arguments for instruction on line {self.current.line}, col {self.current.col}. Takes at least {data[1]}, but found {data[0]}')
		elif errortype == ParserError.DUPLICATE_DECLARATION:
			print(f'Duplicate identifier declaration \"{data[0]}\" on line {data[1]}, col {data[2]}')
		elif errortype == ParserError.EXPECTING_IDENTIFIER:
			print(f'Expecting identifier, but found \"{data}\" instead on line {self.current.line}, col {self.current.col}')
		elif errortype == ParserError.UNDEFINED_IDENTIFIER:
			print(f'Undefined identifier \"{data}\" on line {self.current.line}, col {self.current.col}')

	def advance(self):
		self.current = self.next
		self.next = self.lexer.next_token()

	def is_eof(self):
		return self.current.type == TokenType.EOF

	def is_end_of_statement(self):
		return self.current.type == TokenType.NEWLINE or self.is_eof()

	def expect_newline_or_eof(self):
		self.advance()
		if not self.is_end_of_statement():
			self.throw_parser_error(ParserError.EXPECTING_END_OF_LINE, self.current.value)
			return

	def parse_label(self, program):
		self.expect_identifier()

		new_label = Declaration(DeclarationType.LABEL, self.current.value, self.current.line, self.current.col)
		new_label.value = self.pc #where it exists in the program

		self.expect_newline_or_eof()

		program.declarations.append(new_label)

	def parse_variable(self, program):
		self.expect_identifier()

		identifier = self.current.value

		new_var = Declaration(DeclarationType.VARIABLE, identifier, self.current.line, self.current.col)
		new_var.value = self.vp

		self.expect_newline_or_eof()
		self.vp += 1

		program.declarations.append(new_var)

	def expect_identifier(self):
		self.advance()
		if self.current.type != TokenType.IDENTIFIER:
			self.throw_parser_error(ParserError.EXPECTING_IDENTIFIER, self.current.value)
			return

	def parse_constant(self, program):
		self.expect_identifier()

		identifier = self.current.value

		self.advance()

		if self.current.type != TokenType.NUMBER:
			self.throw_parser_error(ParserError.CONST_EXPECTING_NUMBER, self.next.value)
			return

		new_const = Declaration(DeclarationType.CONST, identifier, self.current.line, self.current.col)
		new_const.value = self.current.value

		self.expect_newline_or_eof()

		program.declarations.append(new_const)

	def parse_array(self, program):
		self.expect_identifier()

		identifier = self.current.value

		self.advance()

		if self.current.type != TokenType.NUMBER:
			self.throw_parser_error(ParserError.ARRAY_EXPECTING_NUMBER, self.current.value)
			return

		new_array = Declaration(DeclarationType.ARRAY, identifier, self.current.line, self.current.col)
		new_array.value = self.vp

		self.vp += self.current.value
		self.expect_newline_or_eof()

		program.declarations.append(new_array)

	def expect_comma(self):
		self.advance()
		if self.current.type != TokenType.COMMA:
			self.throw_parser_error(ParserError.EXPECTING_COMMA, self.current.type)

	def expect_number(self):
		self.advance()
		if self.current.type != TokenType.NUMBER and self.current.type != TokenType.IDENTIFIER:
			self.throw_parser_error(ParserError.EXPECTING_NUMBER_OR_IDENTIFIER, self.current.type)

	def parse_argument(self, args, mode = ArgumentMode.IMMEDIATE, value = None, argtype = ArgumentType.NUMBER):
		if self.current.type == TokenType.NUMBER:
			argtype = ArgumentType.NUMBER
			value = self.current.value
			args.append(BArgument(argtype, mode, value))
		elif self.current.type == TokenType.IDENTIFIER:
			argtype = ArgumentType.IDENTIFIER
			value = self.current.value
			args.append(BArgument(argtype, mode, value))
		elif self.current.type == TokenType.HASHTAG:
			self.expect_number()
			self.parse_argument(args, ArgumentMode.VALUE, value, argtype)
			return
		elif self.current.type == TokenType.AMPERSAND:
			self.expect_number()
			self.parse_argument(args, ArgumentMode.POINTER, value, argtype)
			return
		else:
			self.throw_parser_error(ParserError.EXPECTING_ARGUMENT, self.current.type)

		self.advance()

	def parse_keyword(self, program):
		num_args = ARGS_COUNTS[self.current.value]
		new_instruct = BInstruction(self.current.value)

		args = []

		self.advance()

		if not self.is_end_of_statement():
			self.parse_argument(args)

			while not self.is_end_of_statement():
				if self.current.type != TokenType.COMMA:
					self.throw_parser_error(ParserError.EXPECTING_COMMA, self.current.value)
					return

				self.advance()
				self.parse_argument(args)

				if self.hadError:
					return

			new_instruct.args = args

		if len(args) > num_args[1]:
			self.throw_parser_error(ParserError.TOO_MANY_ARGUMENTS, (len(args), num_args[1]))
			return
		if len(args) < num_args[0]:
			self.throw_parser_error(ParserError.TOO_FEW_ARGUMENTS, (len(args), num_args[0]))
			return

		self.pc += 1
		program.instructions.append(new_instruct)

	def parse_program(self):
		program = BProgram()
		#First pass, collect all declarations and instructions
		while not self.is_eof() and not self.hadError:
			if self.current.type == TokenType.NEWLINE:
				self.advance()
				continue
			elif self.current.type == TokenType.PERIOD:
				self.parse_label(program)
			elif self.current.type == TokenType.KEYWORD:
				if self.current.value == InstructionType.VAR:
					self.parse_variable(program)
				elif self.current.value == InstructionType.CONST:
					self.parse_constant(program)
				elif self.current.value == InstructionType.ARRAY:
					self.parse_array(program)
				else:
					self.parse_keyword(program)
			else:
				self.throw_parser_error(ParserError.EXPECTING_STATEMENT, self.current.type)
			self.advance()

			if self.hadError:
				return None

		#Second pass, check for duplicates/undefined references and resolve identifiers
		for i in range(0, len(program.declarations)):
			for j in range(i + 1, len(program.declarations)):
				p1 = program.declarations[i]
				p2 = program.declarations[j]
				if p1.name == p2.name:
					self.throw_parser_error(ParserError.DUPLICATE_DECLARATION, (p2.name, p2.line, p2.col))
					return None

		for i in program.instructions:
			for arg in i.args:
				if arg.type != ArgumentType.IDENTIFIER:
					continue

				declaration = find_declaration_using_name(program, arg.value)

				if not declaration:
					self.throw_parser_error(ParserError.UNDEFINED_IDENTIFIER, arg.value)
					return None

		return program