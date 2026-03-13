import BLex
import BParse
import BVirtualMachine

test_code = ''

with open('fibonacci.bellow', 'r') as f:
	test_code = test_code + f.read()

lexer = BLex.BellowLexer()
lexer_tokens = lexer.scan_tokens(test_code)

parser = BParse.BellowParser()
program = parser.parse_tokens(lexer_tokens)

bvm = BVirtualMachine.BVirtualMachine()
bvm.load_program(program)

def main():
	bvm.run()

if __name__ == '__main__':
	main()