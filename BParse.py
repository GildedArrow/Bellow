from enum import Enum, auto
import BLex

class BParseError(Enum):
	DUPLICATELABEL

#Goal: take lex tokens and parse them into a runnable bellow program
class BellowParser:
	def __init__(self):
		self.lex_tokens = None
		self.labels = []
		self.program = []

	def parse_tokens(self, lex_tokens):
		self.lex_tokens = lex_tokens
		self.program = []

		line = 0
		labelcount = 0
		current = 0

		while self.lex_tokens[current].tokentype != BLex.BToken.EOF:
			print(self.lex_tokens[current].tokentype)
			current += 1

		return self.program, self.labels

	def ThrowError(self):
		pass