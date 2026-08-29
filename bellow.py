import blex
import bparse
import bcodegen
import binterpreter

import sys

from bcodegen import load_program


def main():
	argc = len(sys.argv)
	argv = sys.argv

	filename = 'collatz.bellow'
	output_name = 'collatz.bec'

	lexer = blex.BLexer(filename)
	parser = bparse.BParser(lexer)

	program = parser.parse_program()
	if program:
		code_generator = bcodegen.BCodeGen(program)
		code = code_generator.generate_bellow_code()
		bcodegen.save_to_file(code, output_name)

		#interpreter = binterpreter.BInterpreter()
		#interpreter.program = load_program(output_name)

		#if interpreter.program:
		#	interpreter.run()
	else:
		print("Compilation failed.")
		return

	'''
	if argc == 2:
		output_file = argv[1]
		interpreter = binterpreter.BInterpreter()

		interpreter.program = bcodegen.load_program(output_file)

		if interpreter.program:
			interpreter.run()
	elif argc == 3:
		filename = argv[1]
		output_name = argv[2]

		lexer = blex.BLexer(filename)

		parser = bparse.BParser(lexer)
		program = parser.parse_program()

		if program:
			code_generator = bcodegen.BCodeGen(program)
			code = code_generator.generate_bellow_code()
			bcodegen.save_to_file(code, output_name)
		else:
			print("Compilation failed.")
			return
	'''
if __name__ == '__main__':
	main()