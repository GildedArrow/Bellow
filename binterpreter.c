#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define MEMORY_LENGTH 1024
#define MAX_STACK_SIZE 16
#define MAX_ARGS 3
#define HEADER_LENGTH 5

#define MAJOR_VERSION 1
#define MINOR_VERSION 0
#define PATCH_VERSION 0

typedef struct {
    int mode;
    unsigned int value;
} BArg;

typedef struct {
    BArg args[MAX_ARGS];
    int instruction;
} BInstruction;

typedef struct {
    uint32_t callstack[MAX_STACK_SIZE];
    uint32_t pc;
	uint32_t sp;
	uint32_t *memory;
	uint32_t instruction_count;
    BInstruction *program;
} BInterpreter;

uint32_t read_uint32_bigendian(FILE *file) {
	uint8_t buffer[4];
	
	size_t c = fread(buffer, 1, 4, file);
	if (c != 4) {
		printf("[I/O] Couldn't read bytes, read: %i\n", c);
		return 0;
	}
	
	return  ((uint32_t)buffer[0] << 24) |
			((uint32_t)buffer[1] << 16) |
			((uint32_t)buffer[2] << 8)  |
			 (uint32_t)buffer[3];
}

void printInstruction(BInstruction instruction) {
	printf("%i - (%i, %i), (%i, %i), (%i, %i)\n",
	instruction.instruction,
	instruction.args[0].mode, instruction.args[0].value,
	instruction.args[1].mode, instruction.args[1].value,
	instruction.args[2].mode, instruction.args[2].value	
	);
}

BInstruction *load_from_file(BInterpreter *interpreter, const char *filename) {
    FILE *file = fopen(filename, "rb");
    BInstruction *program;

    uint32_t buffer[HEADER_LENGTH];

    if (file == NULL) {
        perror("[I/O] Failed to open file");
        return program;
    }
	
	for (int i = 0; i < HEADER_LENGTH; i++) {
		buffer[i] = read_uint32_bigendian(file);
	}
	
	if (buffer[0] != 0xbadfaced) {
		printf("[I/O] Invalid Bellow signature: %x\n", buffer[0]);
		fclose(file);
		return program;
	}
		
	if (MAJOR_VERSION < buffer[1]) {
		printf("[I/O] File \"%s\" is a newer version (%i.%i.%i) than this interpreter allows (%i.%i.%i)\n",
		filename,
		buffer[1], buffer[2], buffer[3],
		MAJOR_VERSION, MINOR_VERSION, PATCH_VERSION
		);
		fclose(file);
		return program;
	} else if (MAJOR_VERSION > buffer[1]) {
		printf("[I/O] File \"%s\" is an older version (%i.%i.%i) than this interpreter allows (%i.%i.%i)\n",
		filename,
		buffer[1], buffer[2], buffer[3],
		MAJOR_VERSION, MINOR_VERSION, PATCH_VERSION
		);
		fclose(file);
		return program;		
	}

	int instruction_count = buffer[4];
	interpreter->instruction_count = instruction_count;

	program = malloc(sizeof(BInstruction)*instruction_count);
	
	for (int i = 0; i < instruction_count; i++) {
		BInstruction instruction;
		instruction.instruction = read_uint32_bigendian(file);
		
		for (int j = 0; j < MAX_ARGS; j++) {
			BArg arg;
			arg.mode = read_uint32_bigendian(file);
			arg.value = read_uint32_bigendian(file);
			
			instruction.args[j] = arg;
		}
		
		program[i] = instruction;
	}
	
	fclose(file);
	
    return program;
}

BInterpreter createBInterpreter(const char* file) {
	BInterpreter interpreter;
	
	interpreter.pc = 0;
	interpreter.sp = -1;
	interpreter.instruction_count = 0;
	interpreter.program = load_from_file(&interpreter, file);

	interpreter.memory = malloc(sizeof(uint32_t)*MEMORY_LENGTH);
	
	memset(interpreter.memory, 0, sizeof(uint32_t)*MEMORY_LENGTH);
	memset(interpreter.callstack, 0, sizeof(uint32_t)*MAX_STACK_SIZE);
	
	return interpreter;
}

void freeBInterpreter(BInterpreter *interpreter) {
	free(interpreter->program);
	free(interpreter->memory);
}

static inline uint32_t get_number(BInterpreter *interpreter, BArg arg) {
	switch (arg.mode) {
		case 0:
			return arg.value;
		case 1:
			return interpreter->memory[arg.value];
		case 2:
			return interpreter->memory[interpreter->memory[arg.value]];
	}
}

static inline void flush_input() {
	int c;
	while ((c = getchar()) != '\n' && c != EOF);
}

static inline void op_mov(BInterpreter *i, BArg *args) {
	i->memory[get_number(i, args[1])] = get_number(i, args[0]);
}

static inline void op_add(BInterpreter *i, BArg *args) {
	i->memory[get_number(i, args[2])] = get_number(i, args[0]) + get_number(i, args[1]);
}

static inline void op_sub(BInterpreter *i, BArg *args) {
	i->memory[get_number(i, args[2])] = get_number(i, args[0]) - get_number(i, args[1]);
}

static inline void op_div(BInterpreter *i, BArg *args) {
	i->memory[get_number(i, args[2])] = get_number(i, args[0]) / get_number(i, args[1]);
}

static inline void op_mul(BInterpreter *i, BArg *args) {
	i->memory[get_number(i, args[2])] = get_number(i, args[0]) * get_number(i, args[1]);
}

static inline void op_mod(BInterpreter *i, BArg *args) {
	i->memory[get_number(i, args[2])] = get_number(i, args[0]) % get_number(i, args[1]);
}

static inline void op_shr(BInterpreter *i, BArg *args) {
	i->memory[get_number(i, args[2])] = get_number(i, args[0]) >> get_number(i, args[1]);
}

static inline void op_shl(BInterpreter *i, BArg *args) {
	i->memory[get_number(i, args[2])] = get_number(i, args[0]) << get_number(i, args[1]);
}

static inline void op_inc(BInterpreter *i, BArg *args) {
	i->memory[get_number(i, args[0])]++;
}

static inline void op_dec(BInterpreter *i, BArg *args) {
	i->memory[get_number(i, args[0])]--;
}

static inline void op_jmp(BInterpreter *i, BArg *args) {
	i->pc = get_number(i, args[0]) - 1;
}

static inline void op_jnz(BInterpreter *i, BArg *args) {
	if (get_number(i, args[1]) != 0) i->pc = get_number(i, args[0]) - 1;
}

static inline void op_jsr(BInterpreter *i, BArg *args) {
	i->callstack[++i->sp] = i->pc;
	i->pc = get_number(i, args[0]) - 1;
}

static inline void op_jz(BInterpreter *i, BArg *args) {
	if (get_number(i, args[1]) == 0) i->pc = get_number(i, args[0]) - 1;
}

static inline void op_je(BInterpreter *i, BArg *args) {
	if (get_number(i, args[1]) == get_number(i, args[2])) i->pc = get_number(i, args[0]) - 1;
}

static inline void op_jne(BInterpreter *i, BArg *args) {
	if (get_number(i, args[1]) != get_number(i, args[2])) i->pc = get_number(i, args[0]) - 1;
}

static inline void op_jle(BInterpreter *i, BArg *args) {
	if (get_number(i, args[1]) < get_number(i, args[2])) i->pc = get_number(i, args[0]) - 1;
}

static inline void op_jgr(BInterpreter *i, BArg *args) {
	if (get_number(i, args[1]) > get_number(i, args[2])) i->pc = get_number(i, args[0]) - 1;
}

static inline void op_out(BInterpreter *i, BArg *args) {
	switch (get_number(i, args[1])) {
		case 0:
			printf("%d", get_number(i, args[0]));
			break;
		default:
			printf("%c", (char)get_number(i, args[0]));
	}
}

static inline void op_input(BInterpreter *i, BArg *args) {
	scanf("%d", &i->memory[get_number(i, args[0])]);
	flush_input();
}

static inline void op_ret(BInterpreter *i, BArg *args) {
	i->pc = i->callstack[i->sp--];
}

typedef void (*bellow_op)(BInterpreter *i, BArg *args);

static const bellow_op BJumpTable[] = {
	op_mov,
	op_add,
	op_sub,
	op_div,
	op_mul,
	op_mod,
	op_shr,
	op_shl,
	op_inc,
	op_dec,
	op_jmp,
	op_jnz,
	op_jsr,
	op_jz,
	op_je,
	op_jne,
	op_jle,
	op_jgr,
	op_out,
	op_input,
	op_ret
};

void BInterpreter_Run(BInterpreter *i) {
	while (i->pc < i->instruction_count) {
		BInstruction instruct = i->program[i->pc];
		//printInstruction(instruct);
		BJumpTable[instruct.instruction](i, instruct.args);
		i->pc++;
	}
}

int main(int argc, char *argv[]) {
	
	start_time = clock();
	BInterpreter interpreter = createBInterpreter("collatz.bec");
	BInterpreter_Run(&interpreter);
	freeBInterpreter(&interpreter);
	end_time = clock();

    return 0;
}