import BLex
import BParse

test_code = ''

with open('test.bellow', 'r') as f:
	test_code = test_code + f.read()

lexer = BLex.BellowLexer()
lexer_tokens = lexer.scan_tokens(test_code)

parser = BParse.BellowParser()
parser_program = parser.parse_tokens(lexer_tokens)

def main():
	pass

if __name__ == '__main__':
	main()